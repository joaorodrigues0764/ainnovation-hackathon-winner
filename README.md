# AInnovation Hackathon 2026 — Assistente de literacia financeira para jovens

Agente conversacional em PT-PT que ajuda jovens (14–25) a fazer orçamento, poupar para objetivos, perceber juros e crédito e reconhecer burlas. As contas são feitas por ferramentas testadas; o modelo explica. Educa, não recomenda produtos.

## Como correr
1. API (RAG + calculadoras) em `backend/`: setup e testes em [`backend/README.md`](backend/README.md) → `http://localhost:8000`.
2. Front-end Next.js em `frontend/`: [`frontend/README.md`](frontend/README.md) → `http://localhost:3000` (modos Utilizador e Verboso).

### Com Docker (API + front de uma vez)

Precisa do Docker Desktop a correr e de um `.env` na raiz (copiar `.env.example` e pôr a `OPENAI_API_KEY`).

```powershell
docker compose up --build
```

- Front: http://localhost:3000 · API: http://localhost:8000/docs
- O front só arranca quando a API responde ao `/health`.
- Com embeddings (por omissão), o 1.º arranque descarrega o modelo (~470 MB) para o volume `hf-cache`; os seguintes já não.
- Rede fraca ou pressa: `$env:EMBEDDINGS="0"; docker compose up --build` (só BM25, imagem muito mais pequena).
- A chave **não** vai para a imagem: o `.env` está no `.dockerignore` e só entra no contentor ao arrancar (`env_file`).
- Parar: `Ctrl+C` ou `docker compose down`.

## Equipa
luislamy · Aless

## Documentação
- `CLAUDE.md` — regras de trabalho com Claude neste repo
- `docs/PLANO_HACKATHON.md` — plano, âmbito, demo
- `docs/AVALIACAO.md` — casos de teste do agente
- `docs/KB_CONTRACT.md` — formato dos ficheiros da knowledge base (`backend/kb/`)

## Depois do hackathon
(ideias que ficaram de fora)
