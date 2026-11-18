#!/usr/bin/env python3
"""
AI OS Hook Self Test

Roda os hooks de verdade e confere o que eles devolvem. Nao le o codigo pra
adivinhar, executa e mede.

Como rodar:
    python3 .claude/hooks/test-hooks.py      (Mac e Linux)
    python .claude/hooks/test-hooks.py       (Windows)

Sai com codigo 0 se tudo passou, 1 se qualquer caso falhou. Esse codigo de
saida e a prova: "passou" impresso na tela nao vale nada se o exit for 1.

O CASO 3 E O MOTIVO DESTE ARQUIVO EXISTIR
-----------------------------------------
So quatro caminhos falam com a IA:
  - SessionStart, UserPromptSubmit, UserPromptExpansion: o stdout do hook
    entra no contexto do modelo.
  - Stop: nao e stdout. Devolve {"decision": "block", "reason": "..."} e o
    reason vira instrucao.
Em qualquer outro evento o print() vai pro transcript e ninguem le. O hook
roda, sai com codigo 0, parece saudavel, e nao faz nada. Este kit ja cometeu
esse erro duas vezes (session-start.py em PreToolUse, session-capture.py em
PreCompact). O caso 3 executa cada hook configurado e reprova qualquer um que
escreva em stdout num evento que nao entrega stdout pra ninguem.

Saida sem acento de proposito: no Windows o console usa cp1252 e caractere
acentuado cru quebra a escrita.
"""
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parent
VAULT = HOOKS_DIR.parent.parent
SETTINGS = HOOKS_DIR.parent / "settings.json"
SETTINGS_WIN = HOOKS_DIR.parent / "settings-windows.json"

# Eventos cujo stdout o modelo realmente le.
STDOUT_CHANNELS = {"SessionStart", "UserPromptSubmit", "UserPromptExpansion"}
# Stop fala pela chave decision, nao por stdout solto.
DECISION_CHANNEL = "Stop"
ALLOWED_EVENTS = STDOUT_CHANNELS | {DECISION_CHANNEL, "SessionEnd"}

results = []


def check(name, passed, evidence):
    results.append((name, passed, evidence))
    print(("PASS  " if passed else "FAIL  ") + name)
    print("      " + evidence)


def run_hook(script, payload, env_extra=None):
    """Roda um hook e devolve (exit_code, stdout, stderr)."""
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    proc = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    return proc.returncode, proc.stdout, proc.stderr


def load_events(path):
    """Devolve [(evento, caminho_do_script)] a partir de um settings.json."""
    out = []
    data = json.loads(path.read_text(encoding="utf-8"))
    for event, groups in data.get("hooks", {}).items():
        for group in groups:
            for hook in group.get("hooks", []):
                cmd = hook.get("command", "")
                for candidate in HOOKS_DIR.glob("*.py"):
                    if candidate.name in cmd:
                        out.append((event, candidate))
    return out


class DailyNote:
    """Salva e devolve o estado da nota de hoje, pro teste nao sujar o vault."""

    def __init__(self):
        self.path = VAULT / "01 Daily" / f"{date.today().isoformat()}.md"
        self.existed = self.path.exists()
        self.backup = None
        self.mtime = None
        if self.existed:
            self.backup = self.path.read_bytes()
            self.mtime = self.path.stat().st_mtime

    def write_with_age(self, minutes_old):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("teste\n", encoding="utf-8")
        stamp = time.time() - minutes_old * 60
        os.utime(self.path, (stamp, stamp))

    def remove(self):
        if self.path.exists():
            self.path.unlink()

    def restore(self):
        if self.existed:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_bytes(self.backup)
            os.utime(self.path, (self.mtime, self.mtime))
        else:
            self.remove()


def main():
    print("AI OS Hook Self Test")
    print("vault: " + str(VAULT))
    print("")

    # ---- 1. settings valido, eventos conhecidos, scripts existem ----------
    for path in (SETTINGS, SETTINGS_WIN):
        if not path.exists():
            check("settings existe: " + path.name, False, "arquivo nao encontrado")
            continue
        try:
            events = load_events(path)
        except json.JSONDecodeError as exc:
            check("settings e JSON valido: " + path.name, False, str(exc))
            continue
        check(
            "settings e JSON valido: " + path.name,
            True,
            str(len(events)) + " hook(s): " + ", ".join(e for e, _ in events),
        )
        desconhecidos = [e for e, _ in events if e not in ALLOWED_EVENTS]
        check(
            "eventos conhecidos: " + path.name,
            not desconhecidos,
            "todos previstos" if not desconhecidos else "evento inesperado: " + str(desconhecidos),
        )

    events = load_events(SETTINGS)

    # ---- 2. todo hook configurado compila --------------------------------
    for event, script in events:
        proc = subprocess.run(
            [sys.executable, "-m", "py_compile", str(script)],
            capture_output=True,
            text=True,
        )
        check(
            "compila: " + script.name,
            proc.returncode == 0,
            "py_compile exit=" + str(proc.returncode)
            + (" " + proc.stderr.strip()[:120] if proc.returncode else ""),
        )

    # ---- 3. o canal existe de verdade (o caso que pega o hook morto) -----
    note = DailyNote()
    try:
        for event, script in events:
            # Zera ANTES DE CADA hook, nao uma vez pro loop inteiro. O
            # session-start.py recria a nota de hoje quando roda, entao um
            # reset unico deixaria o session-capture ver um daily fresco,
            # ficar calado, e PASSAR por nao ter nada a dizer. Isso e um PASS
            # falso: o caso nunca chega a testar o canal.
            note.remove()
            code, out, _ = run_hook(script, {})
            falou = bool(out.strip())

            if not falou:
                check(
                    "canal ok: " + script.name + " em " + event,
                    True,
                    "nao escreve em stdout, entrega por arquivo ou nao tem o que dizer",
                )
            elif event in STDOUT_CHANNELS:
                check(
                    "canal ok: " + script.name + " em " + event,
                    True,
                    str(len(out)) + " chars em stdout, e " + event + " injeta stdout no contexto",
                )
            elif event == DECISION_CHANNEL:
                try:
                    payload = json.loads(out)
                    ok = payload.get("decision") == "block" and bool(payload.get("reason"))
                    detalhe = "decision=" + str(payload.get("decision")) + ", reason=" + str(len(payload.get("reason", ""))) + " chars"
                except json.JSONDecodeError as exc:
                    ok, detalhe = False, "stdout nao e JSON de decision: " + str(exc)
                check("canal ok: " + script.name + " em " + event, ok, detalhe)
            else:
                check(
                    "canal ok: " + script.name + " em " + event,
                    False,
                    "HOOK MORTO: escreve " + str(len(out)) + " chars em stdout, mas "
                    + event + " nao entrega stdout pra IA. Roda, sai com 0, e ninguem le.",
                )
    finally:
        note.restore()

    # ---- 4. session-start cabe no limite de contexto ---------------------
    start = HOOKS_DIR / "session-start.py"
    if start.exists():
        note = DailyNote()
        try:
            code, out, err = run_hook(start, {})
            check(
                "session-start injeta contexto",
                code == 0 and 0 < len(out) < 10000,
                "exit=" + str(code) + ", " + str(len(out)) + " chars (limite do Claude Code = 10000)",
            )
        finally:
            note.restore()

    # ---- 5. guards do session-capture ------------------------------------
    capture = HOOKS_DIR / "session-capture.py"
    if capture.exists():
        note = DailyNote()
        try:
            code, out, _ = run_hook(capture, {"stop_hook_active": True})
            check(
                "guard 1: stop_hook_active corta o loop",
                code == 0 and not out.strip(),
                "exit=" + str(code) + ", stdout=" + str(len(out)) + " chars (esperado 0)",
            )

            note.write_with_age(0)
            code, out, _ = run_hook(capture, {})
            check(
                "guard 2: daily fresco, hook fica calado",
                code == 0 and not out.strip(),
                "exit=" + str(code) + ", stdout=" + str(len(out)) + " chars (esperado 0)",
            )

            note.write_with_age(60)
            code, out, _ = run_hook(capture, {})
            try:
                payload = json.loads(out)
                ok = payload.get("decision") == "block"
                detalhe = "daily com 60 min, decision=" + str(payload.get("decision"))
            except json.JSONDecodeError:
                ok, detalhe = False, "daily velho mas stdout nao e JSON: " + repr(out[:80])
            check("guard 2 ao contrario: daily velho, hook cobra", ok and code == 0, detalhe)

            code, out, _ = run_hook(capture, {}, {"AIOS_DOCUMENTING": "1"})
            check(
                "guard 3: AIOS_DOCUMENTING corta a recursao",
                code == 0 and not out.strip(),
                "exit=" + str(code) + ", stdout=" + str(len(out)) + " chars (esperado 0)",
            )

            proc = subprocess.run(
                [sys.executable, str(capture)],
                input="isso nao e json",
                capture_output=True,
                text=True,
                timeout=30,
            )
            check(
                "stdin invalido nao derruba a sessao",
                proc.returncode == 0 and not proc.stdout.strip(),
                "exit=" + str(proc.returncode) + ", stdout=" + str(len(proc.stdout)) + " chars",
            )

            note.write_with_age(60)
            _, out, _ = run_hook(capture, {})
            nao_ascii = [c for c in out if ord(c) > 127]
            check(
                "saida ASCII, aguenta cp1252 no Windows",
                not nao_ascii,
                "sem acento na saida" if not nao_ascii else "caracteres que quebram: " + str(nao_ascii[:10]),
            )
        finally:
            note.restore()

    # ---- daily cortado pelo fim e saida do Codex --------------------------
    # Roda o session-start num vault de mentira: daily longo, com a sessao mais
    # nova no fim. O hook tem que guardar o fim (era o comeco, e a ultima
    # conversa do dia sumia).
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="aios-test-"))
    try:
        (tmp / ".claude" / "hooks").mkdir(parents=True)
        shutil.copy2(HOOKS_DIR / "session-start.py", tmp / ".claude" / "hooks" / "session-start.py")
        (tmp / "02 Context").mkdir()
        (tmp / "02 Context" / "me.md").write_text("Nome: Teste\n", encoding="utf-8")
        (tmp / "01 Daily").mkdir()
        longo = "SESSAO-VELHA\n" + ("x" * 5000) + "\nSESSAO-NOVA\n"
        (tmp / "01 Daily" / "2000-01-01.md").write_text(longo, encoding="utf-8")
        start = tmp / ".claude" / "hooks" / "session-start.py"

        _, out, _ = run_hook(start, {"source": "startup"})
        check(
            "daily longo: chega a sessao mais nova",
            "SESSAO-NOVA" in out and "SESSAO-VELHA" not in out,
            "fim presente" if "SESSAO-NOVA" in out else "o fim do daily foi cortado",
        )

        proc = subprocess.run(
            [sys.executable, str(start), "--codex"],
            input=json.dumps({"source": "startup"}),
            capture_output=True, text=True, timeout=30,
        )
        try:
            env = json.loads(proc.stdout)
            ctx = env["hookSpecificOutput"]["additionalContext"]
            ok = env["hookSpecificOutput"]["hookEventName"] == "SessionStart" and "Nome: Teste" in ctx
            detalhe = "envelope JSON com o me.md dentro"
        except Exception as exc:
            ok, detalhe = False, "saida nao e o envelope do Codex: " + str(exc)
        check("codex: session-start --codex devolve JSON", ok and proc.returncode == 0, detalhe)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ---- Codex: hooks.json aponta pros scripts certos ----------------------
    codex_hooks = VAULT / ".codex" / "hooks.json"
    try:
        data = json.loads(codex_hooks.read_text(encoding="utf-8"))
        cmds = {
            ev: " ".join(h.get("command", "") for g in groups for h in g.get("hooks", []))
            for ev, groups in data.get("hooks", {}).items()
        }
        ok = (
            "session-start.py" in cmds.get("SessionStart", "")
            and "--codex" in cmds.get("SessionStart", "")
            and "session-capture.py" in cmds.get("Stop", "")
            and set(cmds) <= {"SessionStart", "Stop"}
        )
        check("codex: hooks.json com SessionStart --codex e Stop", ok, str(sorted(cmds)))
    except Exception as exc:
        check("codex: hooks.json valido", False, str(exc))

    # ---- Codex: skills em sincronia com os comandos -----------------------
    gerar = VAULT / "AIOS" / "scripts" / "gerar-skills-codex.py"
    if gerar.exists():
        proc = subprocess.run(
            [sys.executable, str(gerar), "--check"], capture_output=True, text=True, timeout=30
        )
        check(
            "codex: .agents/skills igual a .claude/commands",
            proc.returncode == 0,
            proc.stdout.strip().splitlines()[0] if proc.stdout.strip() else "sem saida",
        )

    # ---- placar -----------------------------------------------------------
    print("")
    passou = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    print("=" * 60)
    print("RESULTADO: " + str(passou) + "/" + str(total) + " casos passaram")
    if passou != total:
        print("")
        print("Falhou:")
        for name, ok, evidence in results:
            if not ok:
                print("  - " + name + ": " + evidence)
    print("=" * 60)
    return 0 if passou == total else 1


if __name__ == "__main__":
    if shutil.which(sys.executable) is None and not Path(sys.executable).exists():
        print("python nao encontrado")
        sys.exit(1)
    sys.exit(main())
