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
from typing import Callable, Iterator

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
MAX_TOOL_ROUNDS = 2  # voltas de calculadoras antes de o LLM ter de responder

SYSTEM_PROMPT = """És o Caixa Explica, um assistente de literacia financeira para jovens em Portugal.
Regras:
1. Responde apenas com base nas FONTES fornecidas. Cada afirmação factual termina com a citação [n].
2. Se as fontes não chegam para responder, diz que não sabes e indica onde procurar. Não inventes.
3. Nunca faças contas de cabeça. Para qualquer número calculado (prestação, total, juros, quanto poupar) chama a
   ferramenta certa. Só podes usar números das FONTES, das ferramentas ou de RESULTADOS DE CÁLCULO. Diz os
   pressupostos que a ferramenta devolve. Se faltar um valor para a conta (taxa, prazo, montante), pergunta-o.
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
        self._llm_params: dict = {"temperature": 0.1}
        if os.getenv("OPENAI_REASONING_EFFORT"):
            self._llm_params["reasoning_effort"] = os.getenv("OPENAI_REASONING_EFFORT")

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
                     tool_results: dict | None, referrals: list[dict] | None = None,
                     instructions: list[str] | None = None) -> tuple[str, list[dict]]:
        # numerar por documento (url), não por chunk, para citações limpas
        sources, by_url, blocks = [], {}, []

        def add(key: str, src: dict, text: str):
            if key not in by_url:
                by_url[key] = len(sources) + 1
                sources.append({"n": by_url[key], **src})
            blocks.append(f"[{by_url[key]}] {text}")

        for h in hits:
            c: Chunk = h["chunk"]
            add(c.url or c.file, {"title": c.title, "url": c.url, "source": c.source}, c.text)
        for r in referrals or []:  # entidades oficiais para onde reencaminhar (guardrails)
            add(r["url"], {"title": r["title"], "url": r["url"], "source": r["source"]},
                f"{r['title']} — {r['text']}")

        parts = ["FONTES:\n" + "\n\n".join(blocks)]
        if profile:
            parts.append("PERFIL DO UTILIZADOR:\n" + json.dumps(profile, ensure_ascii=False))
        if tool_results:
            parts.append("RESULTADOS DE CÁLCULO (usar estes números tal como estão):\n"
                         + json.dumps(tool_results, ensure_ascii=False))
        if instructions:
            parts.append("INSTRUÇÕES DE ÂMBITO (prevalecem sobre a pergunta):\n"
                         + "\n".join(f"- {i}" for i in instructions))
        parts.append(f"PERGUNTA:\n{question}")
        return "\n\n".join(parts), sources

    def _complete(self, messages: list[dict], stream: bool = False, **extra):
        """Chama o LLM. Modelos diferentes aceitam parâmetros diferentes: se o pedido for recusado
        por causa de um deles, ajusta-o (e lembra-se) e tenta outra vez."""
        while True:
            kwargs = {"model": LLM_MODEL, "messages": messages, "stream": stream, **self._llm_params, **extra}
            try:
                return self._client().chat.completions.create(**kwargs)
            except Exception as e:
                msg = str(e)
                if "temperature" in msg and "temperature" in self._llm_params:
                    # modelos de raciocínio só aceitam a temperatura por omissão
                    del self._llm_params["temperature"]
                elif "reasoning_effort" in msg and self._llm_params.get("reasoning_effort") != "none":
                    # ex.: gpt-6-luna só aceita tools no /chat/completions com reasoning_effort="none"
                    self._llm_params["reasoning_effort"] = "none"
                else:
                    raise
                print(f"[rag] {LLM_MODEL}: a ajustar parâmetros para {self._llm_params}", file=sys.stderr)

    def _generate(self, messages: list[dict], tools: list[dict] | None,
                  run_tool: Callable[[str, str], dict] | None) -> Iterator[dict]:
        """LLM em streaming com tool calling: se pedir calculadoras, corre-as e volta a chamar.
        Emite {"type": "delta", "text"} e {"type": "tool", "name", "args", "result"}."""
        for rnd in range(MAX_TOOL_ROUNDS + 1):
            extra = {}
            if tools:  # na última volta já não pode pedir mais contas: tem de responder
                extra = {"tools": tools, "tool_choice": "auto" if rnd < MAX_TOOL_ROUNDS else "none"}
            calls: dict[int, dict] = {}
            wrote = False
            for event in self._complete(messages, stream=True, **extra):
                if not event.choices:
                    continue
                delta = event.choices[0].delta
                if delta.content:
                    wrote = True
                    yield {"type": "delta", "text": delta.content}
                for tc in getattr(delta, "tool_calls", None) or []:  # chegam aos bocados: juntar por índice
                    c = calls.setdefault(tc.index, {"id": "", "name": "", "arguments": ""})
                    c["id"] = tc.id or c["id"]
                    if tc.function:
                        c["name"] += tc.function.name or ""
                        c["arguments"] += tc.function.arguments or ""
            if not calls:
                return
            if wrote:
                yield {"type": "delta", "text": "\n\n"}
            messages = [*messages, {"role": "assistant", "content": None, "tool_calls": [
                {"id": c["id"], "type": "function",
                 "function": {"name": c["name"], "arguments": c["arguments"]}} for c in calls.values()]}]
            for c in calls.values():
                result = run_tool(c["name"], c["arguments"])
                try:
                    args = json.loads(c["arguments"] or "{}")
                except ValueError:
                    args = {}
                yield {"type": "tool", "name": c["name"], "args": args, "result": result}
                messages.append({"role": "tool", "tool_call_id": c["id"],
                                 "content": json.dumps(result, ensure_ascii=False)})

    @staticmethod
    def _chunks_info(hits: list[dict]) -> list[dict]:
        return [{"file": h["chunk"].file, "section": h["chunk"].section,
                 "score": h["score"]} for h in hits]

    @staticmethod
    def _cited(text: str, sources: list[dict]) -> list[dict]:
        cited = {int(n) for n in re.findall(r"\[(\d+)\]", text)}
        return [s for s in sources if s["n"] in cited] or sources

    def _prepare(self, question: str, journey: str | None, profile: dict | None,
                 tool_results: dict | None, k: int, history: list[dict] | None,
                 referrals: list[dict] | None, instructions: list[str] | None, can_calc: bool):
        """Devolve (hits, messages, sources), ou None se não houver fonte nem calculadora."""
        # follow-ups curtos ("e a 60 meses?") não têm termos: junta a última pergunta do utilizador
        last_user = next((t["content"] for t in reversed(history or []) if t["role"] == "user"), "")
        hits = self.retrieve(f"{last_user}\n{question}".strip(), k=k, journey=journey)
        if not hits and not referrals and not can_calc:
            return None
        user_msg, sources = self.build_prompt(question, hits, profile, tool_results,
                                              referrals, instructions)
        messages = [{"role": "system", "content": SYSTEM_PROMPT}, *(history or []),
                    {"role": "user", "content": user_msg}]
        return hits, messages, sources

    def answer(self, question: str, **kwargs) -> dict:
        """Mesmos argumentos que stream_answer(); devolve {answer, sources, chunks, tools}."""
        out = {"answer": "", "sources": [], "chunks": [], "tools": []}
        for ev in self.stream_answer(question, **kwargs):
            if ev["type"] == "sources":
                out["chunks"] = ev["chunks"]
            elif ev["type"] == "tool":
                out["tools"].append({k: ev[k] for k in ("name", "args", "result")})
            elif ev["type"] == "done":
                out["answer"], out["sources"] = ev["answer"], ev["sources"]
        return out

    def stream_answer(self, question: str, journey: str | None = None,
                      profile: dict | None = None, tool_results: dict | None = None,
                      k: int = TOP_K, history: list[dict] | None = None,
                      referrals: list[dict] | None = None, instructions: list[str] | None = None,
                      tools: list[dict] | None = None,
                      run_tool: Callable[[str, str], dict] | None = None) -> Iterator[dict]:
        """Eventos: {"type": "sources", "sources", "chunks"} -> ({"type": "tool", "name", "args",
        "result"} | {"type": "delta", "text"})* -> {"type": "done", "answer", "sources"}
        (sources = só as citadas). `tools` + `run_tool` ligam as calculadoras (tools.py)."""
        prep = self._prepare(question, journey, profile, tool_results, k, history,
                             referrals, instructions, can_calc=bool(tools))
        if prep is None:
            yield {"type": "sources", "sources": [], "chunks": []}
            yield {"type": "delta", "text": NO_SOURCES_ANSWER}
            yield {"type": "done", "answer": NO_SOURCES_ANSWER, "sources": []}
            return
        hits, messages, sources = prep
        yield {"type": "sources", "sources": sources, "chunks": self._chunks_info(hits)}

        parts = []
        for ev in self._generate(messages, tools, run_tool):
            if ev["type"] == "delta":
                parts.append(ev["text"])
            yield ev
        text = "".join(parts).strip()
        yield {"type": "done", "answer": text, "sources": self._cited(text, sources) if sources else []}


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
    from tools import SCHEMAS, run_tool
    out = rag.answer(args.question, journey=args.journey, tools=SCHEMAS, run_tool=run_tool)
    print(out["answer"])
    print("\nFontes:")
    for s in out["sources"]:
        print(f"  [{s['n']}] {s['title']} — {s['url']}")


if __name__ == "__main__":
    main()
