# Segundo Cérebro — Starter Kit

**por Daniel Shiota** · [WhatsApp](https://wa.me/61414059664)

---

> Transforme o Obsidian no seu sistema operacional com IA.
> Funciona com Claude Code, Cursor, Gemini CLI — qualquer ferramenta que leia markdown.

---

## Pré-requisitos

Antes de começar, tenha instalado:

- **Claude Code** (plano Pro ou Max): [claude.com/code](https://claude.com/code)
- **Obsidian** (grátis): [obsidian.md](https://obsidian.md)
- **Git** (já vem no macOS; no Windows, use o [Git for Windows](https://git-scm.com))
- **Python 3** (`python3` disponível no terminal). É o que faz a injeção de contexto e a documentação automática rodarem. No macOS já vem instalado; no Windows, instale pela [python.org](https://www.python.org) ou use o WSL. Sem Python, o vault e os comandos continuam funcionando, você só perde a automação dos hooks.

No Windows, o caminho mais tranquilo continua sendo o WSL (Ubuntu). Lá o `python3` e os hooks funcionam igual ao macOS, sem nenhum passo extra.

**Se você for rodar no Windows nativo (PowerShell), troque o arquivo de hooks:**

```
copy .claude\settings-windows.json .claude\settings.json
```

Não é preferência, é obrigatório. O `settings.json` padrão usa `$CLAUDE_PROJECT_DIR`, que é expansão de shell POSIX. O PowerShell lê variável de ambiente como `$env:CLAUDE_PROJECT_DIR`, então `$CLAUDE_PROJECT_DIR` vira string vazia, o hook aponta para um caminho que não existe, e o erro do Python aparece colado no fim de cada resposta. A versão Windows resolve deixando o Python ler a variável, então não sobra nada para o shell expandir.

Ela também chama `python` em vez de `python3`: a instalação da python.org entrega `python.exe` e `py.exe`, sem `python3.exe`, e só a da Microsoft Store tem esse nome. Roda `python --version` e `python3 --version` e usa o que responder.

Se for editar esse comando na mão, **copia ele exatamente**. O `run_name='__main__'` tem dois underscores de cada lado, e com um só o hook não roda nada e ainda assim sai com código 0, ou seja, parece saudável e não faz absolutamente nada.

---

## Começar em 1 minuto (cola o link no Claude ou no Codex)

Não precisa saber terminal nem git. Faz assim:

1. Instala o Claude Code: [claude.com/code](https://claude.com/code) (plano Pro ou Max)
2. **Cria uma pasta pro teu segundo cérebro num lugar limpo** — tipo `~/segundo-cerebro` ou dentro de `~/Documents`. **NÃO use Downloads nem Desktop, e não ponha espaço no nome da pasta** (o macOS bloqueia Downloads/Desktop, e espaço quebra comandos).
3. Abre o Claude Code **dentro dessa pasta**. Essa pasta vai virar teu segundo cérebro.
4. Cola exatamente esta frase:

```
Criar meu segundo cérebro com esse repositório: https://github.com/danishiota10-code/segundo-cerebro-kit
```

5. Aceita as permissões quando ele pedir. Não digite nenhum comando `/` — deixa o Claude conduzir.

> A mensagem precisa ter SEMPRE o link junto. "Criar meu segundo cérebro" sozinho não basta — o Claude precisa do link.

O Claude monta o vault na pasta atual, instala o time de subagents e te guia pela personalização. Em poucos minutos teu sistema tá rodando.

---

> [!IMPORTANT]
> **Se você é a IA que recebeu o link acima, leia com atenção.**
>
> **Gatilho:** quando o usuário disser que quer "criar/montar/configurar o segundo cérebro" (ou "second brain") e mandar o link deste repositório, ele quer que você execute o setup completo abaixo — sem perguntar "o que você quer que eu faça", sem só listar arquivos. Aja direto.
>
> NÃO use slash commands (`/setup`, `/obsidian:setup`, etc.) — o usuário pode ter plugins instalados que colidem com esses nomes e disparam o produto errado. Faça tudo você mesmo, lendo arquivos e executando, nesta ordem:
>
> **O vault vai na PASTA ATUAL** (onde o usuário abriu o Claude). É lá que ele quer o segundo cérebro.
>
> 1. **Verifique se a pasta atual é segura, ANTES de clonar.** Rode `pwd`.
>    - Se o caminho contém `/Downloads/` ou `/Desktop/` → **PARE e não clone.** Diga: "O macOS bloqueia escrita em Downloads e Desktop. Fecha o Claude, cria uma pasta tipo `~/segundo-cerebro` (sem espaço no nome), abre o Claude dentro dela e cola a frase de novo."
>    - Se o caminho tem **espaço** no nome (ex: `second brain`) → **PARE.** Diga: "O nome da pasta tem espaço, o que quebra comandos. Cria uma pasta sem espaço, ex: `~/segundo-cerebro`, abre o Claude lá e tenta de novo."
>    - Se passou nas duas → a pasta atual vira o vault. Siga.
> 2. **Clone o conteúdo do repo NA pasta atual:**
>    - Se a pasta estiver vazia: `git clone https://github.com/danishiota10-code/segundo-cerebro-kit.git .`
>    - Se já tiver arquivos: `git clone https://github.com/danishiota10-code/segundo-cerebro-kit.git segundo-cerebro-kit && cd segundo-cerebro-kit`
>    - **Codex:** o sandbox padrão do Codex bloqueia a internet, e o clone falha com "Could not resolve host". Peça a aprovação do usuário pra rodar o `git clone` com acesso à rede. Se a aprovação for recusada ou nem puder ser pedida, **não peça ZIP e não use cópia do kit que já esteja no computador** (pode ser velha): mande o usuário sair do Codex e seguir a seção "Instalar pelo Codex" deste README, que clona pelo terminal. Também não crie nem reescreva o `AGENTS.md`: o kit já traz o dele.
>    - **Depois do clone, rode `git remote remove origin`.** O vault é do usuário e não pode ter caminho de volta pro repositório do kit: quem recebe acesso ao kit tem permissão de escrita nele, e um `git push` subiria o vault pessoal dele pra lá.
>    - Se o clone falhar com "Repository not found" ou pedir senha, é acesso, não erro de digitação: o repositório é privado. Diga ao usuário pra aceitar o convite que chegou no e-mail do GitHub e rodar `gh auth login` no terminal, fora do Claude, e tente de novo.
> 3. **Detecte o sistema operacional e aja de acordo, SEM perguntar ao usuário.** Você já sabe qual é: o seu contexto de ambiente diz a plataforma em que você roda (`win32` = Windows nativo, `darwin` = macOS, `linux` = Linux ou WSL, e WSL conta como Linux). Não assuma macOS por padrão.
>    - **macOS, Linux ou WSL:** não troque nada, o `settings.json` do clone já está certo.
>    - **Windows nativo (PowerShell):** copie `.claude/settings-windows.json` por cima de `.claude/settings.json`. Obrigatório, não preferência: o padrão usa `$CLAUDE_PROJECT_DIR`, que é expansão POSIX e vira string vazia no PowerShell, então todo prompt volta com um erro de Python grudado. Depois rode `python --version`; se só `python3` responder, troque a primeira palavra dos três comandos para `python3`. Declare no seu plano qual sistema detectou e qual arquivo ficou valendo.
> 4. (No Codex, pule os passos 4 e 5: subagents são só do Claude Code.) **Os subagents já vieram no clone.** Estão em `.claude/agents/`, dentro do vault. Nada pra instalar, nada pra baixar de fora, e nada é escrito na pasta pessoal do usuário — o Claude Code carrega agent de projeto sozinho.
> 5. **Confirme** que `.claude/agents/` contém os quatro: `vault-keeper`, `social-agent`, `decision-tracker`, `research-agent`
> 6. **Rode o onboarding LENDO o arquivo, não via slash command.** Leia `.claude/commands/setup.md` (na pasta do vault) e execute aquele fluxo de entrevista diretamente na conversa: faça as perguntas, preencha `02 Context/me.md` com as respostas reais. Você está executando o conteúdo do arquivo, não invocando `/setup`.
> 7. **Prove que funcionou:** leia o `me.md` recém-preenchido e resuma de volta pro usuário quem ele é, do jeito que o `vault-keeper` faria.
> 8. **Oriente o próximo passo:** diga pro usuário, daqui pra frente, abrir o Claude Code E o Obsidian **nesta mesma pasta** — é onde os hooks de documentação automática e os comandos do vault ficam ativos.
>    - **Codex:** diga também que, na próxima vez que abrir o `codex` nesta pasta, é pra rodar `/hooks` e aprovar os dois hooks do vault (início e fim de sessão). Sem isso o Codex não carrega o `me.md` nem o daily. Os comandos aqui são `$setup`, `$organizar`, `$assistente`.
>
> Avise no começo que vai pedir permissão pra rodar `git`, e que é só aceitar.

---

## Instalar pelo Codex

O Codex costuma bloquear a internet dentro da conversa, então o clone vai pelo terminal, antes de abrir o Codex. No terminal (fora do Codex), cola:

```bash
git clone https://github.com/danishiota10-code/segundo-cerebro-kit.git ~/segundo-cerebro && cd ~/segundo-cerebro && git remote remove origin && codex
```

Isso baixa o kit pra pasta `~/segundo-cerebro`, corta o vínculo com o GitHub (o vault é seu) e abre o Codex dentro dela. Lá dentro:

1. Se ele perguntar se confia na pasta, responda que sim.
2. Rode `/hooks` e aprove os dois hooks do vault. São eles que carregam o seu `me.md` e o último daily e pedem pra salvar a sessão.
3. Digite `$setup` pra personalizar o vault.

---

## Mapa rápido do vault

- [[CLAUDE]] contexto principal para a IA
- [[AIOS/index]] comandos, mapas e camada portátil
- [[AIOS/Vault-Map]] sitemap e roteamento
- [[knowledge/index]] conhecimento permanente
- [[prompts/README]] prompts copy-paste
- [[00 Inbox/CLAUDE]] captura temporária
- [[01 Daily/CLAUDE]] notas diárias
- [[02 Context/CLAUDE]] identidade e contexto
- [[03 Projects/CLAUDE]] projetos ativos
- [[03 Intelligence/decisions/README]] decisões, reuniões e pesquisas
- [[04 Resources/CLAUDE]] biblioteca reutilizável
- [[05 Archives/_guide]] histórico

---

## O que está incluído

```
segundo-cerebro-kit/
├── .claude/
│   ├── agents/                   → Os 4 subagents, já inclusos
│   └── commands/
│       ├── setup.md              → Personalização inicial completa
│       ├── assistente.md         → Operação diária (sessões, revisões, tasks)
│       ├── importar-contexto.md  → Trazer contexto de outra IA
│       ├── escrever.md           → Texto curto na sua voz
│       ├── linkedin.md           → Post LinkedIn dedicado
│       ├── newsletter.md         → Edição de newsletter completa
│       ├── case-study.md         → Case study estruturado
│       ├── landing-page.md       → Brief de landing page
│       ├── seo-pagina.md         → Auditoria SEO de URL
│       ├── email-sequencia.md    → Drip campaign automatizada
│       ├── ads-google.md         → Google Ads (audit/build/optimize/copy)
│       └── pesquisa.md           → Deep research multi-fonte
├── CLAUDE.md                     → Contexto para o Claude (auto-loaded)
├── 00 Inbox/                     → Zona de captura
├── 01 Daily/                     → Notas de sessão e diário
├── 02 Context/                   → Identidade permanente (me.md, estratégia, marca)
├── 03 Projects/                  → Projetos ativos
├── 03 Intelligence/              → Pesquisas, decisões, reuniões, market intel
├── 04 Resources/                 → Biblioteca pessoal (textos, cases, ads, SEO)
└── prompts/                      → 10 prompts copy-paste prontos
```

---

## Instalação em 3 passos

### Passo 1 — Clone o repositório

```bash
git clone https://github.com/danishiota10-code/segundo-cerebro-kit.git meu-vault
cd meu-vault
git remote remove origin
```

### Passo 2 — Abra como vault no Obsidian

- Abra o Obsidian
- Clique em "Open folder as vault"
- Selecione a pasta `meu-vault`

### Passo 3 — Rode o setup no Claude Code

```bash
claude
```

Se voce seguiu o fluxo "Comecar em 1 minuto", nao precisa rodar comando: o Claude le `.claude/commands/setup.md` e executa o onboarding na conversa.

Se voce instalou manualmente via `git clone`, dentro do Claude Code rode `/setup`. Ele vai:
1. Perguntar se você quer um agente persistente
2. Oferecer importar contexto de outra IA (ChatGPT, Claude, Gemini)
3. Fazer 8 perguntas curtas
4. Preencher seu `me.md` com dados reais (não placeholders)

### Passo 4: confira que os hooks estão vivos

```bash
python3 .claude/hooks/test-hooks.py     # Mac e Linux
python .claude/hooks/test-hooks.py      # Windows
```

Espere `RESULTADO: 17/17 casos passaram` e código de saída `0`. O teste roda os hooks de verdade em vez de ler o código e achar que está tudo certo.

Um hook ligado no evento errado é o defeito mais caro que existe, porque ele roda, sai com código `0`, e não faz absolutamente nada. Tem cara de saúde. Esse teste é o que separa um hook vivo de um hook que só parece vivo.

---

## Comandos disponíveis

### Operacional

| Comando | O que faz |
|---|---|
| `/setup` | Personalização inicial completa do vault |
| `/assistente` | Operação diária: resume sessão, revisão diária/semanal, tasks, memória, reunião |
| `/organizar` | Limpa o vault: roteia notas órfãs, conecta com wikilinks, arquiva redundância |
| `/importar-contexto` | Traz contexto de outra IA (ChatGPT, Claude, Gemini, Perplexity) |
| `/atualizar-kit` | Traz a versão nova do kit sem tocar nas suas notas |

### Escrita e conteúdo

| Comando | O que faz |
|---|---|
| `/escrever` | Texto curto na sua voz — 3 variações (post LinkedIn, email, headline, bio, caption) |
| `/linkedin` | Post LinkedIn dedicado com hooks testados, 4 estruturas, repurpose de YT/blog |
| `/newsletter` | Edição completa de newsletter — 3 subjects, corpo estruturado, P.S. |
| `/case-study` | Case study estruturado — entrevista, citações, números, lições |

### Web e SEO

| Comando | O que faz |
|---|---|
| `/landing-page` | Brief de landing page completo (positioning, headline, copy seção por seção) |
| `/seo-pagina` | Auditoria SEO de uma URL — on-page, meta, schema, relatório priorizado |

### Crescimento

| Comando | O que faz |
|---|---|
| `/email-sequencia` | Drip campaign — welcome, onboarding, nurture, win-back, pré-venda |
| `/ads-google` | Google Ads — audit, build, optimize, copy |
| `/pesquisa` | Deep research multi-fonte com citações verificáveis |

Todos os comandos funcionam em PT-BR por padrão, mas detectam o idioma da sua mensagem e adaptam.

---

## Os 10 prompts copy-paste

Pra quando você quer só colar no chat sem rodar comando:

| # | Arquivo | Para que serve |
|---|---------|---------------|
| 01 | `revisao-diaria.md` | Revisar o dia, capturar aprendizados |
| 02 | `notas-reuniao.md` | Processar reuniões em ações claras |
| 03 | `brief-conteudo.md` | Criar brief de conteúdo para qualquer canal |
| 04 | `rascunho-email.md` | Redigir e-mails profissionais |
| 05 | `plano-projeto.md` | Estruturar qualquer novo projeto |
| 06 | `pesquisa-concorrentes.md` | Mapa competitivo rápido |
| 07 | `post-linkedin.md` | Post de LinkedIn no seu estilo de voz |
| 08 | `revisao-semanal.md` | Revisão semanal estruturada |
| 09 | `registro-decisao.md` | Documentar decisões com raciocínio |
| 10 | `despejo-ideias.md` | Capturar e organizar ideias brutas |

---

## Fluxo recomendado pra primeira semana

1. **Dia 1 — Setup**
   - Roda `/setup`. Se você usa ChatGPT, escolhe "Sim — uso ChatGPT" pra importar contexto profundo
   - Revisa `02 Context/me.md` e ajusta o que não bate

2. **Dia 2 — Primeiro conteúdo**
   - Roda `/linkedin` pra produzir 1 post completo
   - Avalia se a voz está acertada — ajusta `me.md` se precisar

3. **Dia 3 — Sua oferta**
   - Roda `/landing-page` pra mapear seu produto ou serviço principal
   - Salva em `04 Resources/landing-pages/`

4. **Dia 4 — Captação**
   - Roda `/email-sequencia` modo "Welcome" pra quando alguém entrar na sua lista
   - Roda `/seo-pagina` na URL da landing pra ver gaps

5. **Dia 5 — Newsletter ou case**
   - Se você manda newsletter: `/newsletter`
   - Se você quer documentar caso: `/case-study`

6. **Dia 6 — Pesquisa estratégica**
   - Roda `/pesquisa` sobre algo importante (concorrente, tendência, ferramenta)

7. **Dia 7 — Revisão**
   - Roda `/assistente` e pede "revisão semanal" — fecha a semana com clareza

Depois disso, `/assistente` vira o comando principal do dia a dia. Os outros comandos viram especialistas que você chama quando precisa.

---

## Atualizar o kit sem perder nada

Quando o kit ganhar coisa nova, rode `/atualizar-kit` no Claude Code (ou `$atualizar-kit` no Codex). Ele mostra o plano antes de mudar qualquer coisa:

- **Novos:** arquivos que o seu vault ainda não tem. São copiados.
- **Atualizados:** arquivos do sistema que você nunca editou. São trocados, e a versão antiga vai pra uma pasta `<seu vault>-backup-kit-<data>` ao lado do vault.
- **Mexidos por você:** arquivos do sistema que você editou. Ele não toca; mostra a diferença e pergunta.

Só mexe em `CLAUDE.md`, `AGENTS.md`, `.claude/`, `.codex/`, `.agents/`, `AIOS/scripts/`, nas regras do `AIOS/` e em `prompts/`. As suas notas, o `me.md`, os dailies, o `AIOS/index.md` e o `AIOS/project-map.md` ficam de fora. Nada é apagado.

**Vault criado antes do `/atualizar-kit` existir?** Cole no Claude:

```text
Atualiza meu vault com a versão nova do kit https://github.com/danishiota10-code/segundo-cerebro-kit sem mexer nas minhas notas: clona o kit numa pasta temporária fora do vault, roda o AIOS/scripts/atualizar-kit.py de lá com --vault apontando pra este vault, me mostra o plano e só aplica depois do meu ok.
```

---

## Usar no Codex

O mesmo vault funciona no Codex, da OpenAI. Abra o terminal na pasta do vault e rode `codex`.

- O Codex lê o `AGENTS.md`, que manda ler o `CLAUDE.md`. As regras ficam num lugar só.
- Na primeira sessão, rode `/hooks` e aprove os dois hooks do vault. São eles que carregam o seu `me.md` e o último daily no começo e pedem pra salvar a sessão no fim.
- Os comandos viram skills: `$setup`, `$organizar`, `$assistente`... (digite `$` pra ver a lista).
- Os subagents e a documentação automática do fim de sessão são só do Claude Code.

Testado no macOS. No Windows nativo os hooks do Codex ainda não foram testados; use o WSL.

---

## Quando o grafo do Obsidian bagunçar

Conforme você cola notas e trabalha, o grafo vai encher de notas soltas, sem links. É normal, não é defeito. Rode `/organizar`: ele encontra as notas órfãs, roteia pras pastas certas, conecta com wikilinks e arquiva o que for redundante, sem mexer na estrutura do vault nem nos hooks. Ele pergunta antes de mover quando tiver dúvida.

---

## O time de subagents

Esse vault é o cérebro. Os **subagents** são o time que trabalha em cima dele. Eles já vêm no clone, em `.claude/agents/` — não tem nada pra instalar.

| Subagent | O que faz |
|---|---|
| `vault-keeper` | Lê esse vault e responde com contexto histórico, citando o arquivo |
| `social-agent` | Rascunha respostas pra Telegram, Discord ou iMessage com o contexto dos seus projetos |
| `decision-tracker` | Captura decisões em `03 Intelligence/decisions/`, com o porquê junto |
| `research-agent` | Auditoria de anúncios, variações de copy e plano de mídia, só de fonte pública |

Como ficam dentro do vault e não na sua pasta pessoal, cada vault pode ter o seu time, ajustado ao trabalho dele. Pra editar um, abre o arquivo — é markdown, igual ao resto.

---

## Quer montar isso com alguém do lado

Esse kit é o sistema inteiro, de graça. Se você prefere montar acompanhado, eu dou um treinamento 1:1 de 6 aulas: a gente instala na sua máquina, coloca o seu contexto dentro, conecta o seu e-mail e os seus números, e deixa uma automação rodando sozinha. Você digita, eu conduzo.

**[Falar comigo no WhatsApp](https://wa.me/61414059664)**

---

*Feito com Claude Code. Distribuído gratuitamente.*
