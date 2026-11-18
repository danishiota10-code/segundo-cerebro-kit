#!/usr/bin/env python3
"""
Atualiza um vault com a versão nova do segundo-cerebro-kit sem tocar no que
o usuário escreveu.

Como decide, arquivo por arquivo (só dentro de GERENCIADOS, abaixo):
- não existe no vault            -> NOVO: copia.
- igual à versão nova do kit     -> em dia: nada.
- igual a alguma versão antiga   -> ATUALIZA: o usuário nunca mexeu, troca.
  do kit (histórico do git)
- diferente de toda versão       -> MEXIDO: o usuário editou. Não toca, lista
  do kit                            pra IA mostrar a diferença e perguntar.

Nunca apaga nada. Notas (00 Inbox ... 05 Archives, knowledge, Home, .obsidian),
`AIOS/index.md` e `AIOS/project-map.md` (o /setup personaliza os dois) ficam
fora da lista e nunca são lidos nem escritos.

Antes de trocar qualquer arquivo, guarda a versão do vault numa pasta irmã:
  <pasta do vault>-backup-kit-AAAA-MM-DD-HHMM/

Uso (de dentro do vault):
  python3 AIOS/scripts/atualizar-kit.py            # só mostra o plano
  python3 AIOS/scripts/atualizar-kit.py --aplicar  # aplica

Primeira vez (o vault ainda não tem este script): clone o kit numa pasta
temporária e rode o script de lá, apontando pro vault:
  python3 <kit>/AIOS/scripts/atualizar-kit.py --vault <vault> --kit <kit>
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

KIT_URL = "https://github.com/danishiota10-code/segundo-cerebro-kit"

# Pastas e arquivos do sistema que o kit mantém. Prefixo terminado em "/" = pasta.
GERENCIADOS = [
    "CLAUDE.md",
    "AGENTS.md",
    ".claude/commands/",
    ".claude/hooks/",
    ".claude/agents/",
    ".claude/settings.json",
    ".claude/settings-windows.json",
    ".codex/",
    ".agents/skills/",
    "AIOS/scripts/",
    "AIOS/operating-rules.md",
    "AIOS/knowledge-routing.md",
    "AIOS/Vault-Map.md",
    "prompts/",
]


def gerenciado(rel):
    return any(rel == g or (g.endswith("/") and rel.startswith(g)) for g in GERENCIADOS)


def git(kit, *args):
    return subprocess.run(
        ["git", "-C", str(kit), *args], capture_output=True, check=True
    ).stdout


def norm(data):
    # Windows com autocrlf grava CRLF; não é edição do usuário.
    return data.replace(b"\r\n", b"\n")


def versoes_antigas(kit, rel):
    out = set()
    try:
        commits = git(kit, "log", "--format=%H", "--", rel).decode().split()
    except subprocess.CalledProcessError:
        return out
    for h in commits:
        try:
            out.add(norm(git(kit, "show", f"{h}:{rel}")))
        except subprocess.CalledProcessError:
            pass  # commit que apagou o arquivo
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--vault", default=".", help="pasta do vault (padrão: a atual)")
    ap.add_argument("--kit", help="clone completo do kit (padrão: clona agora)")
    ap.add_argument("--aplicar", action="store_true", help="aplica; sem isso só mostra")
    a = ap.parse_args()

    vault = Path(a.vault).resolve()
    if not (vault / "02 Context").is_dir() or not (vault / "01 Daily").is_dir():
        print(f"Isto não parece um vault do kit: {vault}")
        return 2

    tmp = None
    if a.kit:
        kit = Path(a.kit).resolve()
    else:
        tmp = tempfile.mkdtemp(prefix="segundo-cerebro-kit-")
        kit = Path(tmp) / "kit"
        # Clone completo (sem --depth): o histórico é o que prova que um
        # arquivo do vault é só uma versão antiga do kit.
        subprocess.run(["git", "clone", "-q", KIT_URL, str(kit)], check=True)
    if kit == vault:
        print("--kit e --vault são a mesma pasta.")
        return 2

    arquivos = [
        f for f in git(kit, "ls-files", "-z").decode().split("\0") if f and gerenciado(f)
    ]

    novos, atualiza, mexidos = [], [], []
    for rel in arquivos:
        src, dst = kit / rel, vault / rel
        novo = norm(src.read_bytes())
        if not dst.exists():
            novos.append(rel)
            continue
        atual = norm(dst.read_bytes())
        if atual == novo:
            continue
        if atual in versoes_antigas(kit, rel):
            atualiza.append(rel)
        else:
            mexidos.append(rel)

    commit = git(kit, "log", "-1", "--format=%h %cs %s").decode().strip()
    print(f"Kit: {commit}")
    print(f"Vault: {vault}\n")
    for titulo, lista in (
        ("NOVOS (vão ser copiados)", novos),
        ("ATUALIZADOS (você nunca mexeu, vão ser trocados)", atualiza),
        ("MEXIDOS POR VOCÊ (não vou tocar, compare antes)", mexidos),
    ):
        print(f"{titulo}: {len(lista)}")
        for rel in lista:
            print(f"  {rel}")
    if mexidos:
        print(f"\nPra comparar um mexido: diff \"{vault}/<arquivo>\" \"{kit}/<arquivo>\"")

    if not a.aplicar:
        print("\nNada foi mudado. Rode de novo com --aplicar pra aplicar.")
        return 0
    if not novos and not atualiza:
        print("\nO vault já está em dia.")
        return 0

    backup = None
    if atualiza:
        stamp = datetime.now().strftime("%Y-%m-%d-%H%M")
        backup = vault.parent / f"{vault.name}-backup-kit-{stamp}"
        for rel in atualiza:
            (backup / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(vault / rel, backup / rel)
    for rel in novos + atualiza:
        (vault / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(kit / rel, vault / rel)

    print(f"\nAplicado: {len(novos)} novos, {len(atualiza)} atualizados.")
    if backup:
        print(f"Cópia dos arquivos trocados: {backup}")
    if any(r.startswith(".codex/") for r in novos + atualiza):
        print("Codex: na próxima sessão, rode /hooks e aprove os hooks do vault.")
    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
