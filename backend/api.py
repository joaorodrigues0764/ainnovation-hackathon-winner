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
    warning  {text, pii}            só se a pergunta tinha dados pessoais (foram removidos)
    sources  {sources, chunks}      fontes recuperadas, antes do texto
    delta    {text}                 pedaço da resposta
    done     {answer, sources}      resposta final + só as fontes citadas
    error    {detail}               falhou a meio; o stream termina
"""
from __future__ import annotations

import json
import os
import re
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Iterator, Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field

from rag import JOURNEYS, LLM_MODEL, RAG

KB_DIR = os.getenv("KB_DIR", str(Path(__file__).resolve().parent / "kb"))
USE_EMBEDDINGS = os.getenv("USE_EMBEDDINGS", "1") != "0"
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")]

JOURNEY_LABELS = {
    "credito": "Primeiro crédito",
    "salario": "Primeiro salário",
    "irs": "Primeiro IRS",
    "burlas": "Burlas e segurança",
    "poupanca": "Poupar para um objetivo",
    "geral": "Geral",
}


# ---------------------------------------------------------------- dados pessoais (UC-04)

# Ordem importa: o IBAN sai primeiro para os dígitos dele não contarem como cartão/NIF.
PII_PATTERNS = [
    ("IBAN", re.compile(r"\b[A-Z]{2}\d{2}(?: ?[A-Z0-9]{4}){3,7}(?: ?[A-Z0-9]{1,3})?\b", re.I)),
    ("número de cartão", re.compile(r"(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)")),
    ("NIF ou telefone", re.compile(r"(?<!\d)\d{3} ?\d{3} ?\d{3}(?!\d)")),
]


def redact_pii(text: str) -> tuple[str, list[str]]:
    """Troca NIF/IBAN/cartão por marcadores. O texto original nunca chega ao LLM."""
    found = []
    for label, pattern in PII_PATTERNS:
        text, n = pattern.subn(f"[{label} removido]", text)
        if n:
            found.append(label)
    return text, found


def pii_warning(found: list[str]) -> str:
    return (f"Atenção: a tua mensagem tinha dados pessoais ({', '.join(found)}). "
            "Não partilhes NIF, IBAN, números de cartão ou palavras-passe aqui. "
            "Removi-os antes de responder e não os guardo.")


# ---------------------------------------------------------------- modelos

class Profile(BaseModel):
    model_config = ConfigDict(extra="forbid")  # só estes campos; nada de NIF/IBAN no perfil

    idade: int | None = Field(None, ge=14, le=100)
    rendimento_liquido: float | None = Field(None, ge=0, description="€ líquidos por mês")
    objetivo: str | None = Field(None, max_length=200)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    journey: Literal[JOURNEYS] | None = None
    profile: Profile | None = None


class Source(BaseModel):
    n: int
    title: str
    url: str
    source: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    chunks: list[dict]
    warning: str | None = None


def prepare(req: ChatRequest) -> tuple[str, dict | None, list[str]]:
    question, found = redact_pii(req.question)
    profile = req.profile.model_dump(exclude_none=True) if req.profile else None
    if profile and "objetivo" in profile:
        profile["objetivo"], found_obj = redact_pii(profile["objetivo"])
        found += [f for f in found_obj if f not in found]
    return question, profile or None, found


def calcular(req: ChatRequest, profile: dict | None) -> dict | None:
    """Ligar aqui as calculadoras (RF2): devolve os números que o LLM pode usar."""
    return None


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
    question, profile, found = prepare(req)
    try:
        out = _rag(request).answer(question, journey=req.journey, profile=profile,
                                   tool_results=calcular(req, profile))
    except RuntimeError as e:  # configuração (ex.: falta a chave)
        raise HTTPException(503, str(e))
    except Exception as e:
        print(f"[api] erro no LLM: {e!r}", file=sys.stderr)
        raise HTTPException(502, "O modelo não respondeu. Tenta outra vez.")
    return {**out, "warning": pii_warning(found) if found else None}


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@app.post("/chat/stream")
def chat_stream(req: ChatRequest, request: Request):
    question, profile, found = prepare(req)
    rag = _rag(request)

    def events() -> Iterator[str]:
        if found:
            yield _sse("warning", {"text": pii_warning(found), "pii": found})
        try:
            for ev in rag.stream_answer(question, journey=req.journey, profile=profile,
                                        tool_results=calcular(req, profile)):
                yield _sse(ev.pop("type"), ev)
        except RuntimeError as e:
            yield _sse("error", {"detail": str(e)})
        except Exception as e:
            print(f"[api] erro no stream: {e!r}", file=sys.stderr)
            yield _sse("error", {"detail": "O modelo não respondeu. Tenta outra vez."})

    return StreamingResponse(events(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
