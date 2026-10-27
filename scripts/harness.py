"""Harness das métricas do PRD: corre os casos de docs/harness_cases.json pela API real
(POST /chat/stream, o mesmo caminho do front) e mede:

    citação      respostas com pelo menos uma fonte citada [n]           alvo 100 %
    números      números que não vêm da pergunta, histórico, perfil,
                 calculadoras ou chunks recuperados (= inventados)       alvo 0
    próximo      respostas com "Próximo passo"                           alvo ≥ 90 %
    calculadora  a calculadora certa correu e deu os valores esperados   alvo 100 %
    guardrails   scope/PII esperados                                     alvo 100 %
    latência     1.º texto e total (p50/p95)                             alvo < 5 s

Gasta tokens (1 pedido ao LLM por caso). Correr com a API ligada:
    backend/.venv/Scripts/python scripts/harness.py --md docs/HARNESS.md
    ... --only demo-1-credito --only demo-2-60-meses     (follow-ups puxam o caso de origem)
Sai com código 1 se alguma meta do PRD falhar.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import time
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from rag import load_kb  # noqa: E402

IGNORE_INT_MAX = 10   # contagens ("3 passos", "1.º ano") não são números financeiros
LATENCY_TARGET_S = 5.0

# ---------------------------------------------------------------- números

_NUM = re.compile(
    r"(?<![\w.,])\d{1,3}(?:[   .]\d{3})+(?:,\d+)?(?![\d])"   # 8 000 / 1.555,86
    r"|(?<![\w.,])\d+(?:[.,]\d+)?(?![\d])")                            # 47,07 / 9.0 / 2026


def _parse(raw: str) -> Decimal | None:
    s = raw.replace(" ", " ").replace(" ", " ")
    if re.fullmatch(r"\d{1,3}(?:[ .]\d{3})+(?:,\d+)?", s):
        s = re.sub(r"[ .]", "", s)
    s = s.replace(",", ".")
    try:
        return Decimal(s)
    except InvalidOperation:
        return None


def extract_numbers(text: str) -> list[tuple[str, Decimal]]:
    """Números de um texto, sem citações [n] nem numeração de listas."""
    text = re.sub(r"\[\d+\]", " ", text)
    text = re.sub(r"(?m)^\s*\d+[.)]\s+", " ", text)
    out = []
    for m in _NUM.finditer(text):
        v = _parse(m.group(0))
        if v is not None:
            out.append((m.group(0), v))
    return out


def _variants(v: Decimal) -> set[Decimal]:
    """O LLM pode arredondar ("cerca de 47 €", "ronda 1 130 €") sem inventar."""
    out = {v, v.quantize(Decimal("0.01")), v.quantize(Decimal("0.1")), v.quantize(Decimal("1"))}
    if abs(v) >= 100:
        out.add((v / 10).quantize(Decimal("1")) * 10)
    if 0 < abs(v) < 1:  # taxas em decimal (0.09) aparecem como 9 %
        out |= _variants(v * 100)
    return {x.normalize() for x in out}


def _walk(value) -> list[Decimal]:
    if isinstance(value, bool) or value is None:
        return []
    if isinstance(value, (int, float)):
        return [Decimal(str(value))]
    if isinstance(value, str):
        return [v for _, v in extract_numbers(value)]
    if isinstance(value, dict):
        return [x for v in value.values() for x in _walk(v)]
    if isinstance(value, list):
        return [x for v in value for x in _walk(v)]
    return []


def allowed_numbers(texts: list[str], structured: list) -> set[Decimal]:
    vals = [v for t in texts for _, v in extract_numbers(t)] + [v for s in structured for v in _walk(s)]
    return {x for v in vals for x in _variants(v)}


def unsupported_numbers(answer: str, allowed: set[Decimal]) -> list[str]:
    bad = []
    for raw, v in extract_numbers(answer):
        if v == v.to_integral_value() and 0 <= v <= IGNORE_INT_MAX:
            continue
        if v.normalize() not in allowed:
            bad.append(raw)
    return bad


# ---------------------------------------------------------------- outras verificações

_NEXT = re.compile(r"pr[óo]xim[oa]s?\s+passos?", re.I)


def has_next_step(answer: str) -> bool:
    return bool(_NEXT.search(answer))


def has_citation(answer: str, sources: list[dict]) -> bool:
    cited = {int(n) for n in re.findall(r"\[(\d+)\]", answer)}
    return bool(cited & {s["n"] for s in sources})


def _close(expected, got) -> bool:
    if isinstance(expected, dict):
        return isinstance(got, dict) and all(_close(v, got.get(k)) for k, v in expected.items())
    if isinstance(expected, (int, float)) and isinstance(got, (int, float)):
        return abs(expected - got) <= 0.01
    return expected == got


def tool_problems(expected: dict, calls: list[dict]) -> list[str]:
    problems = []
    for name, values in expected.items():
        runs = [c for c in calls if c["name"] == name]
        if not runs:
            problems.append(f"{name} não foi chamada")
        elif not any(_close(values, c["result"]) for c in runs):
            got = [{k: c["result"].get(k) for k in values} for c in runs]
            problems.append(f"{name}: esperado {values}, veio {got}")
    return problems


# ---------------------------------------------------------------- execução

@dataclass
class Run:
    answer: str = ""
    sources: list[dict] = field(default_factory=list)
    chunks: list[dict] = field(default_factory=list)
    scope: list[str] = field(default_factory=list)
    pii: list[str] = field(default_factory=list)
    tools: list[dict] = field(default_factory=list)
    error: str | None = None
    first_text_s: float | None = None
    total_s: float = 0.0


def call_stream(api: str, body: dict, timeout: float = 120) -> Run:
    run, t0 = Run(), time.perf_counter()
    req = urllib.request.Request(f"{api}/chat/stream", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            event, data = "", []
            for raw in resp:
                line = raw.decode("utf-8").rstrip("\r\n")
                if line.startswith("event:"):
                    event = line[6:].strip()
                elif line.startswith("data:"):
                    data.append(line[5:].strip())
                elif not line and event:
                    _apply(run, event, json.loads("\n".join(data)), time.perf_counter() - t0)
                    event, data = "", []
    except Exception as e:  # rede, HTTP 4xx/5xx, JSON partido
        run.error = f"{type(e).__name__}: {e}"
    run.total_s = time.perf_counter() - t0
    return run


def _apply(run: Run, event: str, d: dict, t: float) -> None:
    if event == "warning":
        run.pii = d.get("pii", [])
    elif event == "sources":
        run.chunks, run.scope = d.get("chunks", []), d.get("scope", [])
    elif event == "tool":
        run.tools.append(d)
    elif event == "delta" and run.first_text_s is None:
        run.first_text_s = t
    elif event == "done":
        run.answer, run.sources = d["answer"], d["sources"]
    elif event == "error":
        run.error = d.get("detail", "erro")


def chunk_texts(kb_dir: Path) -> dict[tuple[str, str], str]:
    texts: dict[tuple[str, str], str] = {}
    for c in load_kb(kb_dir):
        key = (c.file, c.section)
        texts[key] = texts.get(key, "") + "\n" + c.text
    return texts


def evaluate(case: dict, body: dict, run: Run, kb: dict[tuple[str, str], str]) -> dict:
    exp = case.get("expect", {})
    texts = [body["question"], *(t["content"] for t in body.get("history", []))]
    texts += [kb.get((c["file"], c["section"]), "") for c in run.chunks]
    allowed = allowed_numbers(texts, [body.get("profile") or {}, *[[t["args"], t["result"]] for t in run.tools]])

    problems = [f"erro: {run.error}"] if run.error else []
    problems += tool_problems(exp.get("tools", {}), run.tools)
    if exp.get("no_tools") and run.tools:
        problems.append(f"calculadora inesperada: {[t['name'] for t in run.tools]}")
    if sorted(exp.get("scope", [])) != sorted(run.scope):
        problems.append(f"scope esperado {exp.get('scope', [])}, veio {run.scope}")
    if exp.get("pii", False) != bool(run.pii):
        problems.append(f"PII esperado {exp.get('pii', False)}, veio {run.pii}")

    return {
        "id": case["id"], "uc": case.get("uc", ""), "question": body["question"],
        "cited": has_citation(run.answer, run.sources),
        "free_numbers": unsupported_numbers(run.answer, allowed),
        "next_step": has_next_step(run.answer),
        "tools_ok": not tool_problems(exp.get("tools", {}), run.tools) and not (exp.get("no_tools") and run.tools),
        "guardrails_ok": sorted(exp.get("scope", [])) == sorted(run.scope) and exp.get("pii", False) == bool(run.pii),
        "problems": problems,
        "first_text_s": run.first_text_s, "total_s": round(run.total_s, 2),
        "tools": [t["name"] for t in run.tools], "answer": run.answer,
    }


def run_cases(api: str, cases: list[dict], kb: dict, log=print) -> list[dict]:
    by_id, answers, results = {c["id"]: c for c in cases}, {}, []
    for case in cases:
        body = {"question": case["question"], "journey": case.get("journey"),
                "history": list(case.get("history", []))}
        if case.get("profile"):
            body["profile"] = case["profile"]
        parent = case.get("follow_up_of")
        if parent:
            if parent not in answers:  # --only com um follow-up: corre primeiro o caso de origem
                p = by_id[parent]
                answers[parent] = call_stream(api, {"question": p["question"], "journey": p.get("journey"),
                                                    "profile": p.get("profile"), "history": []}).answer
            body["history"] += [{"role": "user", "content": by_id[parent]["question"]},
                                {"role": "assistant", "content": answers[parent][:4000]}]
        run = call_stream(api, body)
        answers[case["id"]] = run.answer
        r = evaluate(case, body, run, kb)
        results.append(r)
        flag = "OK " if not r["problems"] and r["cited"] and not r["free_numbers"] and r["next_step"] else "!! "
        log(f"{flag}{r['id']:<22} {r['total_s']:>5.1f}s  cit={'s' if r['cited'] else 'N'}  "
            f"num={len(r['free_numbers'])}  passo={'s' if r['next_step'] else 'N'}  {'; '.join(r['problems'])}")
    return results


# ---------------------------------------------------------------- resumo

def _pct(n: int, d: int) -> float:
    return 100.0 * n / d if d else 100.0


def _p(values: list[float], q: float) -> float | None:
    if not values:
        return None
    if len(values) == 1:
        return values[0]
    return statistics.quantiles(values, n=100, method="inclusive")[int(q) - 1]


def summarize(results: list[dict], cases: list[dict]) -> list[dict]:
    n = len(results)
    with_tools = [r for r, c in zip(results, cases) if c.get("expect", {}).get("tools") or c.get("expect", {}).get("no_tools")]
    with_guard = [r for r, c in zip(results, cases) if c.get("expect", {}).get("scope") or c.get("expect", {}).get("pii")]
    first = [r["first_text_s"] for r in results if r["first_text_s"] is not None]
    total = [r["total_s"] for r in results]
    rows = [
        ("Respostas com fonte citada", _pct(sum(r["cited"] for r in results), n), "100 %", lambda v: v >= 100),
        ("Respostas com números inventados", sum(bool(r["free_numbers"]) for r in results), "0", lambda v: v == 0),
        ("Respostas com próximo passo", _pct(sum(r["next_step"] for r in results), n), "≥ 90 %", lambda v: v >= 90),
        ("Calculadora certa e valores certos", _pct(sum(r["tools_ok"] for r in with_tools), len(with_tools)), "100 %", lambda v: v >= 100),
        ("Guardrails e PII como esperado", _pct(sum(r["guardrails_ok"] for r in with_guard), len(with_guard)), "100 %", lambda v: v >= 100),
        ("Latência até ao 1.º texto, p50 (s)", _p(first, 50), f"< {LATENCY_TARGET_S:g}", lambda v: v is not None and v < LATENCY_TARGET_S),
        ("Latência total, p95 (s)", _p(total, 95), "(informativo)", lambda v: True),
    ]
    return [{"metric": m, "value": v, "target": t, "ok": ok(v)} for m, v, t, ok in rows]


def _fmt(v) -> str:
    if v is None:
        return "—"
    return f"{v:.1f}" if isinstance(v, float) else str(v)


def markdown(summary: list[dict], results: list[dict], api: str, model: str) -> str:
    lines = [
        "# Harness — métricas do PRD", "",
        f"Corrida de {datetime.now():%Y-%m-%d %H:%M} contra `{api}` (modelo `{model}`), {len(results)} casos de "
        "[`docs/harness_cases.json`](harness_cases.json). Gerado por `scripts/harness.py`.", "",
        "| Métrica | Valor | Alvo | |", "| --- | --- | --- | --- |",
        *[f"| {s['metric']} | {_fmt(s['value'])} | {s['target']} | {'✅' if s['ok'] else '❌'} |" for s in summary],
        "", "## Por caso", "",
        "| Caso | UC | Citação | Números inventados | Próximo passo | Calculadoras | Total (s) | Problemas |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in results:
        lines.append(
            f"| `{r['id']}` | {r['uc']} | {'✅' if r['cited'] else '❌'} | {', '.join(r['free_numbers']) or '—'} | "
            f"{'✅' if r['next_step'] else '❌'} | {', '.join(r['tools']) or '—'} | {r['total_s']:.1f} | "
            f"{'; '.join(r['problems']) or '—'} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--api", default="http://localhost:8000")
    ap.add_argument("--cases", type=Path, default=ROOT / "docs/harness_cases.json")
    ap.add_argument("--kb", type=Path, default=ROOT / "backend/kb")
    ap.add_argument("--only", action="append", help="correr só este caso (pode repetir)")
    ap.add_argument("--md", type=Path, help="escrever o relatório em Markdown")
    ap.add_argument("--json", type=Path, help="escrever os resultados completos em JSON")
    args = ap.parse_args()

    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    if args.only:
        cases = [c for c in cases if c["id"] in set(args.only)]
    with urllib.request.urlopen(f"{args.api}/health", timeout=10) as r:
        health = json.load(r)
    print(f"API {args.api}: {health}\n")

    results = run_cases(args.api, cases, chunk_texts(args.kb))
    summary = summarize(results, cases)
    print()
    for s in summary:
        print(f"{'✅' if s['ok'] else '❌'} {s['metric']:<38} {_fmt(s['value']):>6}   alvo {s['target']}")
    if args.md:
        args.md.write_text(markdown(summary, results, args.api, health.get("model", "?")), encoding="utf-8")
    if args.json:
        args.json.write_text(json.dumps({"health": health, "summary": summary, "results": results},
                                        ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if all(s["ok"] for s in summary) else 1


if __name__ == "__main__":
    sys.exit(main())
