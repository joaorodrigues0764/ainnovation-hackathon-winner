# Plano da equipa — leitura do quadro (27/10/2026, 11:30)
Fonte: `team/assets/quadro-planeamento-2026-10-27.jpg`. Leitura feita a partir de uma foto: o que está marcado POR CONFIRMAR deve ser validado por quem desenhou o quadro.

## Arquitetura (LIDO no quadro)
Pergunta → **RAG** (pipeline) → **Prompt** → **LLM** → resposta, tudo atrás de uma API que serve o front-end.
| Nº | Peça | Detalhe lido | Quem (quadro) |
|---|---|---|---|
| 1 | Pipeline RAG | retrieval híbrido (BM25 + vetorial), «mais semelhantes», variantes de RAG (HyDE); monta o prompt | Lamy (luislamy) |
| 2 | KB (base de conhecimento) | vetorial/índice; alimenta o RAG | Guilherme, João, Alessandro (Aless) |
| 3 | Backend | Python, FastAPI, Ollama (LLM local; nome do modelo ilegível: POR CONFIRMAR) | POR DECIDIR (quadro não indica) |
| 4 | Front-end | Next.js, chat | POR DECIDIR |
| 5 | UCs (casos de uso) | 5 casos de uso com ecrã de chat | Simone |

## Ordem (LIDO)
1, 2 e 5 em paralelo → 3 → 4. Fases: 1) RAG funcional · 2) juntar RAG à API · 3) UI · 4) Harness Engineering.

## O que muda face ao nosso plano anterior
| Antes (`docs/PLANO_HACKATHON.md`) | Agora |
|---|---|
| Aless = API + ferramentas de cálculo | Aless = **KB (2)** com Guilherme e João |
| Front = página HTML única | Next.js |
| LLM = o que o desafio fornecer | Ollama local (POR CONFIRMAR face às regras do desafio) |
| 3 ferramentas de cálculo no centro | continuam obrigatórias («o LLM não faz contas») mas ficam como ferramentas no backend (3) / harness (4) |

## KB (2) — formato decidido: o do Lamy (PR #3), 27/10 11:50
- Um ficheiro `.md` por fonte em `backend/kb/`, com front matter (`title`, `source`, `url`, `journey`, `collected`). Detalhe: `docs/KB_CONTRACT.md` (PR #3). Substitui a proposta `chunks.jsonl`.
- Conteúdo: só fontes oficiais, pela hierarquia de `team/skills/literacia-financeira-jovens/SKILL.md` §4. `url` = página exata do tema; números sempre com data ou período.
- A KB só tem texto; **valores e contas ficam nas funções**, nunca na KB.
- Jornadas a acrescentar ao contrato (proposta): `burlas` e `poupanca`, além de `credito`, `salario`, `irs`, `geral`.
- Os 5 UCs da Simone definem os temas a cobrir primeiro.

## Por decidir em grupo
1. Quem faz o backend (3) e o front (4).
2. Ollama local confirmado? Qual o modelo, e corre nos portáteis da demo?
3. Jornadas novas `burlas` e `poupanca` no contrato da KB.
4. Os 5 UCs (Simone) — lista final.
