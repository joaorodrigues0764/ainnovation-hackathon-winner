"""Máscara de dados sensíveis ANTES de o texto ir para o LLM (só privacidade).

Não guarda nem usa os dados: troca cada um por uma etiqueta e devolve apenas
CONTAGENS por tipo (nunca os valores). Leve: regex + saída rápida quando o
texto não tem dígitos nem '@'.

    from privacy import mask_pii
    r = mask_pii(question)
    llm_input = r.text        # texto mascarado
    r.found                   # ex.: {"IBAN": 1}  (para log/harness, sem valores)
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

# IBAN português: "PT50" + 21 dígitos (espaços/hífens tolerados). O teste do prefixo
# vem primeiro: se não houver PT50, não se gasta mais nada com o IBAN.
_IBAN_PT = re.compile(r"\bPT\s?50(?:[\s-]?\d){21}\b", re.I)
_NIB = re.compile(r"(?<!\d)(?:\d[\s-]?){20}\d(?!\d)")  # 21 dígitos soltos (NIB)
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_CARD = re.compile(r"(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)")  # 13–19 dígitos, valida com Luhn
_NINE = re.compile(r"(?<!\d)(?:\+?351[\s-]?)?(\d{3}[\s-]?\d{3}[\s-]?\d{3})(?!\d)")  # NIF / telemóvel
_SECRET = re.compile(
    r"(?i)\b(c[oó]digo|pin|cvv|cvc|password|palavra[- ]?passe|senha)\b([^\d\n]{0,25})(\d{3,8})(?!\d)"
)


@dataclass
class MaskResult:
    text: str
    found: dict[str, int] = field(default_factory=dict)


def _luhn(digits: str) -> bool:
    total, alt = 0, False
    for ch in reversed(digits):
        d = int(ch)
        if alt:
            d = d * 2 - 9 if d * 2 > 9 else d * 2
        total += d
        alt = not alt
    return total % 10 == 0


def mask_pii(text: str) -> MaskResult:
    found: dict[str, int] = {}

    def bump(kind: str) -> None:
        found[kind] = found.get(kind, 0) + 1

    if not text or not (any(c.isdigit() for c in text) or "@" in text):
        return MaskResult(text or "", found)

    def sub(pattern: re.Pattern, kind: str, s: str, check=None, repl=None) -> str:
        def fn(m: re.Match) -> str:
            if check and not check(m):
                return m.group(0)
            bump(kind)
            return repl(m) if repl else f"[{kind}]"
        return pattern.sub(fn, s)

    s = text
    if re.search(r"pt\s?50", s, re.I):                      # saída rápida do IBAN
        s = sub(_IBAN_PT, "IBAN", s)
    s = sub(_EMAIL, "EMAIL", s)
    s = sub(_NIB, "NIB", s)
    s = sub(_CARD, "CARTAO", s, check=lambda m: _luhn(re.sub(r"\D", "", m.group(0))))
    s = sub(_SECRET, "CODIGO", s, repl=lambda m: f"{m.group(1)}{m.group(2)}[CODIGO]")
    s = sub(_NINE, "NIF_OU_TELEMOVEL", s)
    return MaskResult(s, found)
