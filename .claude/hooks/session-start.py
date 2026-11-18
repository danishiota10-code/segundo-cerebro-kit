#!/usr/bin/env python3
"""
AI OS Session Start Hook

Injeta o contexto central do vault no inicio de cada sessao do Claude Code
e do Codex. O mesmo arquivo serve os dois: com `--codex` a saida vai no
envelope JSON do SessionStart do Codex (hookSpecificOutput.additionalContext),
sem ele vai em texto puro, que e o que o Claude Code adiciona ao contexto.

IMPORTANTE: dispara no evento SessionStart. O stdout do SessionStart E injetado
no contexto do modelo. O evento antigo (PreToolUse) NAO injeta stdout no contexto,
por isso o agente parecia "nao conectado" mesmo com o hook rodando.

Regras de robustez:
- Output sempre abaixo de 10.000 caracteres (limite por hook). Teto de 9.000 aqui.
- Sem dependencia de /tmp (nao existe em Windows nativo). SessionStart roda uma
  vez por sessao, entao nao precisa de lock.
- Leitura sempre em utf-8. Toda operacao de arquivo tolera falha sem quebrar.
- O vault e detectado pela localizacao deste arquivo, sem paths absolutos.

Mesmo que este hook falhe (sem python, por exemplo), o agente ainda conecta:
o CLAUDE.md (sempre carregado pelo Claude Code) instrui a IA a ler estes arquivos.
"""
import json
import os
import sys
from datetime import date
from pathlib import Path

# Guard anti-recursao: a documentacao automatica de fim de sessao chama
# 'claude -p' headless, que dispara SessionStart de novo. Nessa rodada, sai.
if os.environ.get("AIOS_DOCUMENTING") == "1":
    sys.exit(0)

# Consome o stdin do hook (JSON do SessionStart) sem depender dele.
try:
    sys.stdin.read()
except Exception:
    pass

# Vault root = pai de .claude/hooks/
VAULT = Path(__file__).resolve().parent.parent.parent

CHAR_BUDGET = 9000  # margem de seguranca sob o limite de 10k por hook


def read_capped(rel_path, limit, keep="start"):
    """Le o arquivo e corta em `limit` caracteres.

    keep="start" guarda o comeco (identidade: o mais importante vem primeiro).
    keep="end" guarda o fim (daily: as sessoes novas sao acrescentadas no fim,
    e cortar o fim fazia a IA perder justamente a ultima conversa do dia).
    """
    p = VAULT / rel_path
    if not p.exists():
        return None
    try:
        text = p.read_text(encoding="utf-8")
    except Exception:
        return None
    if len(text) > limit:
        if keep == "end":
            text = "[... inicio cortado, leia o arquivo inteiro se precisar ...]\n" + text[-limit:]
        else:
            text = text[:limit] + "\n[... truncado, leia o arquivo inteiro se precisar ...]"
    return text


def detect_mode():
    op = VAULT / "02 Context" / "operator.md"
    org = VAULT / "02 Context" / "organization.md"
    return "empresa" if (op.exists() and org.exists()) else "solo"


def latest_daily():
    d = VAULT / "01 Daily"
    if not d.exists():
        return None
    files = sorted(d.glob("????-??-??.md"), reverse=True)
    return files[0] if files else None


def ensure_today_daily():
    today = date.today().isoformat()
    d = VAULT / "01 Daily"
    try:
        d.mkdir(parents=True, exist_ok=True)
        f = d / f"{today}.md"
        if not f.exists():
            f.write_text(
                f"---\ntype: daily\ndate: {today}\nstatus: active\ntags: [daily]\n---\n",
                encoding="utf-8",
            )
    except Exception:
        pass
    return today


header = "[AI OS Session Start] Voce e a IA pessoal que opera este vault. Contexto carregado abaixo.\n"
parts = [header]
used = len(header)


def add(block):
    global used
    if used + len(block) < CHAR_BUDGET:
        parts.append(block)
        used += len(block)


# 1. Identidade (prioridade maxima, e o que faz o agente "te conhecer")
if detect_mode() == "empresa":
    identity = [
        ("02 Context/operator.md", "Operador", 2500),
        ("02 Context/organization.md", "Empresa", 2500),
    ]
else:
    identity = [("02 Context/me.md", "Identidade", 4000)]

for rel, label, lim in identity:
    txt = read_capped(rel, lim)
    if txt:
        add(f"--- {label} ({rel}) ---\n{txt}\n")

# 2. Ultima sessao (continuidade)
ld = latest_daily()
if ld:
    txt = read_capped(ld.relative_to(VAULT).as_posix(), 2000, keep="end")
    if txt:
        add(f"--- Ultima Sessao ({ld.stem}) ---\n{txt}\n")

# 3. Ponteiros pro resto (lidos sob demanda pela IA)
add(
    "--- Leia sob demanda ---\n"
    "- AIOS/index.md (skills e comandos disponiveis)\n"
    "- AIOS/operating-rules.md (como operar neste vault)\n"
    "- AIOS/knowledge-routing.md (onde salvar cada coisa)\n"
    "- knowledge/index.md (conhecimento permanente)\n"
)

# 4. Garante o daily de hoje + instrucao de documentacao
today = ensure_today_daily()
add(
    f"--- Documentacao ---\n"
    f"A nota de hoje existe em `01 Daily/{today}.md`. Registre decisoes reais nela "
    f"ou em `03 Intelligence/decisions/` conforme trabalha.\n"
)

context = "\n".join(parts)
if "--codex" in sys.argv[1:]:
    # O Codex le texto puro como contexto tambem, mas um texto que comeca com
    # "[AI OS ..." parece um array JSON pro parser dele. O envelope explicito
    # evita a ambiguidade.
    json.dump(
        {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}},
        sys.stdout,
        ensure_ascii=True,
    )
    sys.stdout.write("\n")
else:
    sys.stdout.write(context)
