# Caixa Explica — front-end

Next.js 16 (App Router) + TypeScript + Tailwind CSS 4. Fala com a API de `backend/` por `POST /chat/stream` (Server-Sent Events).

## Correr

Primeiro a API (ver [`backend/README.md`](../backend/README.md)):

```powershell
cd backend
uvicorn api:app --reload --port 8000
```

Depois, noutro terminal:

```powershell
cd frontend
npm install
npm run dev        # http://localhost:3000
```

Se a API estiver noutro endereço, copiar `.env.example` para `.env.local` e mudar `NEXT_PUBLIC_API_URL` (é lido no build; reiniciar o `npm run dev`). A API só aceita pedidos de `http://localhost:3000` por omissão (`CORS_ORIGINS` no `.env` da raiz).

Verificar antes de um PR:

```powershell
npx tsc --noEmit
npm run lint
npm run build
```

## Requisitos mínimos da UI

| # | Requisito | Onde |
| --- | --- | --- |
| 1 | Escolher a jornada (crédito, salário, IRS, burlas, poupança, geral), vinda de `GET /journeys` | `app/page.tsx` |
| 2 | Perfil curto e opcional (idade, rendimento, objetivo), validado, só em memória (RF1, privacidade) | `components/ProfileForm.tsx` |
| 3 | Escrever pergunta (Enter envia, Shift+Enter muda de linha), resposta a chegar em stream, botão Parar | `components/Composer.tsx` |
| 4 | Citações `[n]` clicáveis e lista de fontes com link (RF3) | `components/Answer.tsx`, `Sources.tsx` |
| 4b | Cartão de resposta (PRD): número em destaque vindo só das calculadoras (evento `tool`, marcado "calculado"), explicação, "Próximo passo" destacado e fontes. Com crédito + poupança mostra os dois lado a lado | `lib/card.ts`, `components/ResultCard.tsx` |
| 5 | Follow-ups com histórico ("e se for a 60 meses?", RF7) e "Nova conversa" | `lib/chat.ts` |
| 5b | Sugestões de perguntas seguintes (até 3) depois de cada resposta, a partir das calculadoras que correram (prazos ±12 meses com os valores reais, poupar em vez de crédito, guardar mais por mês…), dos guardrails e da jornada. Sem chamada ao LLM; nunca repetem perguntas feitas nem prazos já calculados | `lib/followups.ts` |
| 6 | Aviso quando a mensagem tinha dados pessoais (UC-04) | `components/ExchangeView.tsx` |
| 7 | Erros claros com "Tentar outra vez"; aviso se a API estiver em baixo | `app/page.tsx` |
| 8 | Aviso fixo: informação educativa, não é aconselhamento | `components/Composer.tsx` |
| 9 | Sugestões de perguntas por jornada no ecrã vazio | `app/page.tsx` |
| 10 | Funciona a 375 px, modo escuro, `aria-live` na resposta, botões com estado acessível | — |

## Modos

Botão no topo, à direita. A escolha fica guardada neste browser.

**Utilizador** — pergunta, resposta e citações (mais o aviso de dados pessoais, quando existe). É o modo da demo.

**Verboso** — tudo o que a API devolveu, por cada resposta:

- estado da API no topo: modelo, nº de chunks, embeddings ligados ou não;
- estado, jornada, nº de mensagens de histórico enviadas, guardrails ativados (`scope`) e dados pessoais tapados;
- tempos: até às fontes, até ao 1.º texto, total; nº de deltas;
- calculadoras chamadas: argumentos escolhidos pelo LLM e resultado do Python;
- chunks recuperados (ficheiro, secção, score RRF);
- fontes que foram no prompt, citadas ou não;
- o pedido enviado (JSON) e o registo de eventos SSE com tempos (deltas agrupados).

## Estrutura

```
src/
  app/page.tsx              página única: estado da conversa, jornada, perfil, modos
  lib/api.ts                tipos da API, leitura do stream SSE (fetch + reader)
  lib/chat.ts               aplica cada evento SSE ao estado de uma troca; histórico para a API
  components/Answer.tsx     markdown simples da resposta (parágrafos, listas, negrito, [n])
  components/Sources.tsx    lista de fontes citadas
  components/Inspector.tsx  painel do modo verboso
  components/ExchangeView.tsx, Composer.tsx, ProfileForm.tsx
```
