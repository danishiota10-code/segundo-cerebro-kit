---
name: organizar
description: "Organiza o vault. Encontra notas órfãs, roteia pra estrutura certa, conecta com wikilinks e arquiva redundância, sem mexer nas pastas do sistema. Pergunta quando tiver dúvida."
---

<!-- Gerado de .claude/commands/organizar.md por AIOS/scripts/gerar-skills-codex.py. Edite o comando, não este arquivo. -->

> No Codex: onde este texto disser `/organizar` ou outro comando com barra, entenda a skill `$organizar`. Onde disser "AskUserQuestion", faça a pergunta na conversa com as opções numeradas, uma por vez.

# Organizar: Limpeza e Roteamento do Vault

Use quando o grafo virar uma sopa: notas soltas, sem links, jogadas na raiz ou no Inbox. Este comando roteia tudo pra estrutura que o `/setup` já criou, conecta com wikilinks e arquiva o que for redundante. Nunca reestrutura o vault e nunca apaga nada.

---

## Idioma / Language

Detecte o idioma da mensagem que invocou esse comando e use em todas as perguntas e mensagens.
PT-BR padrão. Inglês ou espanhol se o usuário escreveu nessa língua.
Conteúdo de arquivos, paths e chaves de frontmatter ficam intactos. Não traduza.

---

## Antes de qualquer coisa

Leia no início, sem anunciar:
1. `02 Context/me.md` (quem é o usuário, voz, projetos) no modo solo, OU `02 Context/operator.md` + `organization.md` no modo empresa
2. O arquivo mais recente em `01 Daily/`, pra pegar o contexto da última sessão

---

## Regras duras (NÃO quebre nenhuma)

- **NÃO renomeie, mova nem apague** as pastas do sistema: `00 Inbox`, `01 Daily`, `02 Context`, `03 Projects`, `03 Intelligence`, `04 Resources`, `05 Archives`, `AIOS/`, `knowledge/`, `.claude/`. Os hooks usam esses caminhos exatos, e mexer quebra o agente.
- **NÃO toque** em `README.md`, `CLAUDE.md`, nem em arquivos `index`. Eles aparecem soltos no grafo mas são estruturais e estão corretos assim. Nunca entram na lista de órfãs.
- **NUNCA apague nada.** Redundância vai pra `05 Archives/`, nunca pro lixo.
- **Feche o Obsidian antes de mover arquivos** (evita cópias de conflito tipo "Nota 2.md"). Avise o usuário disso antes de executar a Fase 4.
- Use **wikilinks `[[ ]]`** do Obsidian, nunca link markdown pra notas internas.
- Trabalhe em silêncio na execução. Confirmação só no final.

---

## Fase 1: Mapear (não mude nada)

1. Liste a árvore de pastas atual do vault (até 2 níveis).
2. Identifique as **notas órfãs**: arquivos `.md` que o usuário criou ou colou e que estão soltos. Uma nota é órfã se:
   - não tem nenhum wikilink `[[ ]]` de saída E nenhuma outra nota linka pra ela, OU
   - está na raiz do vault ou em `00 Inbox/` sem destino claro.

   **Exclua sempre** `README.md`, `CLAUDE.md`, qualquer `index`, e notas que já vivem corretamente dentro de uma subpasta de projeto ou contexto e já estão linkadas.
3. Pra cada nota órfã, diga em 1 linha o que ela parece ser.
4. Mostre essa lista pro usuário. Não mude nada ainda.

---

## Fase 2: Classificar e perguntar

Classifique cada nota órfã usando este roteamento:

| Tipo de conteúdo | Destino |
|---|---|
| Identidade, avatar, voz, posicionamento, promessa, oferta | `02 Context/` |
| Projeto real (curso, produto, marketplace, cliente) | `03 Projects/{nome}/` |
| Framework, método, swipe, modelo, prompt reutilizável | `04 Resources/` |
| Pesquisa de mercado ou concorrente, decisão estratégica | `03 Intelligence/` |
| Rascunho sem dono claro | `00 Inbox/` |

**Onde o destino for óbvio, decida sozinho.** Onde NÃO for óbvio, pergunte via AskUserQuestion, **uma pergunta de cada vez**, com as pastas como opções. Pergunte também quando:

- **Duplicatas:** duas notas parecem a mesma coisa.
  - Pergunta: "`{{nota A}}` e `{{nota B}}` parecem o mesmo conteúdo. O que faço?"
  - Header: `Duplicata`
  - Opções: `Juntar numa só` / `Manter A, arquivar B` / `Manter B, arquivar A` / `Manter as duas`

- **Versões "CONSOLIDADO":** vários arquivos parecem versões do mesmo doc.
  - Pergunta: "Achei {{N}} versões de '{{tema}}'. Qual é a boa? As outras vão pra 05 Archives."
  - Header: `Versão boa`
  - Opções: liste os arquivos como opções, mais `Manter todas`

- **Rascunho abandonado:** nota velha, vazia ou claramente descartada.
  - Pergunta: "`{{nota}}` parece rascunho abandonado. Arquivo em 05 Archives?"
  - Header: `Arquivar?`
  - Opções: `Sim, arquivar` / `Não, é importante, manter` / `Você decide onde vai`

- **Destino ambíguo:** não dá pra saber a pasta.
  - Pergunta: "Onde vai '`{{nota}}`'? Resumo: {{1 linha}}."
  - Header: `Destino`
  - Opções: `02 Context` / `03 Projects` / `04 Resources` / `03 Intelligence` / `00 Inbox`

Junte as dúvidas e resolva todas antes de montar o plano. Não comente entre perguntas, vá direto pra próxima.

---

## Fase 3: Plano (espere o "pode ir")

Monte o plano final e PARE:

```
PLANO DE ORGANIZAÇÃO

Mover ({{N}}):
- {{nota}} -> {{pasta destino}}
- ...

Arquivar em 05 Archives ({{N}}):
- {{nota}}: motivo
- ...

Wikilinks a criar:
- {{nota}} liga com {{nota ou hub}}
- ...
```

Pergunte: "Posso executar? (lembra de fechar o Obsidian antes)". Só siga pra Fase 4 com aprovação explícita.

---

## Fase 4: Executar (só depois de aprovado)

Trabalhe em silêncio:

1. **Mover** cada nota pra pasta de destino. Crie subpastas de projeto (`03 Projects/{nome}/`) quando precisar.
2. **Frontmatter:** garanta `type`, `date`, `status`, `tags` em toda nota movida. Preencha o que faltar com base no conteúdo.
3. **Wikilinks:** conecte cada nota ao contexto a que pertence. Notas do mesmo tema linkam entre si (ex: avatar, promessa e método se referenciam e apontam pro hub de `02 Context`). Toda nota deve ter pelo menos 1 link de entrada ou saída no final.
4. **Arquivar:** mova redundância pra `05 Archives/` (nunca apague). Se arquivar várias de um tema, crie um `05 Archives/{tema}/README.md` curto dizendo o que é e por quê.
5. **Index:** atualize `knowledge/index` com as notas roteadas, se o arquivo existir.

---

## Fase 5: Resumo

Mensagem curta, sem floreio:

> "Organizado.
> - Movidas: {{N}} notas para {{pastas}}
> - Linkadas: {{N}}
> - Arquivadas: {{N}} em 05 Archives
> - Ainda em aberto: {{0 ou lista do que você não soube decidir}}
>
> Pode reabrir o Obsidian. O grafo deve estar conectado agora."

---

## Regras

- Auto-save sempre. Nunca peça permissão pra salvar, só pra mover em massa (Fase 3).
- Nunca invente destino. Se não souber, pergunte (Fase 2) ou jogue em `00 Inbox`.
- Nunca apague. Tudo que sai vai pra `05 Archives`.
- Nunca mexa nas pastas do sistema, README, CLAUDE ou index.
- Se o usuário corrigir um roteamento, salve a regra em `02 Context/me.md` pra não repetir o erro.
