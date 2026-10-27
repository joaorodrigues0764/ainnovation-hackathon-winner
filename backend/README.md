# Caixa Explica — RAG pipeline

Pipeline: `kb/*.md` → chunks por secção `##` → BM25 + embeddings (multilingual-e5-small) → fusão RRF → prompt com fontes numeradas → OpenAI → resposta citada.

## Setup (PowerShell)

Todos os comandos correm a partir de `backend/` (o default de `--kb` é `kb`, relativo à pasta atual).

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item ..\.env.example ..\.env   # depois abrir ..\.env e colar a OPENAI_API_KEY
```

O `rag.py` lê o `.env` da raiz do repo (que está no `.gitignore`). Uma variável já definida no terminal (`$env:OPENAI_API_KEY`) tem prioridade sobre o `.env`.

## Testar

```powershell
# só retrieval (não gasta tokens)
python rag.py "Qual a diferença entre TAEG e TAN?" --retrieve-only

# resposta completa
python rag.py "Vale a pena pedir crédito para um carro?" --journey credito

# sem embeddings (se o download do modelo falhar na rede do evento)
python rag.py "O IRS Jovem aplica-se a mim?" --no-embeddings
```

Na primeira execução o sentence-transformers descarrega o modelo de embeddings (~470 MB). Façam isto já, enquanto a rede aguenta.

## API (FastAPI)

```powershell
uvicorn api:app --reload --port 8000   # docs interativas em http://localhost:8000/docs
```

| Método | Rota | O que faz |
| --- | --- | --- |
| GET | `/health` | n.º de chunks, embeddings ligados, modelo |
| GET | `/journeys` | `[{id, label}]` para o ecrã de escolha de jornada |
| POST | `/chat` | resposta completa em JSON: `{answer, sources, chunks, warning}` |
| POST | `/chat/stream` | a mesma resposta em Server-Sent Events |

Corpo dos dois `POST`:

```json
{"question": "Vale a pena pedir crédito para o carro?",
 "journey": "credito",
 "profile": {"idade": 23, "rendimento_liquido": 1100, "objetivo": "carro de 8000 €"}}
```

`journey` e `profile` são opcionais. O perfil só aceita estes três campos.

Eventos de `/chat/stream`, por esta ordem:

| Evento | `data` | Quando |
| --- | --- | --- |
| `warning` | `{text, pii}` | só se a pergunta tinha NIF/IBAN/cartão (já removidos) |
| `sources` | `{sources, chunks}` | antes do texto, para o front mostrar as fontes cedo |
| `delta` | `{text}` | cada pedaço da resposta |
| `done` | `{answer, sources}` | fim; `sources` = só as citadas |
| `error` | `{detail}` | falhou a meio; o stream termina |

O `EventSource` do browser só faz `GET`, por isso no Next.js lê-se o stream com `fetch` e `response.body.getReader()`.

Testar o stream no terminal:

```powershell
curl.exe -N -X POST http://localhost:8000/chat/stream -H "Content-Type: application/json" -d '{\"question\": \"O que e a TAEG?\", \"journey\": \"credito\"}'
```

**Dados pessoais (UC-04):** NIF, IBAN e números de cartão são trocados por marcadores *antes* de a pergunta ir para a OpenAI, e a resposta começa com um aviso.

**Calculadoras (RF2):** ligam-se em `calcular()` no `api.py`. O cliente não pode enviar números; só a API os passa ao LLM.

Variáveis opcionais no `.env`: `KB_DIR`, `USE_EMBEDDINGS=0` (só BM25, arranque rápido), `CORS_ORIGINS` (por omissão `http://localhost:3000`, separar várias por vírgulas).

## Usar o RAG diretamente em Python

```python
from rag import RAG
rag = RAG("kb")   # no startup, uma vez

out = rag.answer(
    question,
    journey="credito",                       # credito | salario | irs | burlas | poupanca | geral | None
    profile={"idade": 23, "rendimento_liquido": 1100},
    tool_results={"prestacao_mensal": 165.2}, # números das calculadoras
)
# out["answer"]  -> texto com citações [n]
# out["sources"] -> [{n, title, url, source}] só das fontes citadas
# out["chunks"]  -> chunks recuperados + score (para debug / harness)
```

## Knowledge base (equipa 2)

Formato em [`docs/KB_CONTRACT.md`](../docs/KB_CONTRACT.md). Basta largar `.md` novos em `kb/` e reiniciar o servidor.

## Próximos passos (harness)

- Conjunto de perguntas de teste com o ficheiro esperado → medir hit@5 do retrieval.
- Variantes no quadro (query rewriting, HyDE): acrescentar como passo antes de `retrieve()` e comparar com o mesmo conjunto.
