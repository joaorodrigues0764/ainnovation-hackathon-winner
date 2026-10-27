"""Lógica do harness (scripts/harness.py), sem API nem LLM."""
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import harness as h  # noqa: E402


def nums(text):
    return [v for _, v in h.extract_numbers(text)]


def test_extrai_formatos_portugueses():
    assert nums("pagas 199,08 € por mês e 9 555,86 € no total") == [Decimal("199.08"), Decimal("9555.86")]
    assert nums("um carro de 8 000 € a 9% em 48 meses") == [Decimal("8000"), Decimal("9"), Decimal("48")]
    assert nums("total de 1.555,86 €") == [Decimal("1555.86")]
    assert nums("taxa nominal 9.0% ao ano (0.75% ao mês)") == [Decimal("9.0"), Decimal("0.75")]


def test_ignora_citacoes_e_numeracao_de_listas():
    assert nums("A TAEG inclui comissões [1] e seguros [12].") == []
    assert nums("1. Compara a TAEG\n2. Lê a FIN") == []


def test_numeros_das_calculadoras_e_arredondamentos_sao_permitidos():
    allowed = h.allowed_numbers(["Quero 1000 € a 12% em 24 meses"],
                                [{"montante": 1000, "taxa_anual_nominal": 0.12, "prestacoes": 24},
                                 {"prestacao_mensal": 47.07, "total_a_pagar": 1129.76, "juros": 129.76}])
    answer = "Pagas cerca de 47 € por mês (47,07 €), no total ronda 1 130 €, com 129,76 € de juros a 12%."
    assert h.unsupported_numbers(answer, allowed) == []


def test_apanha_numeros_inventados():
    allowed = h.allowed_numbers(["Quanto está hoje a Euribor?"], [])
    assert h.unsupported_numbers("A Euribor a 12 meses está nos 2,45%.", allowed) == ["12", "2,45"]


def test_contagens_pequenas_nao_contam():
    assert h.unsupported_numbers("Guarda 3 a 6 meses de despesas; o 1.º passo é simples.", set()) == []


def test_citacao_tem_de_bater_com_uma_fonte_devolvida():
    sources = [{"n": 1, "title": "TAEG", "url": "u", "source": "BdP"}]
    assert h.has_citation("A TAEG inclui comissões [1].", sources)
    assert not h.has_citation("A TAEG inclui comissões [2].", sources)
    assert not h.has_citation("A TAEG inclui comissões.", sources)


def test_proximo_passo():
    assert h.has_next_step("**Próximo passo:** pede a FIN.")
    assert h.has_next_step("Próximos passos:\n1. ...")
    assert not h.has_next_step("Pede a FIN ao banco.")


def test_calculadora_esperada():
    calls = [{"name": "custo_credito", "args": {}, "result": {"prestacao_mensal": 47.07, "juros": 129.76}}]
    assert h.tool_problems({"custo_credito": {"prestacao_mensal": 47.07}}, calls) == []
    assert h.tool_problems({"custo_credito": {"prestacao_mensal": 50.0}}, calls)
    assert h.tool_problems({"orcamento": {"saldo": 250.0}}, calls) == ["orcamento não foi chamada"]
    nested = [{"name": "orcamento", "args": {}, "result": {"regra": {"necessidades": 450.0, "desejos": 270.0}}}]
    assert h.tool_problems({"orcamento": {"regra": {"necessidades": 450.0}}}, nested) == []


def test_evaluate_junta_tudo():
    case = {"id": "x", "expect": {"tools": {"custo_credito": {"prestacao_mensal": 47.07}}}}
    body = {"question": "1000 € a 12% em 24 meses?", "history": []}
    run = h.Run(answer="Pagas 47,07 € por mês [1]. Próximo passo: compara a TAEG.",
                sources=[{"n": 1, "title": "t", "url": "u", "source": "s"}],
                tools=[{"name": "custo_credito", "args": {"montante": 1000}, "result": {"prestacao_mensal": 47.07}}],
                first_text_s=1.0, total_s=2.0)
    r = h.evaluate(case, body, run, {})
    assert r["cited"] and r["next_step"] and r["tools_ok"] and r["guardrails_ok"]
    assert r["free_numbers"] == [] and r["problems"] == []


def test_casos_do_harness_sao_validos():
    import json
    cases = json.loads((ROOT / "docs/harness_cases.json").read_text(encoding="utf-8"))
    ids = [c["id"] for c in cases]
    assert len(cases) == 20 and len(set(ids)) == len(ids)
    for c in cases:
        assert c["question"] and c.get("journey") in {"credito", "salario", "irs", "burlas", "poupanca", "geral"}
        assert c.get("follow_up_of") in (None, *ids)
        for name in c.get("expect", {}).get("tools", {}):
            assert name in {"custo_credito", "objetivo_poupanca", "juros_compostos", "orcamento",
                            "salario_liquido", "efeito_inflacao"}
