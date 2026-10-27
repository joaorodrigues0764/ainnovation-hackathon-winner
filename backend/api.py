"""
Caixa Explica — API (FastAPI) por cima do RAG.

Correr (a partir de backend/):
    uvicorn api:app --reload --port 8000

Endpoints:
    GET  /health        estado do índice e do modelo
    GET  /journeys      jornadas disponíveis
    POST /chat          resposta completa em JSON
    POST /chat/stream   a mesma resposta em Server-Sent Events

Eventos de /chat/stream (cada um com `data:` em JSON):
    warning  {text, pii}              só se a mensagem tinha dados pessoais (foram mascarados)
    sources  {sources, chunks, scope} fontes recuperadas, antes do texto; scope = guardrails ativados
    tool     {name, args, result}     uma calculadora correu (os números do cartão de resposta)
    delta    {text}                   pedaço da resposta
    done     {answer, sources}        resposta final + só as fontes citadas
    error    {detail}                 falhou a meio; o stream termina

O servidor não guarda conversa: o front envia o histórico em `history` a cada pedido.
"""
from __future__ import annotations

import json
import os
import re
import sys
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field

from guardrails import check_scope
from privacy import mask_pii
from rag import JOURNEYS, LLM_MODEL, RAG
from tools import SCHEMAS, run_tool

KB_DIR = os.getenv("KB_DIR", str(Path(__file__).resolve().parent / "kb"))
USE_EMBEDDINGS = os.getenv("USE_EMBEDDINGS", "1") != "0"
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")]
MAX_HISTORY = 12  # mensagens (≈ 6 trocas) que seguem para o LLM

JOURNEY_LABELS = {
    "credito": "Primeiro crédito",
    "salario": "Primeiro salário",
    "irs": "Primeiro IRS",
    "burlas": "Burlas e segurança",
    "poupanca": "Poupar para um objetivo",
    "geral": "Geral",
}

_CITE = re.compile(r" ?\[\d+\]")

PII_LABELS = {
    "IBAN": "IBAN", "NIB": "NIB", "CARTAO": "número de cartão", "CODIGO": "código ou PIN",
    "EMAIL": "email", "NIF_OU_TELEMOVEL": "NIF ou telemóvel",
}


# ---------------------------------------------------------------- modelos

class Profile(BaseModel):
    model_config = ConfigDict(extra="forbid")  # só estes campos; nada de NIF/IBAN no perfil

    idade: int | None = Field(None, ge=14, le=100)
    rendimento_liquido: float | None = Field(None, ge=0, description="€ líquidos por mês")
    objetivo: str | None = Field(None, max_length=200)


class Turn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    journey: Literal[JOURNEYS] | None = None
    profile: Profile | None = None
    history: list[Turn] = Field(default_factory=list, max_length=40,
                                description="mensagens anteriores, da mais antiga para a mais recente")


class Source(BaseModel):
    n: int
    title: str
    url: str
    source: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    chunks: list[dict]
    tools: list[dict] = []
    scope: list[str] = []
    warning: str | None = None


# ---------------------------------------------------------------- preparação do pedido

@dataclass
class Prepared:
    question: str
    profile: dict | None
    history: list[dict]
    pii: list[str]
    scope: list[str]
    referrals: list[dict]
    instructions: list[str]

    @property
    def warning(self) -> str | None:
        if not self.pii:
            return None
        return (f"Atenção: a tua mensagem tinha dados pessoais ({', '.join(self.pii)}). "
                "Não partilhes NIF, IBAN, números de cartão, códigos ou palavras-passe aqui. "
                "Tapei-os antes de responder e não os guardo.")

    def rag_kwargs(self, req: ChatRequest) -> dict:
        return {"journey": req.journey, "profile": self.profile, "history": self.history,
                "referrals": self.referrals, "instructions": self.instructions,
                "tools": SCHEMAS, "run_tool": run_tool}  # RF2: as contas são das calculadoras


def prepare(req: ChatRequest) -> Prepared:
    """Mascara dados pessoais (UC-04) em tudo o que vai para o LLM e aplica os guardrails."""
    found: dict[str, int] = {}

    def mask(text: str) -> str:
        r = mask_pii(text)
        for k, v in r.found.items():
            found[k] = found.get(k, 0) + v
        return r.text

    question = mask(req.question)
    profile = req.profile.model_dump(exclude_none=True) if req.profile else {}
    if "objetivo" in profile:
        profile["objetivo"] = mask(profile["objetivo"])
    # só a pergunta atual conta para o aviso; o histórico já foi avisado na sua vez
    pii = [PII_LABELS.get(k, k) for k in found]
    # as citações [n] de respostas antigas apontam para outra numeração de fontes: tirá-las
    # evita que o LLM as copie para a resposta nova (citações que não levam a lado nenhum)
    history = [{"role": t.role, "content": _CITE.sub("", mask_pii(t.content).text)}
               for t in req.history[-MAX_HISTORY:]]

    hits = check_scope(question)
    referrals = list({r["url"]: r for h in hits for r in h.referrals}.values())
    return Prepared(question, profile or None, history, pii, [h.kind for h in hits],
                    referrals, [h.instruction for h in hits])


# ---------------------------------------------------------------- app

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.rag = RAG(KB_DIR, use_embeddings=USE_EMBEDDINGS)  # uma vez, no arranque
    yield


app = FastAPI(title="Caixa Explica API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


def _rag(request: Request) -> RAG:
    return request.app.state.rag


@app.get("/health")
def health(request: Request):
    rag = _rag(request)
    return {"status": "ok", "chunks": len(rag.chunks),
            "embeddings": rag.vecs is not None, "model": LLM_MODEL}


@app.get("/journeys")
def journeys():
    return [{"id": j, "label": JOURNEY_LABELS[j]} for j in JOURNEYS]


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, request: Request):
    p = prepare(req)
    try:
        out = _rag(request).answer(p.question, **p.rag_kwargs(req))
    except RuntimeError as e:  # configuração (ex.: falta a chave)
        raise HTTPException(503, str(e))
    except Exception as e:
        print(f"[api] erro no LLM: {e!r}", file=sys.stderr)
        raise HTTPException(502, "O modelo não respondeu. Tenta outra vez.")
    return {**out, "scope": p.scope, "warning": p.warning}


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@app.post("/chat/stream")
def chat_stream(req: ChatRequest, request: Request):
    p = prepare(req)
    rag = _rag(request)

    def events() -> Iterator[str]:
        if p.warning:
            yield _sse("warning", {"text": p.warning, "pii": p.pii})
        try:
            for ev in rag.stream_answer(p.question, **p.rag_kwargs(req)):
                kind = ev.pop("type")
                if kind == "sources":
                    ev["scope"] = p.scope
                yield _sse(kind, ev)
        except RuntimeError as e:
            yield _sse("error", {"detail": str(e)})
        except Exception as e:
            print(f"[api] erro no stream: {e!r}", file=sys.stderr)
            yield _sse("error", {"detail": "O modelo não respondeu. Tenta outra vez."})

    return StreamingResponse(events(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
