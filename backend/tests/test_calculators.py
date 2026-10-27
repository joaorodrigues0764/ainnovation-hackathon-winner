import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from calculators import (custo_credito, efeito_inflacao, juros_compostos, objetivo_poupanca,
                         orcamento, salario_liquido)


def test_uc01_objetivo_com_clarificacao():          # USE_CASES UC-01
    r = objetivo_poupanca(600, 6, 0, mensal_disponivel=80)
    assert (r["necessario_por_mes"], r["juntaria_no_prazo"], r["defice_total"], r["defice_por_mes"],
            r["meses_necessarios"]) == (100.0, 480.0, 120.0, 20.0, 8)


def test_c2_avaliacao_600_em_8_meses_com_120():     # AVALIACAO C2
    assert objetivo_poupanca(600, 8, 120)["necessario_por_mes"] == 60.0


def test_uc02_regra_50_30_20():                     # UC-02
    assert orcamento(900, 0)["regra"] == {"necessidades": 450.0, "desejos": 270.0, "poupanca": 180.0}


def test_c1_avaliacao_saldo():                      # AVALIACAO C1
    r = orcamento(400, 150)
    assert r["saldo"] == 250.0 and r["taxa_poupanca_atual_pct"] == 62.5


def test_uc05_credito_1000_12pct_24():              # UC-05
    r = custo_credito(1000, 12, 24)
    assert (r["prestacao_mensal"], r["total_a_pagar"], r["juros"]) == (47.07, 1129.76, 129.76)
    assert "TAEG" in r["pressupostos"]


def test_credito_sem_juros():
    r = custo_credito(1200, 0, 12)
    assert (r["prestacao_mensal"], r["total_a_pagar"], r["juros"]) == (100.0, 1200.0, 0.0)


def test_uc06_juros_compostos_50_3pct_5anos():      # UC-06 / AVALIACAO C3
    r = juros_compostos(50, 3, 5)
    assert (r["depositado"], r["valor_final"], r["juros"], r["meses"]) == (3000.0, 3232.34, 232.34, 60)


def test_juros_compostos_confere_com_formula_independente():
    r, n, p = 0.03 / 12, 60, 50
    esperado = p * (((1 + r) ** n - 1) / r)
    assert abs(juros_compostos(50, 3, 5)["valor_final"] - esperado) < 0.01


def test_juros_zero_e_capital_inicial():
    assert juros_compostos(100, 0, 1)["valor_final"] == 1200.0
    assert juros_compostos(0, 12, 1, capital_inicial=1000)["valor_final"] == 1126.83


def test_uc17_seguranca_social_sem_inventar_irs():  # UC-17
    r = salario_liquido(1000)
    assert (r["seguranca_social"], r["apos_seguranca_social"], r["retencao_irs"]) == (110.0, 890.0, None)


def test_inflacao():
    r = efeito_inflacao(1000, 2, 10)
    assert r["poder_de_compra_futuro"] == 820.35 and r["perda"] == 179.65


@pytest.mark.parametrize("chamada", [
    lambda: objetivo_poupanca(600, 0), lambda: objetivo_poupanca(-1, 6), lambda: objetivo_poupanca(600, 2.5),
    lambda: custo_credito(0, 5, 12), lambda: custo_credito(1000, -1, 12), lambda: custo_credito(1000, 5, 0),
    lambda: juros_compostos(50, 3, 0), lambda: orcamento(0, 10), lambda: orcamento(100, -5),
    lambda: orcamento(100, 10, regra=(50, 30, 30)), lambda: salario_liquido(0),
])
def test_entradas_invalidas_levantam_erro(chamada):
    with pytest.raises(ValueError):
        chamada()
