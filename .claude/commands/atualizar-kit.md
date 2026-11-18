---
description: Atualiza o vault com a versão nova do segundo-cerebro-kit (comandos, hooks, regras) sem tocar em nenhuma nota sua. Mostra o plano antes e guarda cópia do que trocar.
---

# Atualizar Kit

Traz a versão nova do kit pro vault. Só mexe nos arquivos do sistema (`CLAUDE.md`, `AGENTS.md`, `.claude/`, `.codex/`, `.agents/`, `AIOS/scripts/`, `prompts/`). As notas do usuário, o `AIOS/index.md` e o `AIOS/project-map.md` nunca são tocados. Nada é apagado.

## Passo 1: ver o plano (não muda nada)

Rode na raiz do vault:

```bash
python3 AIOS/scripts/atualizar-kit.py
```

Se o arquivo não existir (vault antigo), clone o kit numa pasta temporária fora do vault e rode o script de lá:

```bash
git clone -q https://github.com/danishiota10-code/segundo-cerebro-kit /tmp/segundo-cerebro-kit
python3 /tmp/segundo-cerebro-kit/AIOS/scripts/atualizar-kit.py --vault . --kit /tmp/segundo-cerebro-kit
```

No Windows (PowerShell), troque `/tmp/` por `$env:TEMP\` e `python3` por `python` se só ele responder.

Se o clone falhar com "Repository not found" ou pedir senha, é acesso: o kit pode estar privado. Peça pro usuário avisar quem passou o kit.

## Passo 2: explicar e confirmar

Mostre o resultado em linguagem simples:
- **Novos**: o que chega (ex.: suporte ao Codex, comando novo).
- **Atualizados**: arquivos do sistema que o usuário nunca editou. Vão ser trocados; a versão atual vai pra uma pasta de cópia ao lado do vault.
- **Mexidos por você**: arquivos do sistema que o usuário editou. O script **não toca**. Pra cada um, rode o `diff` que o script sugere, explique a diferença em uma frase e pergunte, um por vez, se quer: manter o seu, trocar pelo novo (a cópia vai pra pasta de backup) ou juntar os dois.

Pergunte se pode aplicar. Só siga com o "sim".

## Passo 3: aplicar

```bash
python3 AIOS/scripts/atualizar-kit.py --aplicar
```

(ou o comando da primeira vez com `--aplicar` no fim.)

Depois:
- Os arquivos "mexidos" que o usuário decidiu trocar ou juntar: faça agora, guardando antes uma cópia na mesma pasta de backup.
- Se chegou coisa em `.codex/`: avise que, no Codex, na primeira sessão ele roda `/hooks` e aprova os hooks do vault.
- Diga onde ficou a cópia e registre a atualização no daily de hoje.
