# Quadro de estado (cada agente atualiza a SUA linha ao acabar uma tarefa; 1 linha por pessoa)

Última atualização: 27/10 12:20 (Lisboa). Ver também `team/TRACE.md` (histórico) e `team/handoff/` (passagens entre agentes).

| Pessoa | Ferramenta | A fazer agora | Branch / PR | Bloqueio / pedido aos outros |
|---|---|---|---|---|
| Lamy | POR VERIFICAR | `feat/api` (API FastAPI + SSE), pequena alteração em curso | `feat/api` | **Não aprovar o PR dele ainda** (pedido dele, 12:14) |
| Aless | Claude | calculadoras (`backend/calculators.py`), depois KB dos UC-03/07/08/12/17 e texto dos guardrails | `aless/calc` (a criar) | Lamy: ligar `mask_pii` e `calcular()` na API; responder ao comentário do PR #6 |
| Simone | POR VERIFICAR | casos de uso (`USE_CASES.md`, 18 UCs em `main`) | — | — |
| Guilherme, João | POR VERIFICAR | KB (com Aless) | POR VERIFICAR | — |

## Por decidir (grupo)
1. OpenAI ou Ollama (hoje o código usa a API da OpenAI, gpt-4o-mini por omissão).
2. Deteção automática da jornada (hoje vem do cliente) e idade mínima (UC dizem 18–25; plano inicial 14–25).
3. Quem faz o front-end (Next.js).
