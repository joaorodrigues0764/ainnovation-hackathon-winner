"""Avaliação local de pesquisa por ficheiro; não chama o LLM nem usa embeddings.

Uso na raiz: backend/.venv/bin/python scripts/avaliar_kb.py --kb backend/kb
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from rag import RAG  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kb", type=Path, default=ROOT / "backend/kb")
    parser.add_argument("--cases", type=Path, default=ROOT / "docs/kb_retrieval_cases.json")
    parser.add_argument("--output", type=Path, help="Guardar resultados detalhados em JSON")
    parser.add_argument("--group", action="append", help="Avaliar apenas este grupo; pode repetir")
    args = parser.parse_args()
    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    if not cases or len({case["id"] for case in cases}) != len(cases):
        parser.error("Os casos devem ser não vazios e ter identificadores únicos")
    if args.group:
        unknown = set(args.group) - {case["group"] for case in cases}
        if unknown:
            parser.error(f"Grupos desconhecidos: {sorted(unknown)}")
        cases = [case for case in cases if case["group"] in args.group]
    rag = RAG(args.kb, use_embeddings=False)
    results = []
    groups = defaultdict(lambda: {"passed": 0, "total": 0})
    for case in cases:
        if not case["expected_files"]:
            parser.error(f"Sem ficheiros esperados: {case['id']}")
        hits = rag.retrieve(case["question"], k=5, journey=case["journey"])
        found = [hit["chunk"].file for hit in hits]
        # Cada ficheiro esperado deve aparecer; repetições do mesmo ficheiro
        # não contam como fontes distintas. A métrica não avalia o texto gerado.
        passed = set(case["expected_files"]).issubset(found)
        if any(hit["chunk"].journey not in (case["journey"], "geral") for hit in hits):
            raise RuntimeError(f"Filtro de jornada violado: {case['id']}")
        groups[case["group"]]["total"] += 1
        groups[case["group"]]["passed"] += int(passed)
        results.append({
            **case,
            "passed": passed,
            "missing_files": sorted(set(case["expected_files"]) - set(found)),
            "hits": [{"file": hit["chunk"].file, "section": hit["chunk"].section,
                      "score": hit["score"]} for hit in hits],
        })
        print(f"{'PASS' if passed else 'FAIL'} {case['id']}: {found}")
    report = {"mode": "BM25; sem LLM ou embeddings", "kb": str(args.kb),
              "files": len({chunk.file for chunk in rag.chunks}),
              "chunks": len(rag.chunks), "groups": dict(groups), "results": results}
    if args.output:
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for group, counts in groups.items():
        print(f"{group}: {counts['passed']}/{counts['total']} ficheiro esperado no top 5")
    return 0 if all(result["passed"] for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
