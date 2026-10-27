# Como operamos (5 pessoas, ferramentas diferentes)

## 1. Princípios
- Um ficheiro, um sítio. Documentos apontam (ponteiros) em vez de copiar. Índice: `team/INDEX.md`.
- Nada de suposições: cada facto é MEDIDO, LIDO (fonte + data) ou POR VERIFICAR.
- O LLM não faz contas: cálculos em funções testadas. Segredos só em `.env`.
- Revemos tudo, não alteramos nada dos outros sem decisão do grupo registada.

## 2. Quem faz o quê (do quadro de 27/10, ver `team/PLANO_EQUIPA.md`; POR CONFIRMAR com o grupo)
| Pessoa | Ferramenta | Área | Branch |
|---|---|---|---|
| luislamy (Lamy) | POR VERIFICAR | 1 · pipeline RAG | `luislamy/<coisa>` |
| Aless | Claude (Pro) | 2 · KB (com Guilherme e João) | `aless/<coisa>` |
| Guilherme, João | POR VERIFICAR | 2 · KB | `guilherme/<coisa>`, `joao/<coisa>` |
| Simone | POR VERIFICAR | 5 · casos de uso | `simone/<coisa>` |
| POR DECIDIR | — | 3 · backend FastAPI e 4 · front Next.js | — |

## 3. Tokens (Claude Pro e ChatGPT partilhados) — regra para não gastar em duplicado
- Antes de pedir a uma IA: ler `team/INDEX.md` e `team/TRACE.md` (o que já existe) para não refazer.
- Cada ferramenta lê o repo; ninguém cola o repo inteiro no chat. Pede-se só o ficheiro/ponteiro necessário.
- Revisão cruzada por ferramenta diferente da que escreveu (quem escreve não revê).
- Tarefas de contexto longo (revisão final, integração) concentram-se numa só ferramenta por vez; avisar no grupo.

## 4. Git e trace
1. Branch própria `nome/coisa`. `main` só por merge combinado no grupo.
2. Commits pequenos. Última linha da mensagem: `Ferramenta: Claude` | `ChatGPT` | outra.
3. Antes de cada push: `git log origin/main..HEAD --oneline` e `git diff --stat origin/main...HEAD` (quem faz o push lê).
4. Depois do push ou merge, acrescentar 1 linha ao fim de `team/TRACE.md` (ou `sh team/trace.sh "resumo"`). Cada linha aponta para o commit e, se existir, para a revisão.
5. Conflito de git: parar e avisar o grupo; nunca resolver por cima do trabalho de outro. Nunca `--force`, rebase ou apagar branches alheias.

## 5. Revisão
- Quem faz push avisa no grupo (branch + 1 linha do que mudou).
- Revisor (outra ferramenta) usa `team/skills/senior-engineer-review/SKILL.md` e escreve relatório curto: está bem / problemas (alta, média, baixa) / sugestões / choques de integração / perguntas para o grupo.
- Gravidade alta sempre: segurança, dados de menores, contas feitas pelo LLM, segredos no código.

## 6. Relógio
Congelar funcionalidades 14:15 · código 14:40 · entrega 14:55 (prazo 15:00). Detalhe: `team/skills/hackathon-sprint/SKILL.md`.

## 7. Instalar a configuração do grupo (skills, agentes, modelos)
Fonte única no git: `team/skills/`, `team/config/` (agentes, scripts, settings, CLAUDE.md) e `team/docs/`. Cada pessoa corre uma vez, na pasta do repo clonado: `sh team/instalar.sh` (copia para `.claude/`, `CLAUDE.md` e `docs/`, sem sobrescrever o que já existe e sem entrar no git). Claude Code carrega-os sozinho. ChatGPT e outras ferramentas: ler `AGENTS.md` e as skills em `team/skills/` como instruções.
Quem altera a configuração (Aless): `sh team/sync-skills.sh` e commit em `aless/...`. Modelos por agente: Opus 5.5 (planeador, revisor-final, revisor-equipa), Sonnet 5.5 (orquestra, revisor-adversarial), Haiku 5.5 (batedor, escritor, medidor) — plano Pro: máx. 2 Haiku em paralelo.
