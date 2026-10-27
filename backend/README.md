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

## Interface para a FastAPI (equipa 3)

```python
from rag import RAG
rag = RAG("kb")   # no startup, uma vez

out = rag.answer(
    question,
    journey="credito",                       # credito | salario | irs | geral | None
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
