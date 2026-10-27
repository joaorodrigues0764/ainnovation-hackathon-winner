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
| POST | `/chat` | resposta completa em JSON: `{answer, sources, chunks, tools, scope, warning}` |
| POST | `/chat/stream` | a mesma resposta em Server-Sent Events |

Corpo dos dois `POST`:

```json
{"question": "e se for a 60 meses?",
 "journey": "credito",
 "profile": {"idade": 23, "rendimento_liquido": 1100, "objetivo": "carro de 8000 €"},
 "history": [{"role": "user", "content": "Vale a pena pedir crédito para o carro?"},
             {"role": "assistant", "content": "…resposta anterior…"}]}
```

Só `question` é obrigatório. O perfil só aceita estes três campos.

**Histórico:** o servidor não guarda conversa (o perfil e as mensagens ficam só na sessão do browser). O front envia em `history` as mensagens anteriores, da mais antiga para a mais recente, a cada pedido; seguem para o LLM as últimas 12. A última pergunta do utilizador também entra na pesquisa, para follow-ups curtos como "e a 60 meses?" encontrarem as fontes certas.

Eventos de `/chat/stream`, por esta ordem:

| Evento | `data` | Quando |
| --- | --- | --- |
| `warning` | `{text, pii}` | só se a pergunta tinha dados pessoais (já tapados) |
| `sources` | `{sources, chunks, scope}` | antes do texto, para o front mostrar as fontes cedo; `scope` = guardrails ativados |
| `tool` | `{name, args, result}` | uma calculadora correu; `result` tem os números para o cartão de resposta (pode haver vários) |
| `delta` | `{text}` | cada pedaço da resposta |
| `done` | `{answer, sources}` | fim; `sources` = só as citadas |
| `error` | `{detail}` | falhou a meio; o stream termina |

O `EventSource` do browser só faz `GET`, por isso no Next.js lê-se o stream com `fetch` e `response.body.getReader()`.

Testar o stream no terminal:

```powershell
curl.exe -N -X POST http://localhost:8000/chat/stream -H "Content-Type: application/json" -d '{\"question\": \"O que e a TAEG?\", \"journey\": \"credito\"}'
```

**Dados pessoais (UC-04):** `privacy.py` tapa IBAN, NIB, cartões (com Luhn), NIF/telemóvel, emails e códigos/PIN na pergunta, no histórico e no perfil, *antes* de irem para a OpenAI. Se a pergunta atual tinha algum, a resposta começa com o evento `warning`.

**Guardrails de âmbito (Bloco 3):** `guardrails.py` deteta, sem LLM, três casos e acrescenta ao prompt uma instrução e a entidade oficial para onde reencaminhar (citável como fonte):

| `scope` | Exemplo | Reencaminha para |
| --- | --- | --- |
| `investimento` | "melhores ações?", "devo comprar Bitcoin?" | CMVM |
| `acao_externa` | "podes renegociar o crédito / tratar do meu IRS?" | Banco de Portugal, DECO, Portal das Finanças |
| `produto` | "qual o melhor banco?", "que cartão me recomendas?" | comparadores do Portal do Cliente Bancário |

**Calculadoras (RF2), com tool calling:** `tools.py` expõe as funções de `calculators.py` ao LLM (`custo_credito`, `objetivo_poupanca`, `juros_compostos`, `orcamento`, `salario_liquido`, `efeito_inflacao`). O LLM escolhe a função e os argumentos a partir da pergunta, do perfil e do histórico; a conta é feita em Python e o resultado volta ao LLM, que só o explica. Se faltar um valor (ex.: a taxa), o LLM pergunta-o em vez de o inventar. Argumentos inválidos voltam ao LLM como `{"erro": ...}`. No máximo 2 voltas de calculadoras por resposta. O cliente não pode enviar números.

Exemplo de evento `tool` para "e se for a 60 meses?":

```json
{"name": "custo_credito",
 "args": {"montante": 8000, "taxa_anual_nominal": 9, "prestacoes": 60},
 "result": {"prestacao_mensal": 166.07, "total_a_pagar": 9964.01, "juros": 1964.01, "pressupostos": "..."}}
```

**Modelos diferentes:** se o modelo recusar um parâmetro (`temperature`, ou tools sem `reasoning_effort="none"`, como o `gpt-6-luna`), o pipeline ajusta-o sozinho no 1.º pedido. Para evitar essa repetição, pode pôr-se `OPENAI_REASONING_EFFORT=none` no `.env`.

Testes (não gastam tokens, o LLM é falso):

```powershell
pip install pytest
python -m pytest -q tests
```

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
