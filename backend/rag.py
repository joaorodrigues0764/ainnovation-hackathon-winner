"""
Caixa Explica — RAG pipeline (naive + hybrid).

Fluxo: kb/*.md -> chunks por secção -> índice híbrido (BM25 + embeddings) ->
retrieve com RRF -> prompt com fontes numeradas -> LLM OpenAI -> resposta citada.

Uso rápido:
    python rag.py "Vale a pena pedir crédito para um carro?"
    python rag.py "O IRS Jovem aplica-se a mim?" --journey irs

Para a FastAPI (equipa 3):
    from rag import RAG
    rag = RAG("kb")                      # constrói o índice uma vez no arranque
    out = rag.answer(question, journey="credito", profile={...}, tool_results={...})
    # out = {"answer": str, "sources": [{"n", "title", "url", "source"}], "chunks": [...]}
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

import numpy as np
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi

# .env na raiz do repo (fora do git); variáveis já definidas no ambiente têm prioridade
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

EMBED_MODEL = os.getenv("EMBED_MODEL", "intfloat/multilingual-e5-small")
LLM_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # mudar para o modelo que a equipa usar
JOURNEYS = ("credito", "salario", "irs", "burlas", "poupanca", "geral")  # = docs/KB_CONTRACT.md
NO_SOURCES_ANSWER = "Não encontrei informação nas fontes para responder a isto."
MAX_CHARS = 1200
TOP_K = 5
RRF_K = 60

SYSTEM_PROMPT = """És o Caixa Explica, um assistente de literacia financeira para jovens em Portugal.
Regras:
1. Responde apenas com base nas FONTES fornecidas. Cada afirmação factual termina com a citação [n].
2. Se as fontes não chegam para responder, diz que não sabes e indica onde procurar. Não inventes.
3. Não faças contas. Só podes usar números que estejam nas FONTES ou em RESULTADOS DE CÁLCULO.
4. Não recomendes produtos nem bancos específicos. É informação educativa, não aconselhamento.
5. Português de Portugal, frases curtas, explica termos técnicos (TAEG, TAN) na primeira vez.
6. Estrutura: resposta direta (1-2 frases) -> explicação (até 3 frases) -> "Próximo passo:" com uma ação concreta."""


# ---------------------------------------------------------------- KB loading

@dataclass
class Chunk:
    id: int
    text: str
    title: str
    section: str
    url: str
    source: str
    journey: str
    file: str
    meta: dict = field(default_factory=dict)


def _parse_front_matter(raw: str) -> tuple[dict, str]:
    meta: dict = {}
    if raw.startswith("---"):
        end = raw.find("\n---", 3)
        if end != -1:
            for line in raw[3:end].strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
            raw = raw[end + 4:]
    return meta, raw.strip()


def _split_sections(body: str) -> list[tuple[str, str]]:
    """Divide por headings ## / ###. Texto antes do 1.º heading fica na secção ''."""
    parts = re.split(r"^(#{2,3} .+)$", body, flags=re.M)
    sections, current = [], ""
    if parts[0].strip():
        sections.append(("", parts[0].strip()))
    for piece in parts[1:]:
        if re.match(r"^#{2,3} ", piece):
            current = piece.lstrip("#").strip()
        elif piece.strip():
            sections.append((current, piece.strip()))
    return sections


def _split_long(text: str, max_chars: int = MAX_CHARS) -> list[str]:
    """Agrupa parágrafos até max_chars, com o último parágrafo como overlap."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    out, buf = [], []
    for p in paras:
        if buf and sum(len(x) for x in buf) + len(p) > max_chars:
            out.append("\n\n".join(buf))
            buf = [buf[-1]] if len(buf[-1]) < max_chars // 2 else []
        buf.append(p)
    if buf:
        out.append("\n\n".join(buf))
    return out


def load_kb(kb_dir: str | Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    files = sorted(Path(kb_dir).glob("**/*.md"))
    if not files:
        raise FileNotFoundError(f"Sem ficheiros .md em {kb_dir}")
    for f in files:
        meta, body = _parse_front_matter(f.read_text(encoding="utf-8"))
        title = meta.get("title", f.stem)
        for section, text in _split_sections(body):
            for piece in _split_long(text):
                header = f"{title} — {section}" if section else title
                chunks.append(Chunk(
                    id=len(chunks),
                    text=f"{header}\n{piece}",
                    title=title,
                    section=section,
                    url=meta.get("url", ""),
                    source=meta.get("source", ""),
                    journey=meta.get("journey", "geral").lower(),
                    file=f.name,
                    meta=meta,
                ))
    return chunks


# ---------------------------------------------------------------- indexing

def _normalize(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


STOPWORDS = set(_normalize(
    "a o as os um uma uns umas de do da dos das em no na nos nas por para com sem "
    "e ou mas que se ao aos a as e é sao ser ter tem mais menos muito qual quais "
    "como quando onde porque isto isso este esta esse essa me mim eu tu ele ela "
    "nao sim ja so ate entre sobre pelo pela pelos pelas seu sua seus suas meu minha "
    "vale pena fazer devo posso"
).split())


def _tokenize(s: str) -> list[str]:
    return [t for t in re.findall(r"\w+", _normalize(s)) if t not in STOPWORDS]


class Embedder:
    """sentence-transformers; e5 precisa dos prefixos 'query: ' e 'passage: '."""

    def __init__(self, model_name: str = EMBED_MODEL):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)
        self.e5 = "e5" in model_name.lower()

    def docs(self, texts: list[str]) -> np.ndarray:
        texts = [f"passage: {t}" for t in texts] if self.e5 else texts
        return self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)

    def query(self, text: str) -> np.ndarray:
        text = f"query: {text}" if self.e5 else text
        return self.model.encode([text], normalize_embeddings=True)[0]


class RAG:
    def __init__(self, kb_dir: str | Path = "kb", use_embeddings: bool = True):
        self.chunks = load_kb(kb_dir)
        tokenized = [_tokenize(c.text) for c in self.chunks]
        self.bm25 = BM25Okapi(tokenized)
        self._token_sets = [set(t) for t in tokenized]
        self.embedder, self.vecs = None, None
        if use_embeddings:
            try:
                self.embedder = Embedder()
                self.vecs = self.embedder.docs([c.text for c in self.chunks])
            except Exception as e:  # sem rede/modelo: continua só com BM25
                print(f"[rag] embeddings desligados ({e}); a usar só BM25", file=sys.stderr)
        self._llm = None
        self._temperature: float | None = 0.1

    # ---- retrieval

    def retrieve(self, query: str, k: int = TOP_K, journey: str | None = None) -> list[dict]:
        allowed = np.array([
            journey is None or c.journey in (journey, "geral") for c in self.chunks
        ])
        rankings = []

        q_tokens = _tokenize(query)
        bm = np.array(self.bm25.get_scores(q_tokens))
        overlap = np.array([bool(set(q_tokens) & toks) for toks in self._token_sets])
        bm[~allowed | ~overlap] = -np.inf
        order = np.argsort(-bm)
        rankings.append(order[np.isfinite(bm[order])])  # só chunks com termos em comum

        if self.vecs is not None:
            sim = self.vecs @ self.embedder.query(query)
            sim[~allowed] = -np.inf
            rankings.append(np.argsort(-sim))

        # Reciprocal Rank Fusion
        fused: dict[int, float] = {}
        for ranking in rankings:
            for rank, idx in enumerate(ranking[: k * 4]):
                if allowed[idx]:
                    fused[int(idx)] = fused.get(int(idx), 0.0) + 1.0 / (RRF_K + rank + 1)

        top = sorted(fused.items(), key=lambda x: -x[1])[:k]
        return [{"chunk": self.chunks[i], "score": round(s, 4)} for i, s in top]

    # ---- generation

    def _client(self):
        if self._llm is None:
            from openai import OpenAI
            if not os.getenv("OPENAI_API_KEY"):
                raise RuntimeError("Falta OPENAI_API_KEY: copiar .env.example para .env na raiz do repo e preencher")
            self._llm = OpenAI()  # lê OPENAI_API_KEY do ambiente
        return self._llm

    @staticmethod
    def build_prompt(question: str, hits: list[dict], profile: dict | None,
                     tool_results: dict | None) -> tuple[str, list[dict]]:
        # numerar por documento (url), não por chunk, para citações limpas
        sources, by_url, blocks = [], {}, []
        for h in hits:
            c: Chunk = h["chunk"]
            key = c.url or c.file
            if key not in by_url:
                by_url[key] = len(sources) + 1
                sources.append({"n": by_url[key], "title": c.title, "url": c.url, "source": c.source})
            blocks.append(f"[{by_url[key]}] {c.text}")

        parts = ["FONTES:\n" + "\n\n".join(blocks)]
        if profile:
            parts.append("PERFIL DO UTILIZADOR:\n" + json.dumps(profile, ensure_ascii=False))
        if tool_results:
            parts.append("RESULTADOS DE CÁLCULO (usar estes números tal como estão):\n"
                         + json.dumps(tool_results, ensure_ascii=False))
        parts.append(f"PERGUNTA:\n{question}")
        return "\n\n".join(parts), sources

    def _complete(self, user_msg: str, stream: bool = False):
        messages = [{"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg}]
        kwargs = {"model": LLM_MODEL, "messages": messages, "stream": stream}
        if self._temperature is not None:
            try:
                return self._client().chat.completions.create(temperature=self._temperature, **kwargs)
            except Exception as e:  # alguns modelos (ex.: de raciocínio) só aceitam a temperatura por omissão
                if "temperature" not in str(e):
                    raise
                print(f"[rag] {LLM_MODEL} não aceita temperature; a usar a por omissão", file=sys.stderr)
                self._temperature = None
        return self._client().chat.completions.create(**kwargs)

    @staticmethod
    def _chunks_info(hits: list[dict]) -> list[dict]:
        return [{"file": h["chunk"].file, "section": h["chunk"].section,
                 "score": h["score"]} for h in hits]

    @staticmethod
    def _cited(text: str, sources: list[dict]) -> list[dict]:
        cited = {int(n) for n in re.findall(r"\[(\d+)\]", text)}
        return [s for s in sources if s["n"] in cited] or sources

    def answer(self, question: str, journey: str | None = None, profile: dict | None = None,
               tool_results: dict | None = None, k: int = TOP_K) -> dict:
        hits = self.retrieve(question, k=k, journey=journey)
        if not hits:
            return {"answer": NO_SOURCES_ANSWER, "sources": [], "chunks": []}
        user_msg, sources = self.build_prompt(question, hits, profile, tool_results)
        resp = self._complete(user_msg)
        text = resp.choices[0].message.content.strip()
        return {"answer": text, "sources": self._cited(text, sources),
                "chunks": self._chunks_info(hits)}

    def stream_answer(self, question: str, journey: str | None = None,
                      profile: dict | None = None, tool_results: dict | None = None,
                      k: int = TOP_K) -> Iterator[dict]:
        """Mesma resposta que answer(), em eventos:
        {"type": "sources", "sources", "chunks"} -> {"type": "delta", "text"}* ->
        {"type": "done", "answer", "sources"} (sources = só as citadas)."""
        hits = self.retrieve(question, k=k, journey=journey)
        if not hits:
            yield {"type": "sources", "sources": [], "chunks": []}
            yield {"type": "delta", "text": NO_SOURCES_ANSWER}
            yield {"type": "done", "answer": NO_SOURCES_ANSWER, "sources": []}
            return
        user_msg, sources = self.build_prompt(question, hits, profile, tool_results)
        yield {"type": "sources", "sources": sources, "chunks": self._chunks_info(hits)}

        stream = self._complete(user_msg, stream=True)
        parts = []
        for event in stream:
            delta = event.choices[0].delta.content if event.choices else None
            if delta:
                parts.append(delta)
                yield {"type": "delta", "text": delta}
        text = "".join(parts).strip()
        yield {"type": "done", "answer": text, "sources": self._cited(text, sources)}


# ---------------------------------------------------------------- CLI

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("question")
    ap.add_argument("--kb", default="kb")
    ap.add_argument("--journey", choices=JOURNEYS)
    ap.add_argument("--retrieve-only", action="store_true", help="não chama o LLM")
    ap.add_argument("--no-embeddings", action="store_true")
    args = ap.parse_args()

    rag = RAG(args.kb, use_embeddings=not args.no_embeddings)
    if args.retrieve_only:
        for h in rag.retrieve(args.question, journey=args.journey):
            c = h["chunk"]
            print(f"{h['score']:.4f}  {c.file} :: {c.section or '(intro)'}")
        return
    out = rag.answer(args.question, journey=args.journey)
    print(out["answer"])
    print("\nFontes:")
    for s in out["sources"]:
        print(f"  [{s['n']}] {s['title']} — {s['url']}")


if __name__ == "__main__":
    main()
