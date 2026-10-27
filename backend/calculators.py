"""Calculadoras do agente. O LLM NUNCA faz contas: chama-se uma destas funções e o modelo só explica.

Regras: dinheiro em Decimal e arredondado a cêntimos (meio para cima); entradas inválidas levantam
ValueError (nunca devolvem 0 em silêncio); cada resultado traz os `pressupostos` usados, para o
agente os mostrar. Taxas em PERCENTAGEM (3 = 3%). Valores vêm em `float` (€) já arredondados.

    from calculators import (orcamento, objetivo_poupanca, juros_compostos,
                             custo_credito, efeito_inflacao, salario_liquido)
"""
from __future__ import annotations

import math
from decimal import ROUND_HALF_UP, Decimal, getcontext

getcontext().prec = 28
_CENT = Decimal("0.01")


def _d(x) -> Decimal:
    return Decimal(str(x))


def _eur(x: Decimal) -> float:
    return float(x.quantize(_CENT, rounding=ROUND_HALF_UP))


def _taxa(nome: str, x) -> Decimal:
    """Taxa em decimal, de 0 a 1 (0.12 = 12 %). Fora disso é erro, para não aceitar 12 ou 0.0012 por engano."""
    v = _d(x)
    if v < 0 or v > 1:
        raise ValueError(f"{nome} tem de estar entre 0 e 1 (0.12 = 12 %): {x}")
    return v


def _pos(nome: str, x, *, zero_ok: bool = True) -> Decimal:
    v = _d(x)
    if v < 0 or (v == 0 and not zero_ok):
        raise ValueError(f"{nome} inválido: {x}")
    return v


def orcamento(entradas: float, gastos: float, regra: tuple[int, int, int] = (50, 30, 20)) -> dict:
    """Saldo do mês e divisão de referência necessidades/desejos/poupança (por defeito 50/30/20)."""
    e, g = _pos("entradas", entradas, zero_ok=False), _pos("gastos", gastos)
    if sum(regra) != 100:
        raise ValueError("a regra tem de somar 100")
    return {
        "entradas": _eur(e), "gastos": _eur(g), "saldo": _eur(e - g),
        "taxa_poupanca_atual_pct": _eur((e - g) / e * 100),
        "regra": {"necessidades": _eur(e * regra[0] / 100), "desejos": _eur(e * regra[1] / 100),
                  "poupanca": _eur(e * regra[2] / 100)},
        "pressupostos": f"regra {regra[0]}/{regra[1]}/{regra[2]} como ponto de partida, não obrigação",
    }


def objetivo_poupanca(valor: float, meses: int, ja_tenho: float = 0, mensal_disponivel: float | None = None) -> dict:
    """Quanto poupar por mês para um objetivo (sem juros). Com `mensal_disponivel`, diz o défice e o prazo real."""
    v, j = _pos("valor", valor, zero_ok=False), _pos("ja_tenho", ja_tenho)
    if int(meses) != meses or meses <= 0:
        raise ValueError(f"meses inválido: {meses}")
    falta = max(v - j, Decimal(0))
    out = {"valor": _eur(v), "ja_tenho": _eur(j), "falta": _eur(falta), "meses": int(meses),
           "necessario_por_mes": _eur(falta / int(meses)),
           "pressupostos": "sem juros; depósitos mensais iguais"}
    if mensal_disponivel is not None:
        m = _pos("mensal_disponivel", mensal_disponivel, zero_ok=False)
        out.update({
            "mensal_disponivel": _eur(m),
            "juntaria_no_prazo": _eur(j + m * int(meses)),
            "defice_total": _eur(max(falta - m * int(meses), Decimal(0))),
            "defice_por_mes": _eur(max(falta / int(meses) - m, Decimal(0))),
            "meses_necessarios": math.ceil(falta / m) if falta > 0 else 0,
        })
    return out


def juros_compostos(deposito_mensal: float, taxa_anual: float, anos: float, capital_inicial: float = 0) -> dict:
    """Valor final com depósito mensal e capitalização mensal (depósito no fim de cada mês)."""
    p, c = _pos("deposito_mensal", deposito_mensal), _pos("capital_inicial", capital_inicial)
    t, a = _taxa("taxa_anual", taxa_anual), _pos("anos", anos, zero_ok=False)
    n = int(round(a * 12))
    if n <= 0:
        raise ValueError("prazo curto demais")
    r = t / 12
    if r == 0:
        final = c + p * n
    else:
        f = (1 + r) ** n
        final = c * f + p * (f - 1) / r
    depositado = c + p * n
    return {"depositado": _eur(depositado), "valor_final": _eur(final), "juros": _eur(final - depositado), "meses": n,
            "pressupostos": f"taxa nominal {float(t * 100)}% ao ano, capitalização mensal, depósitos no fim do mês, "
                            "sem impostos nem comissões"}


def custo_credito(montante: float, taxa_anual_nominal: float, prestacoes: int) -> dict:
    """Prestação e custo total (sistema francês, taxa nominal). NÃO é a TAEG: esta inclui comissões e seguros."""
    m, t = _pos("montante", montante, zero_ok=False), _taxa("taxa_anual_nominal", taxa_anual_nominal)
    if int(prestacoes) != prestacoes or prestacoes <= 0:
        raise ValueError(f"prestacoes inválido: {prestacoes}")
    n = int(prestacoes)
    r = t / 12
    pmt = m / n if r == 0 else m * r / (1 - (1 + r) ** -n)
    total = pmt * n
    return {"montante": _eur(m), "prestacoes": n, "prestacao_mensal": _eur(pmt), "total_a_pagar": _eur(total),
            "juros": _eur(total - m),
            "pressupostos": f"taxa nominal {float(t * 100)}% ao ano ({_eur(r * 100)}% ao mês), prestações iguais, "
                            "sem comissões, impostos nem seguros; a TAEG real pode ser superior. "
                            "Total = prestação exata x nº de prestações."}


def efeito_inflacao(valor: float, taxa_inflacao: float, anos: float) -> dict:
    """Poder de compra de `valor` daqui a `anos` com inflação constante."""
    v, t, a = _pos("valor", valor, zero_ok=False), _taxa("taxa_inflacao", taxa_inflacao), _pos("anos", anos)
    poder = v / ((1 + t) ** _d(a))
    return {"valor": _eur(v), "poder_de_compra_futuro": _eur(poder), "perda": _eur(v - poder),
            "pressupostos": f"inflação constante de {float(t * 100)}% ao ano (exemplo, não previsão)"}


def salario_liquido(bruto: float, taxa_ss: float = 0.11) -> dict:
    """Bruto -> após Segurança Social. A retenção de IRS NÃO é calculada (depende de situação pessoal e tabelas).
    taxa_ss=0.11 (11 %) vem do USE_CASES (UC-17): POR VERIFICAR na Segurança Social."""
    b, s = _pos("bruto", bruto, zero_ok=False), _taxa("taxa_ss", taxa_ss)
    ss = b * s
    return {"bruto": _eur(b), "seguranca_social": _eur(ss), "apos_seguranca_social": _eur(b - ss),
            "retencao_irs": None,
            "pressupostos": f"Segurança Social a {float(s * 100)}% (trabalhador); retenção de IRS não calculada: "
                            "confirmar tabelas no Portal das Finanças"}
