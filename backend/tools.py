"""Calculadoras expostas ao LLM como tools (tool calling da OpenAI).

O LLM só escolhe a função e os argumentos; a conta é sempre feita em `calculators.py`.

    from tools import SCHEMAS, run_tool
    run_tool("custo_credito", '{"montante": 8000, "taxa_anual_nominal": 9, "prestacoes": 48}')
"""
from __future__ import annotations

import json

import calculators

_MISSING = "Se o utilizador não deu um valor necessário, não o inventes: pergunta-lho em vez de chamar a função."


def _fn(name: str, description: str, properties: dict, required: list[str]) -> dict:
    return {"type": "function", "function": {
        "name": name,
        "description": f"{description} {_MISSING}",
        "parameters": {"type": "object", "properties": properties, "required": required,
                       "additionalProperties": False},
    }}


def _num(description: str) -> dict:
    return {"type": "number", "description": description}


def _int(description: str) -> dict:
    return {"type": "integer", "description": description}


SCHEMAS = [
    _fn("custo_credito",
        "Prestação mensal, total a pagar e juros de um crédito com prestações iguais (taxa nominal). "
        "Usar para 'quanto pago por mês', 'quanto custa o crédito', 'e se for a N meses?'.",
        {"montante": _num("valor pedido em €"),
         "taxa_anual_nominal": _num("taxa nominal anual em percentagem (9 = 9%)"),
         "prestacoes": _int("número de prestações mensais")},
        ["montante", "taxa_anual_nominal", "prestacoes"]),
    _fn("objetivo_poupanca",
        "Quanto poupar por mês para juntar um valor num prazo (sem juros). Com mensal_disponivel, "
        "diz quanto junta, o défice e quantos meses precisa de facto.",
        {"valor": _num("valor total do objetivo em €"),
         "meses": _int("meses até ao objetivo"),
         "ja_tenho": _num("valor já poupado em € (0 se nada)"),
         "mensal_disponivel": _num("quanto consegue guardar por mês em €, se o disse")},
        ["valor", "meses"]),
    _fn("juros_compostos",
        "Valor final de depósitos mensais com juros compostos (capitalização mensal).",
        {"deposito_mensal": _num("depósito por mês em €"),
         "taxa_anual": _num("taxa anual em percentagem (3 = 3%)"),
         "anos": _num("prazo em anos"),
         "capital_inicial": _num("valor já depositado no início em € (0 se nada)")},
        ["deposito_mensal", "taxa_anual", "anos"]),
    _fn("orcamento",
        "Saldo do mês e divisão de referência 50/30/20 (necessidades/desejos/poupança).",
        {"entradas": _num("rendimento líquido do mês em €"),
         "gastos": _num("gastos do mês em € (0 se não disse)")},
        ["entradas", "gastos"]),
    _fn("salario_liquido",
        "Do salário bruto ao valor após Segurança Social (11%). Não calcula a retenção de IRS.",
        {"bruto": _num("salário bruto mensal em €")},
        ["bruto"]),
    _fn("efeito_inflacao",
        "Poder de compra de um valor daqui a N anos com inflação constante.",
        {"valor": _num("valor em €"),
         "taxa_inflacao": _num("inflação anual em percentagem (2 = 2%)"),
         "anos": _num("anos")},
        ["valor", "taxa_inflacao", "anos"]),
]

_FUNCS = {s["function"]["name"]: getattr(calculators, s["function"]["name"]) for s in SCHEMAS}


def run_tool(name: str, arguments: str | dict) -> dict:
    """Executa uma calculadora. Erros voltam como {"erro": ...} para o LLM pedir o valor certo."""
    if name not in _FUNCS:
        return {"erro": f"função desconhecida: {name}"}
    try:
        args = json.loads(arguments or "{}") if isinstance(arguments, str) else dict(arguments)
        return _FUNCS[name](**{k: v for k, v in args.items() if v is not None})
    except (ValueError, TypeError) as e:  # inclui JSON inválido e argumentos em falta/errados
        return {"erro": str(e)}
