#!/usr/bin/env python3
"""
Gera as skills do Codex a partir dos comandos do Claude Code.

A fonte de verdade e `.claude/commands/*.md`. O Codex nao le essa pasta: ele
procura skills em `.agents/skills/<nome>/SKILL.md`, com `name` e `description`
no frontmatter. Este script copia cada comando pra la, no formato do Codex.

Mudou um comando? Rode de novo:  python3 AIOS/scripts/gerar-skills-codex.py
O `.claude/hooks/test-hooks.py` falha se as duas pastas sairem de sincronia.

Sem symlink de proposito: symlink quebra no Windows.
"""
import sys
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent.parent
COMMANDS = VAULT / ".claude" / "commands"
SKILLS = VAULT / ".agents" / "skills"

AVISO = (
    "<!-- Gerado de .claude/commands/{nome}.md por AIOS/scripts/gerar-skills-codex.py. "
    "Edite o comando, não este arquivo. -->\n\n"
    "> No Codex: onde este texto disser `/{nome}` ou outro comando com barra, "
    "entenda a skill `${nome}`. Onde disser \"AskUserQuestion\", faça a pergunta "
    "na conversa com as opções numeradas, uma por vez.\n\n"
)


def split_frontmatter(text):
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    meta = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, text[end + 5:]


def render(cmd_path):
    nome = cmd_path.stem
    meta, body = split_frontmatter(cmd_path.read_text(encoding="utf-8"))
    desc = meta.get("description", nome).replace('"', "'")
    return (
        f"---\nname: {nome}\ndescription: \"{desc}\"\n---\n\n"
        + AVISO.format(nome=nome)
        + body.lstrip("\n")
    )


def expected():
    return {p.stem: render(p) for p in sorted(COMMANDS.glob("*.md"))}


def main():
    check = "--check" in sys.argv[1:]
    want = expected()
    stale = []
    for nome, text in want.items():
        f = SKILLS / nome / "SKILL.md"
        cur = f.read_text(encoding="utf-8") if f.exists() else None
        if cur != text:
            stale.append(nome)
            if not check:
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(text, encoding="utf-8")
    if check:
        if stale:
            print("Skills do Codex desatualizadas: " + ", ".join(stale))
            print("Rode: python3 AIOS/scripts/gerar-skills-codex.py")
            return 1
        print(f"OK: {len(want)} skills do Codex em sincronia com .claude/commands")
        return 0
    print(f"{len(want)} skills geradas em .agents/skills ({len(stale)} mudaram)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
