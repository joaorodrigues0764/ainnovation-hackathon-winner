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

## Proposta para a KB (2) — a validar com Lamy (1) e Simone (5)
- Conteúdo: só fontes oficiais, pela hierarquia de `team/skills/literacia-financeira-jovens/SKILL.md` §4 (Todos Contam, Portal do Cliente Bancário, CMVM, Finanças/SS).
- Formato único de pedaço (chunk), um por linha em `kb/chunks.jsonl`: `id`, `texto`, `tema`, `entidade`, `fonte_url`, `data_consulta`. Sem fonte e data, não entra (zero suposições).
- A KB só tem texto e metadados; **valores e contas ficam nas funções**, nunca em pedaços da KB.
- Os 5 UCs da Simone definem os temas a cobrir primeiro (a KB segue os UCs).
- Contrato 1↔2: Lamy lê `kb/chunks.jsonl`. Se preferir outro formato, decide-se já, antes de escrever conteúdo.

## Por decidir em grupo
1. Quem faz o backend (3) e o front (4).
2. Ollama local confirmado? Qual o modelo, e corre nos portáteis da demo?
3. Formato dos pedaços da KB (proposta acima).
4. Os 5 UCs (Simone) — lista final.
