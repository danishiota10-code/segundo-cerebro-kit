# AI OS — instruções pro Codex

Este vault é o mesmo do Claude Code. As regras ficam num lugar só: **leia o `CLAUDE.md` da raiz inteiro, agora, antes de responder**, e siga tudo que ele diz como se estivesse escrito aqui.

Diferenças do Codex:

- Os comandos do kit (`/setup`, `/organizar`, `/assistente`...) aqui são skills em `.agents/skills/`. Chame com `$` (`$setup`, `$organizar`) ou peça pelo nome.
- Onde uma skill diz "pergunte via AskUserQuestion", faça a pergunta na conversa, com as opções numeradas, uma pergunta por vez.
- O hook de início (`.codex/hooks.json`) já injeta o `me.md` e o último daily. Se esse bloco não veio, leia os arquivos do Session Startup do `CLAUDE.md` você mesmo.
