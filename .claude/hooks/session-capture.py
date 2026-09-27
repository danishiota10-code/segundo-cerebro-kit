#!/usr/bin/env python3
"""
AI OS Session Capture Hook

Dispara em Stop. Pede pra IA persistir a sessao no daily antes do turno acabar.

POR QUE Stop E NAO PreCompact
-----------------------------
Este hook rodava em PreCompact, escrevendo o lembrete com print() e saindo com
codigo 0. Pela spec de hooks do Claude Code, so UserPromptSubmit,
UserPromptExpansion e SessionStart colocam o stdout do hook no contexto do
modelo. Todo o resto, PreCompact incluso, manda o stdout pro transcript e
ninguem le. Ou seja: o lembrete era escrito e lido zero vezes. E o mesmo
defeito que fazia o session-start.py nao fazer nada quando estava em PreToolUse.

Stop e o unico evento de ciclo de vida com um canal documentado de volta pra
conversa: devolver {"decision": "block", "reason": "..."} impede a parada e
entrega o `reason` pra IA como instrucao do que fazer agora. O mecanismo e
esse, nao o stdout.

DOIS GUARDS, E POR QUE O PRIMEIRO NAO BASTA
-------------------------------------------
1. stop_hook_active. Bloquear o Stop faz a IA trabalhar e tentar parar de novo.
   Sem esse guard vira loop infinito. O payload traz stop_hook_active: true da
   segunda tentativa em diante DENTRO DO MESMO TURNO, entao o guard sai com 0 e
   deixa aquele turno terminar.

   Atencao: a flag reseta a cada turno. O guard 1 evita loop, nao repeticao.

2. Frescor do daily. Disparar em todo turno e barulho, inclusive nos turnos que
   acabaram de escrever o daily. Entao se a nota de hoje foi modificada nos
   ultimos FRESH_MINUTES, a sessao ja esta sendo persistida e o hook sai calado.
   O lembrete so aparece quando a persistencia realmente ficou velha.

Guard anti-recursao: a documentacao automatica do session-end.py chama
'claude -p' headless, que dispara os hooks de novo. AIOS_DOCUMENTING=1 faz
sair cedo.

Saida sem acento de proposito: no Windows o console usa cp1252 e caractere
acentuado cru quebra a escrita.
"""
import json
import os
import sys
import time
from datetime import date
from pathlib import Path

# Vault root = pai de .claude/hooks/ (sem path absoluto, funciona em qualquer maquina)
VAULT = Path(__file__).resolve().parent.parent.parent

FRESH_MINUTES = 20


def main() -> int:
    # Nunca roda dentro da propria rodada de documentacao headless.
    if os.environ.get("AIOS_DOCUMENTING") == "1":
        return 0

    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        # Sem payload legivel nao da pra checar o guard. Ficar calado e melhor
        # do que arriscar um loop.
        return 0

    if payload.get("stop_hook_active"):
        return 0

    today = date.today().isoformat()

    note = VAULT / "01 Daily" / f"{today}.md"
    try:
        if (time.time() - note.stat().st_mtime) < FRESH_MINUTES * 60:
            return 0
    except OSError:
        # Nota ainda nao existe ou nao da pra ler. E exatamente quando o
        # lembrete vale, entao segue.
        pass

    reason = (
        f"[AI OS Session Capture] Antes de encerrar: persista esta sessao em "
        f"01 Daily/{today}.md.\n\n"
        "Adicione uma entrada `## Sessao` com:\n"
        "- **Decisoes tomadas:** decisoes reais desta sessao\n"
        "- **O que foi feito:** acoes concretas realizadas\n"
        "- **Aprendizados:** o que funcionou, o que falhou, o que foi descoberto\n"
        "- **Proximos passos:** acoes pendentes, especificas e com data\n\n"
        "Depois roteie o resto pro lugar certo: decisao importante vai pra "
        "03 Intelligence/decisions/, estado novo de projeto vai pra nota do "
        "projeto, correcao que o usuario te deu vira regra permanente no "
        "02 Context/me.md. Em duvida, consulte AIOS/knowledge-routing.md.\n\n"
        "Se a sessao foi so conversa e nao tem nada que valha guardar, diga "
        "isso em uma linha e pare. Nao invente entrada pra satisfazer o hook."
    )

    json.dump({"decision": "block", "reason": reason}, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
