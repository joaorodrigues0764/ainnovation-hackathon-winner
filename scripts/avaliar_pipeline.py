"""Avaliação determinista da pipeline (sem LLM, sem rede): calculadoras, guardrails e máscara de dados.
Cada caso vem de um UC de USE_CASES.md. Uso na raiz: python scripts/avaliar_pipeline.py
Saída: tabela UC | verificação | esperado | obtido | OK. Código de saída 1 se algum falhar."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from calculators import (custo_credito, efeito_inflacao, juros_compostos, objetivo_poupanca,  # noqa: E402
                         orcamento, salario_liquido)
from guardrails import check_scope  # noqa: E402
from privacy import mask_pii  # noqa: E402


def kinds(q):
    return sorted(h.kind for h in check_scope(q))


def urls(q):
    return sorted({r["url"].split("//")[1].split("/")[0] for h in check_scope(q) for r in h.referrals})


CASOS = [
    ("UC-01", "poupança 600 em 6 m, 80/mês: necessário, défice, meses",
     (100.0, 20.0, 8),
     lambda: (lambda r: (r["necessario_por_mes"], r["defice_por_mes"], r["meses_necessarios"]))(objetivo_poupanca(600, 6, 0, 80))),
    ("UC-02", "orçamento 900: regra 50/30/20", (450.0, 270.0, 180.0),
     lambda: tuple(orcamento(900, 0)["regra"].values())),
    ("UC-05", "crédito 1000, 12 %, 24 prest.: prestação, total, juros", (47.07, 1129.76, 129.76),
     lambda: (lambda r: (r["prestacao_mensal"], r["total_a_pagar"], r["juros"]))(custo_credito(1000, 0.12, 24))),
    ("UC-05b", "taxa 12, '12%' e 0.12 dão o mesmo resultado", True,
     lambda: custo_credito(1000, 12, 24) == custo_credito(1000, "12%", 24) == custo_credito(1000, 0.12, 24)),
    ("UC-06", "juros compostos 50/mês, 3 %, 5 anos: depositado, juros", (3000.0, 232.34),
     lambda: (lambda r: (r["depositado"], r["juros"]))(juros_compostos(50, 0.03, 5))),
    ("UC-17", "bruto 1000: SS, líquido, IRS não inventado", (110.0, 890.0, None),
     lambda: (lambda r: (r["seguranca_social"], r["apos_seguranca_social"], r["retencao_irs"]))(salario_liquido(1000))),
    ("UC-19", "orçamento 800: poupança 20 %", 160.0, lambda: orcamento(800, 0)["regra"]["poupanca"]),
    ("UC-09", "pede ações/Bitcoin: guardrail investimento + CMVM", (["investimento"], ["www.cmvm.pt"]),
     lambda: (kinds("Quais são as melhores ações para investir hoje para ter lucro rápido? Ou devo comprar Bitcoin?"),
              urls("Quais são as melhores ações para investir hoje para ter lucro rápido? Ou devo comprar Bitcoin?"))),
    ("UC-13", "pede renegociar e tratar do IRS: ação externa + 3 entidades", ["acao_externa"],
     lambda: kinds("Podes renegociar a taxa de juro do meu crédito comigo ou tratar da minha declaração de IRS no portal?")),
    ("UC-14", "pede 'melhor banco': guardrail produto", ["produto"], lambda: kinds("Qual é o melhor banco para abrir conta?")),
    ("UC-15", "escalões e Euribor de hoje: valores_atuais (precisa do PR #21)", ["valores_atuais"],
     lambda: kinds("Quais são os escalões de IRS deste ano e quanto está hoje a Euribor?")),
    ("neg-1", "pergunta normal não dispara guardrail", [], lambda: kinds("Quero juntar 600 euros em 6 meses para uma viagem")),
    ("neg-2", "'O que é a Euribor?' não dispara valores_atuais", [], lambda: kinds("O que é a Euribor?")),
    ("UC-10", "NIF e IBAN mascarados antes do LLM", (False, False),
     lambda: (lambda t: ("123456789" in t, "0002 0123" in t))(mask_pii("O meu NIF é 123456789 e o IBAN PT50 0002 0123 1234 5678 9015 4").text)),
    ("erro-1", "taxa 150 % é recusada", "ValueError",
     lambda: _erro(lambda: custo_credito(1000, 150, 24))),
    ("erro-2", "inflação 2 % a 10 anos: perda = 1000 - 1000/1.02^10", round(1000 - 1000 / 1.02 ** 10, 2),
     lambda: efeito_inflacao(1000, 0.02, 10)["perda"]),
]


def _erro(f):
    try:
        f()
    except ValueError:
        return "ValueError"
    return "sem erro"


def main() -> int:
    falhas = 0
    print("| ID | Verificação | Esperado | Obtido | OK |\n|---|---|---|---|---|")
    for id_, desc, esperado, f in CASOS:
        try:
            obtido = f()
        except Exception as e:  # noqa: BLE001
            obtido = f"EXCEÇÃO {e!r}"
        ok = obtido == esperado
        falhas += not ok
        print(f"| {id_} | {desc} | {esperado} | {obtido} | {'OK' if ok else 'FALHA'} |")
    print(f"\n{len(CASOS) - falhas}/{len(CASOS)} OK")
    return 1 if falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())
