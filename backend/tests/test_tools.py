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
