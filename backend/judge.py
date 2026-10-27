"""Juiz de completude (LLM-as-a-judge), antes da resposta.

Decide se a pergunta, com o histórico e o perfil, tem os dados necessários para uma resposta
personalizada (UC-01, UC-19, UC-20). Se faltar algo, a resposta cobre só o que os dados permitem e
termina com até 3 perguntas curtas, em vez de inventar valores.

Falha aberta: se o juiz der erro ou JSON inválido, considera-se completa e a resposta segue normal.

    from judge import assess, clarify_instruction
    a = assess(rag._complete, question, history, profile, journey)
    if not a.complete: instructions.append(clarify_instruction(a))
"""
from __future__ import annotations

import json
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from typing import Callable

MAX_QUESTIONS = 3
HISTORY_TURNS = 6

JUDGE_PROMPT = """Avalias se a mensagem de um jovem sobre dinheiro tem a informação necessária para uma resposta
personalizada e completa. NÃO respondes à pergunta.

Considera a PERGUNTA, o HISTÓRICO e o PERFIL: um dado que já esteja em qualquer um deles não está em falta.
Só falta um dado se, sem ele, a resposta ficasse genérica ou errada para esta pessoa. Na dúvida, está completa.
Dados essenciais, só quando a pessoa pede uma decisão ou uma conta para a sua própria situação:
- "quanto posso gastar em X", "quanto sobra", "quanto posso poupar": rendimento líquido mensal E despesas fixas mensais
- "quanto preciso de poupar por mês" para um objetivo: valor do objetivo E prazo
- "em quanto tempo junto" um valor: valor do objetivo E quanto consegue guardar por mês
- crédito ou prestação: montante, prazo E taxa
- fundo de emergência ("quanto devo ter"): despesas fixas mensais
- juros compostos: depósito, taxa E prazo
NÃO estão em falta (usa o valor óbvio e não perguntes): capital inicial ou valor já poupado (0), o tipo de taxa
(uma taxa dada conta como nominal anual), o montante do crédito quando a pessoa diz o preço do que quer comprar,
comissões, seguros ou outros encargos que a pessoa não referiu (a resposta já explica que a TAEG pode ser maior),
e qualquer dado que só tornaria a resposta mais exata mas que não muda a conta pedida.
Estão completas: perguntas sobre conceitos, regras, riscos, direitos, burlas, IRS em geral, e pedidos fora de âmbito.
Mensagens vagas sem objetivo ("ajuda-me com o meu dinheiro") estão incompletas: pergunta o objetivo e o rendimento.
Nunca peças NIF, IBAN, contactos, palavras-passe, nome ou morada.

Responde só com JSON, sem texto à volta:
{"completa": true ou false, "em_falta": ["dado em falta", ...], "perguntas": ["até 3 perguntas curtas, pt-PT, a tratar por tu"], "motivo": "uma frase"}"""


@dataclass
class Assessment:
    complete: bool = True
    missing: list[str] = field(default_factory=list)
    questions: list[str] = field(default_factory=list)
    reason: str = ""
    ms: int = 0
    error: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def _user_msg(question: str, history: list[dict], profile: dict | None, journey: str | None) -> str:
    hist = "\n".join(f"{t['role']}: {t['content'][:600]}" for t in history[-HISTORY_TURNS:]) or "(vazio)"
    return (f"JORNADA: {journey or 'não indicada'}\n"
            f"PERFIL: {json.dumps(profile or {}, ensure_ascii=False)}\n"
            f"HISTÓRICO:\n{hist}\n"
            f"PERGUNTA: {question}")


def parse(text: str) -> Assessment:
    """JSON do juiz → Assessment. Tolera texto à volta e campos em falta; levanta ValueError se não houver JSON."""
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        raise ValueError("o juiz não devolveu JSON")
    d = json.loads(m.group(0))
    complete = d.get("completa", True)
    if not isinstance(complete, bool):
        raise ValueError(f"'completa' inválido: {complete!r}")
    questions = [q.strip() for q in d.get("perguntas", []) if isinstance(q, str) and q.strip()][:MAX_QUESTIONS]
    missing = [x.strip() for x in d.get("em_falta", []) if isinstance(x, str) and x.strip()]
    if not complete and not questions:  # incompleta sem perguntas não serve para nada: segue como completa
        complete = True
    return Assessment(complete=complete, missing=missing if not complete else [],
                      questions=questions if not complete else [], reason=str(d.get("motivo", ""))[:300])


def assess(complete_fn: Callable, question: str, history: list[dict], profile: dict | None,
           journey: str | None) -> Assessment:
    """`complete_fn` é RAG._complete (mesmo modelo, mesmo ajuste de parâmetros)."""
    t0 = time.perf_counter()
    try:
        resp = complete_fn([{"role": "system", "content": JUDGE_PROMPT},
                            {"role": "user", "content": _user_msg(question, history, profile, journey)}])
        a = parse(resp.choices[0].message.content)
    except Exception as e:  # falha aberta: nunca impede a resposta
        print(f"[judge] erro, a seguir sem clarificação: {e!r}", file=sys.stderr)
        a = Assessment(error=str(e)[:200])
    a.ms = round((time.perf_counter() - t0) * 1000)
    return a


def clarify_instruction(a: Assessment) -> str:
    qs = "\n".join(f"  - {q}" for q in a.questions)
    return ("Faltam dados para uma resposta personalizada"
            + (f" ({'; '.join(a.missing)})" if a.missing else "") + ". "
            "Responde só ao que os dados e as fontes já permitem: podes usar as calculadoras com os valores que "
            "existem, dizendo que é uma referência. NÃO inventes nem suponhas os valores em falta. "
            "Antes do 'Próximo passo:', escreve 'Para te ajudar melhor, diz-me:' e uma lista com estas perguntas:\n"
            f"{qs}\nO 'Próximo passo:' é responder a essas perguntas.")
