# 🏆 Caixa Explica — AInnovation Hackathon 2026 Winner

**1st place · AInnovation Hackathon · Lisbon, Portugal · 27 October 2026**

An AI-powered financial literacy assistant that helps young people in Portugal understand everyday financial decisions through **plain-language explanations, cited sources, reliable Python calculators, and privacy safeguards**.

> **Team project.** Built collaboratively by five contributors during the AInnovation Hackathon 2026.

## The challenge

Financial concepts such as credit, interest rates, taxes, budgeting, and fraud prevention can be difficult to navigate, especially for students and people entering the workforce. Caixa Explica was created to make these topics easier to understand in **European Portuguese**, while helping users check information against relevant sources.

Rather than suggesting specific financial products or making decisions on users' behalf, the assistant focuses on **education, transparency, and practical next steps**.

## What it does

- **Explains financial concepts** including TAN vs. TAEG, compound interest, salary deductions, IRS Jovem, and budgeting.
- **Supports saving and credit scenarios** with dedicated Python calculators instead of relying on the language model to perform arithmetic.
- **Retrieves supporting material** from a curated knowledge base using hybrid BM25 and semantic search, with citations in responses.
- **Recognizes sensitive information** such as tax identifiers, bank details, and passwords, and applies masking before model requests.
- **Uses guardrails** for questions that would require personalized investment advice, selecting commercial products, or actions reserved for financial institutions.
- **Guides users through follow-up questions**, clarifications, and actionable next steps.
- **Streams responses** to a responsive web interface, with clickable sources and an optional technical inspection mode.

### Example questions

> How much would I pay each month for an €8,000 car loan at 9% over 48 months?

> What's the difference between TAN and TAEG?

> I received a suspicious message asking for my banking code. What should I do?

> How can I save €600 for a trip in six months?

## Architecture

```text
Next.js / React / TypeScript UI
           |
           | HTTP + Server-Sent Events
           v
     FastAPI backend
           |
           +-- Privacy filtering and scope guardrails
           +-- Hybrid retrieval (BM25 + embeddings, RRF fusion)
           |       \-- Curated Markdown knowledge base
           +-- OpenAI language model
           +-- Python calculation tools
           |
           v
 Explanation + cited sources + calculated results
```

The knowledge base draws on financial education and institutional material, including sources from **Banco de Portugal, Autoridade Tributária, Segurança Social, BCE, CMVM, DECO**, and other relevant publishers. Not every knowledge-base entry is an official government source.

### Technology stack

| Layer | Technologies |
| --- | --- |
| Web application | Next.js 16, React 19, TypeScript, Tailwind CSS 4 |
| API | Python, FastAPI, Uvicorn |
| AI integration | OpenAI API, retrieval-augmented generation |
| Retrieval | BM25 (`rank-bm25`), Sentence Transformers, reciprocal rank fusion |
| Calculations and safety | Python tools, input validation, privacy masking, guardrails |
| Infrastructure | Docker Compose; Render and Vercel deployment configurations |
| Quality assurance | Pytest, deterministic evaluations, retrieval tests, API-based evaluation harness |

## Evaluation results

The team measured the following results **during the hackathon on 27 October 2026**. These are results from the project's recorded test suites and evaluation cases, **not production-wide accuracy guarantees**.

| Metric | Recorded result |
| --- | ---: |
| Backend automated tests | **188/188 passing** |
| Deterministic pipeline evaluations | **16/16 passing** |
| Knowledge-base retrieval cases | **24/24 passing** (target source in top 5, BM25 evaluation) |
| Responses with citations | **100%** in the recorded API evaluation |
| Invented numerical values | **0 detected** in the recorded API evaluation |
| Correct calculator selection and values | **95.2%** |
| Median time to first streamed text | **3.0 s** |

**Known limitations:** The recorded evaluation had 24 API scenarios, some combined-topic retrieval cases were not handled successfully, and some source links required further auditing. Model output varies between runs. See [`docs/METRICAS.md`](docs/METRICAS.md) for the evaluation methodology and caveats.

## Run locally

### Requirements

- Python 3 and Node.js/npm, or Docker with Docker Compose
- An OpenAI API key to use the AI-backed endpoints

### Option A — Docker Compose

1. Copy `.env.example` to `.env` in the repository root.
2. Set `OPENAI_API_KEY` in `.env`.
3. Start the stack:

```bash
docker compose up --build
```

Open the web app at **http://localhost:3000** and API docs at **http://localhost:8000/docs**.

The first launch with embeddings enabled may download an embedding model. For additional configuration and troubleshooting, refer to [`backend/README.md`](backend/README.md) and [`frontend/README.md`](frontend/README.md).

### Option B — Separate development servers

**Backend:**

```bash
cd backend
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip install pytest
.venv/bin/python -m uvicorn api:app --reload --port 8000
```

**Frontend (in another terminal):**

```bash
cd frontend
npm install
npm run dev
```

Configure the environment variables described in the component READMEs before starting the services.

### Tests

From the repository root, with the backend virtual environment and `pytest` installed:

```bash
cd backend
.venv/bin/python -m pytest -q tests
cd ..
backend/.venv/bin/python scripts/avaliar_pipeline.py
backend/.venv/bin/python scripts/avaliar_kb.py
```

The end-to-end evaluation harness requires the running API and model access; see [`docs/HARNESS.md`](docs/HARNESS.md).

## Responsible use

Caixa Explica is an **educational prototype**, not financial, legal, investment, or tax advice. It does not apply for benefits, file tax returns, renegotiate contracts, or recommend particular financial products. Financial rules and rates can change, and cited materials may be incomplete or outdated. Verify important details with the relevant institutions before acting.

## Team and acknowledgements

Created collaboratively by **Group 2**, a five-person team at the **AInnovation Hackathon 2026**.

- **João** — [GitHub profile](https://github.com/joaorodrigues0764)
- **Lamy** — [GitHub profile](https://github.com/luislamy)
- **Aless** — [GitHub profile](https://github.com/AlessSaints)
- **Guilherme** — [GitHub profile](https://github.com/Guigs13)
- **Simone** — [GitHub profile](https://github.com/simonedossantos-ship-it)


## Hackathon

**Award:** 1st place, AInnovation Hackathon 2026 — Lisbon, Portugal, 27 October 2026.

The team presented the problem, system design, live demonstration, technical implementation, evaluation results, and responsible-use limitations.

---

*Built as a team. Presented with pride. Designed to make financial education more accessible.*
