# Deploy: API no Render, front no Vercel

**API de produção:** https://caixa-explica-api.onrender.com ([`/health`](https://caixa-explica-api.onrender.com/health)). É o valor por omissão do build de produção do front (`frontend/.env.production`).

```
browser ──► Vercel (frontend/, Next.js) ──fetch/SSE──► Render (backend/, Docker) ──► OpenAI
```

A chave da OpenAI fica **só no Render**. O Vercel só sabe o endereço público da API.

## 1. API no Render (primeiro, porque o front precisa do URL dela)

1. Em [render.com](https://render.com), entrar com o GitHub e dar acesso ao repo `luislamy/ainnovation-hackathon-2026`.
2. **New → Blueprint** → escolher o repo. O Render lê o [`render.yaml`](../render.yaml) da raiz e cria o serviço `caixa-explica-api` (Docker, `backend/Dockerfile`, Frankfurt, health check em `/health`).
3. Preencher os valores pedidos no ecrã:

   | Variável | Valor |
   | --- | --- |
   | `OPENAI_API_KEY` | a chave (fica só aqui) |
   | `OPENAI_MODEL` | o modelo da equipa (ex.: `gpt-6-luna`) |
   | `OPENAI_REASONING_EFFORT` | `none` para o `gpt-6-luna`; vazio para o `gpt-4o-mini` |
   | `CORS_ORIGINS` | por agora `http://localhost:3000`; no passo 3 passa a ser o URL do Vercel |
   | `CORS_ORIGIN_REGEX` | vazio por agora; no passo 3, ex.: `https://caixa-explica-.*\.vercel\.app` |

   Já vêm definidos no `render.yaml`: `EMBEDDINGS=0` e `USE_EMBEDDINGS=0` (só BM25), `RATE_LIMIT_PER_MIN=10` por IP, `DAILY_LIMIT=500` perguntas por dia, `JUDGE=1`.
4. **Apply**. O 1.º build demora uns minutos. No fim, abrir https://caixa-explica-api.onrender.com/health: deve devolver `{"status":"ok", ...}`.

**Embeddings no Render:** o plano free tem 512 MB de memória e o torch não cabe, por isso vai só com BM25 (a pesquisa por palavras passa 24/24 no `scripts/avaliar_kb.py`). Com um plano pago de 2 GB ou mais, pôr `EMBEDDINGS=1` e `USE_EMBEDDINGS=1` e fazer **Manual Deploy → Clear build cache & deploy**.

**O plano free adormece** depois de 15 min sem pedidos e o 1.º pedido seguinte demora ~1 min. Antes da demo, abrir o `/health` uns minutos antes (ou usar o plano Starter).

## 2. Front no Vercel

1. Em [vercel.com](https://vercel.com), entrar com o GitHub → **Add New → Project** → importar `luislamy/ainnovation-hackathon-2026`.
2. **Root Directory: `frontend`** (botão *Edit* ao lado). O Vercel deteta Next.js; não mudar comandos de build.
3. **Environment Variables**: opcional. Sem nada, o build usa `frontend/.env.production` (`https://caixa-explica-api.onrender.com`). Para apontar para outra API, definir `NEXT_PUBLIC_API_URL` (sem `/` no fim), que tem prioridade sobre o ficheiro.
4. **Deploy**. No fim fica um URL do tipo `https://caixa-explica.vercel.app`.

`NEXT_PUBLIC_API_URL` é gravada no build: se o URL da API mudar, é preciso **Redeploy** no Vercel.

## 3. Ligar os dois (CORS)

No Render → serviço → **Environment**:

- `CORS_ORIGINS` = `https://caixa-explica.vercel.app` (o domínio de produção que o Vercel deu; vários separados por vírgulas, pode manter `http://localhost:3000`)
- `CORS_ORIGIN_REGEX` = `https://caixa-explica-.*\.vercel\.app` para os previews (o Vercel cria um URL novo por cada push/PR; ajustar ao nome do projeto)

Guardar: o Render reinicia o serviço sozinho.

## 4. Verificar

1. Abrir o URL do Vercel, escolher "Primeiro crédito" e clicar na sugestão do carro: deve aparecer o cartão com **199,08 €/mês**.
2. Mudar para **Verboso**: no topo deve aparecer `<modelo> · <n> chunks · emb off`.
3. Se aparecer "Não consigo falar com a API": ver no browser (F12 → Console) se é erro de CORS (falta o domínio no passo 3) ou se a API está a dormir (abrir o `/health` e esperar).
4. Opcional: correr o harness contra a API pública (gasta tokens e conta para o limite diário):

   ```powershell
   backend\.venv\Scripts\python scripts\harness.py --api https://caixa-explica-api.onrender.com
   ```

## Custos e segurança

- A API é pública: qualquer pessoa com o URL pode fazer perguntas, e cada uma gasta tokens da chave. Os limites (`RATE_LIMIT_PER_MIN`, `DAILY_LIMIT`) travam abusos, mas **pôr também um limite de gastos na conta da OpenAI**.
- O limite é em memória: reinicia quando o serviço reinicia ou adormece. Chega para uma demo, não para produção.
- Depois do hackathon, apagar o serviço no Render ou trocar a chave.
