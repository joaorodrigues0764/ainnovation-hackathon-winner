# Como operamos (5 pessoas, ferramentas diferentes)

## 1. Princípios
- Um ficheiro, um sítio. Documentos apontam (ponteiros) em vez de copiar. Índice: `team/INDEX.md`.
- Nada de suposições: cada facto é MEDIDO, LIDO (fonte + data) ou POR VERIFICAR.
- O LLM não faz contas: cálculos em funções testadas. Segredos só em `.env`.
- Revemos tudo, não alteramos nada dos outros sem decisão do grupo registada.

## 2. Quem faz o quê (POR DECIDIR em grupo — proposta do plano, não confirmada)
| Pessoa | Ferramenta | Área | Branch |
|---|---|---|---|
| Aless | Claude (Pro) | API, agente, ferramentas de cálculo, revisões | `aless/<coisa>` |
| luislamy | POR VERIFICAR | página de chat, funcionalidade visível, pitch | `luislamy/<coisa>` |
| 3 restantes | POR VERIFICAR | POR DECIDIR | `nome/<coisa>` |

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
