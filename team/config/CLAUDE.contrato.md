# CLAUDE.md — Hackathon AInnovation 2026 · Assistente de literacia financeira para jovens

Contrato para qualquer sessão Claude (Cowork, Claude Code, subagentes) neste projeto. Lê isto primeiro, sempre.

## 1. Missão e relógio
- **Desafio:** criar um agente que é um **assistente de literacia financeira para jovens**.
- **Hoje, 27/10/2026. Prazo: 15:00 (Lisboa).** Congelar funcionalidades às **14:15**, código às **14:40**, entrega às **14:55**.
- Plano por blocos de tempo: `docs/PLANO_HACKATHON.md`. Antes de cada tarefa, confirma com `date` em que bloco estamos.
- Repo: `https://github.com/luislamy/ainnovation-hackathon-2026` (privado, equipa: luislamy + Aless).

## 2. Skills deste projeto (em `.claude/skills/`)
| Skill | Quando |
|---|---|
| `hackathon-sprint` | SEMPRE: como operar contra o relógio (blocos, portões, MVP primeiro, demo) |
| `literacia-financeira-jovens` | TODO o conteúdo, prompt do agente, guardrails e testes do domínio |
| `engenharia` | qualquer código (lente sénior + segurança geral) |
| `senior-engineer-review` | revisão antes de cada merge para `main` |
| `deep-research` | só se for preciso confirmar um facto do domínio numa fonte oficial |


## 3. Regras que valem sempre (adaptadas de um workflow de agentes anterior)
1. **Zero suposições:** cada facto é MEDIDO (corri/vi), LIDO (fonte + data) ou POR VERIFICAR. Nunca apresentar dedução como medição.
2. **O LLM não faz contas.** Valores (juros, poupança, orçamento) calculam-se em funções testadas; o modelo só explica. O cliente envia a intenção; o servidor deriva o valor.
3. **Segredos nunca no repo nem na linha de comandos.** Só em `.env` (ignorado). `.env.example` com placeholders `COLA_AQUI_<NOME>`.
4. **Não é aconselhamento financeiro:** educa, não recomenda produtos nem investimentos concretos (ver skill do domínio).
5. **Dados mínimos:** o assistente não pede nem guarda IBAN, cartões, passwords, NIF ou dados de saúde. Utilizadores podem ser menores.
6. **MVP primeiro:** um fluxo ponta-a-ponta feio a funcionar às **12:45** vale mais do que três meio feitos.
7. **Commits pequenos e frequentes**, mensagem clara. Claude faz commits; **push só com OK do Aless** (ou se ele disser «push livre» para o hackathon). Nada se apaga sem OK.
8. **Respostas ao humano:** veredicto primeiro, ≤5 linhas, tabela se houver números. Comandos num só bloco, com caminho absoluto.
9. **Modelos e agentes:** método de agentes — Opus planeia e faz a revisão final, Sonnet orquestra, Haiku faz o trabalho bruto. Ver §6.

## 4. Stack (decidir às 11:15 — ver `docs/PLANO_HACKATHON.md` §2)
Por omissão, se ninguém decidir outra coisa: **Python 3 + FastAPI** (API do agente e ferramentas de cálculo) + **página web única** (HTML/JS) para o chat + um fornecedor de LLM via variável de ambiente (`LLM_PROVIDER`, `LLM_API_KEY`). Se o hackathon impuser plataforma ou modelo (ex.: Azure OpenAI, NTT DATA), essa regra ganha a esta.

## 5. Estrutura
```
CLAUDE.md                 este contrato
README.md                 como correr + pitch curto
docs/PLANO_HACKATHON.md   blocos de tempo, âmbito, portões, demo
docs/AVALIACAO.md         casos de teste do agente (comportamento esperado)
.claude/skills/           skills adaptadas
.env.example              variáveis (sem valores)
```

## 6. Workflow de agentes (método de agentes, 27/10/2026)

| Papel | Quem | Modelo · effort | Faz | Não faz |
|---|---|---|---|---|
| Decide | Aless (e as especificações do outro chat) | — | aprova, decide, faz push | — |
| Planeia | subagente `planeador` | **Opus 5.5 · low** (medium se tocar em segurança/dados ou o Aless pedir) | plano do bloco em tarefas pequenas, com `depende:` e critério de feito medível | código |
| Orquestra | sessão principal Claude Code | **Sonnet 5.5 · medium** | distribui tarefas aos Haiku, revê cada entrega com 4 perguntas (fronteira, falha silenciosa, teste que distingue, sintoma vs causa), devolve com a lacuna nomeada (máx. 2 devoluções), integra e commita | trabalho braçal |
| Bruto | subagentes `batedor`, `escritor`, `medidor` | **Haiku 5.5 · low** | batedor: procurar/ler ficheiros e logs · escritor: código e testes · medidor: correr testes, curl, medir | decidir âmbito, git de escrita |
| Revisão adversarial | `revisor-adversarial` | Sonnet 5.5 · medium | só em código de dados, segurança ou guardrails | — |
| Revisão final | `revisor-final` | **Opus 5.5 · medium** | diff completo antes de cada merge para `main`/pedido de push e no Portão 2 | push |

**Ciclo por bloco:** especificação → `planeador` (Opus) → orquestrador (Sonnet) distribui → Haiku executam → orquestrador verifica e commita → `revisor-final` (Opus) antes do merge → Aless faz push.
**Regras:** quem escreve não revê; modelo sempre explícito; omissão dos subagentes = Haiku (`.claude/settings.json`); no máximo 2 Haiku em paralelo (plano Pro); se o relógio apertar, o orquestrador corta âmbito e avisa o Aless numa linha.
**Arranque da sessão principal (Terminal do Mac):**

    cd <pasta-do-repo> && claude --model claude-sonnet-5-5 --effort medium

Sessões extra em segundo plano: `sh .claude/scripts/lancar-agente.sh <nome> <ficheiro-ordem> <effort> <modelo>`. Ver modelos e consumo reais: `python3 .claude/scripts/painel-agentes.py`.

## 7. Equipa de 5 com ferramentas diferentes (Claude, ChatGPT e outras) — 27/10/2026
**Regra principal: revemos tudo, não alteramos nada dos outros sem decisão do grupo.** Apontamos, sugerimos, ajudamos a integrar.

| Regra | Como |
|---|---|
| Saber quem fez o quê | antes de rever, correr `sh .claude/scripts/quem-fez.sh` (autor, branch, ficheiros, hora). Nunca adivinhar autoria: se o commit não identifica a pessoa, escrever «autor POR VERIFICAR» |
| Código dos outros | só leitura. Nada de editar, reverter, rebase, merge ou apagar ficheiros/branches de outra pessoa sem decisão do grupo registada (quem decidiu, quando) |
| O nosso código | na nossa branch (`aless/<coisa>`), commits pequenos; merge para `main` só depois de o grupo concordar |
| Revisão | agente `revisor-equipa` (Opus 5.5 low) → relatório em `docs/revisoes/AAAA-MM-DD_HHMM_<autor>_<branch>.md` (local). O Aless decide se o partilha e onde (chat do grupo, issue ou comentário no GitHub). Publicar no GitHub só com OK dele |
| Linguagem dos relatórios | curta, direta, termos simples, sem jargão, sem culpar pessoas: falar do código, não de quem o escreveu. Começar pelo que está bem |
| Integração | procurar choques entre o nosso trabalho e o dos outros: nomes de ficheiros, rotas da API, variáveis de ambiente, versões de dependências, formato das mensagens do agente. Propor uma solução, não impor |
| Conflito de git | parar e avisar o Aless numa linha; nunca resolver por cima do trabalho de outro |
| Propostas ao grupo (precisam de decisão coletiva) | 1) uma branch por pessoa `nome/coisa`; 2) `main` só por merge combinado; 3) cada commit diz a ferramenta usada no fim da mensagem (`Ferramenta: Claude` / `ChatGPT` / ...); 4) uma lista curta de quem faz o quê no README |

## 8. Autonomia sobre a própria configuração (Aless, 27/10/2026)
O Claude deste projeto PODE corrigir a sua configuração local (`CLAUDE.md`, `.claude/skills/`, `.claude/agents/`, `.claude/settings.json`, `.claude/scripts/`) quando um erro vem dela, sem pedir OK, com 3 condições: 1) cópia antes em `.claude/backups/<ficheiro>.<HHMM>`; 2) uma linha em `.claude/backups/ALTERACOES.md` (hora, ficheiro, erro, correção); 3) avisar o Aless numa linha. Não pode: mexer no `.gitignore` para incluir coisas locais no git, enfraquecer guardrails do domínio ou regras de segredos, nem alterar código de outros membros.
**Git:** trabalho local no SSD; antes de cada push, mostrar ao humano o resumo do que sobe (`git log` + `git diff --stat`) para ele ler e confirmar; ele corre o push (comando num só bloco, caminho absoluto).
