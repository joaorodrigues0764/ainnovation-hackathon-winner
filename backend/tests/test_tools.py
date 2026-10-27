import inspect
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import calculators  # noqa: E402
from tools import SCHEMAS, run_tool  # noqa: E402


def test_esquemas_batem_com_as_calculadoras():
    for s in SCHEMAS:
        f = s["function"]
        params = inspect.signature(getattr(calculators, f["name"])).parameters
        assert set(f["parameters"]["properties"]) <= set(params), f["name"]
        assert set(f["parameters"]["required"]) <= set(f["parameters"]["properties"])
        obrigatorios = {n for n, p in params.items() if p.default is inspect.Parameter.empty}
        assert obrigatorios <= set(f["parameters"]["required"]), f["name"]


def test_corre_com_json_e_com_dict():
    esperado = calculators.custo_credito(1000, 12, 24)
    assert run_tool("custo_credito", '{"montante": 1000, "taxa_anual_nominal": 12, "prestacoes": 24}') == esperado
    assert run_tool("custo_credito", {"montante": 1000, "taxa_anual_nominal": 12, "prestacoes": 24}) == esperado


def test_opcionais_a_null_sao_ignorados():
    r = run_tool("objetivo_poupanca", '{"valor": 600, "meses": 6, "mensal_disponivel": null}')
    assert r["necessario_por_mes"] == 100.0 and "mensal_disponivel" not in r


def test_erros_nunca_rebentam():
    assert "erro" in run_tool("apagar_tudo", "{}")
    assert "erro" in run_tool("custo_credito", "{não é json")
    assert "erro" in run_tool("custo_credito", '{"montante": 1000}')                   # faltam argumentos
    assert "erro" in run_tool("custo_credito", '{"montante": 1000, "taxa_anual_nominal": 12, "prestacoes": 24, "x": 1}')
    assert "erro" in run_tool("custo_credito", '{"montante": -5, "taxa_anual_nominal": 12, "prestacoes": 24}')


def test_taxas_em_decimal_sem_ambiguidade_no_1_porcento():
    # o esquema pede decimal ao LLM: 1 % chega como 0.01 (o número 1 seria lido como 100 %)
    for s in SCHEMAS:
        for nome, p in s["function"]["parameters"]["properties"].items():
            if "taxa" in nome:
                assert "decimal" in p["description"], (s["function"]["name"], nome)
    r = run_tool("juros_compostos", '{"deposito_mensal": 100, "taxa_anual": 0.01, "anos": 1}')
    assert 1200 < r["valor_final"] < 1210


def test_orcamento_divide_tambem_o_que_sobra():
    # AVALIACAO C1: "recebo 400 €, gasto 150, como divido o resto?" -> 50/30/20 dos 250 € feito em Python
    r = run_tool("orcamento", '{"entradas": 400, "gastos": 150}')
    assert r["saldo"] == 250.0
    assert r["regra_do_que_sobra"] == {"necessidades": 125.0, "desejos": 75.0, "poupanca": 50.0}
    assert "regra_do_que_sobra" not in run_tool("orcamento", '{"entradas": 900, "gastos": 0}')


def test_taxa_de_esforco_com_o_rendimento_do_perfil():
    args = '{"montante": 8000, "taxa_anual_nominal": 0.09, "prestacoes": 60}'
    r = run_tool("custo_credito", args, profile={"rendimento_liquido": 1100})
    assert r["prestacao_mensal"] == 166.07 and r["taxa_esforco_pct"] == 15.1
    assert "taxa_esforco_pct" not in run_tool("custo_credito", args)
