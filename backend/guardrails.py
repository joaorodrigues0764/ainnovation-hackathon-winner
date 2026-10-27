"""Guardrails de âmbito (USE_CASES Bloco 3), deterministas, antes do LLM.

Não bloqueiam a resposta: acrescentam ao prompt uma instrução que prevalece sobre a
pergunta e as entidades oficiais para onde reencaminhar (citáveis como fontes).

    from guardrails import check_scope
    hits = check_scope(question)          # [] na maior parte das perguntas
    [h.kind for h in hits]                # ex.: ["investimento"]
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

CMVM = {"title": "CMVM — literacia financeira", "url": "https://www.cmvm.pt",
        "source": "Comissão do Mercado de Valores Mobiliários",
        "text": "entidade que supervisiona os investimentos e publica guias educativos sobre como investir e os seus riscos."}
BDP = {"title": "Portal do Cliente Bancário", "url": "https://clientebancario.bportugal.pt",
       "source": "Banco de Portugal",
       "text": "informação oficial sobre crédito, contas e comparação de produtos bancários; apoio a quem tem dificuldades em pagar créditos."}
DECO = {"title": "DECO — apoio ao consumidor", "url": "https://www.deco.proteste.pt",
        "source": "DECO",
        "text": "associação de defesa do consumidor com apoio a famílias sobre-endividadas."}
FINANCAS = {"title": "Portal das Finanças", "url": "https://www.portaldasfinancas.gov.pt",
            "source": "Autoridade Tributária",
            "text": "onde se entrega e consulta a declaração de IRS e se confirmam as regras e tabelas em vigor."}


@dataclass
class ScopeHit:
    kind: str
    instruction: str
    referrals: list[dict] = field(default_factory=list)


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


_INVEST = re.compile(
    r"\b(bitcoin|btc|ethereum|cripto\w*|crypto|forex|trading|day ?trading|etfs?|"
    r"bolsa de valores|fundos? de investimento|lucro rapido|ficar rico)\b"
    r"|\b(investir|comprar|melhores)\b.{0,40}\bacoes\b|\bacoes\b.{0,40}\b(investir|comprar|lucro|bolsa)\b"
    r"|\b(onde|em que|como) (devo |posso )?investir\b")

# pedidos para o agente FAZER algo por ele (não "como é que se faz")
_ACT = re.compile(
    r"\b(podes|pode|consegues|consegue|queria que)\b.{0,50}"
    r"\b(renegoci\w*|negoci\w*|tratar|tratas|submeter|entregar|preencher|alterar|cancelar|falar com o)\b"
    r"|\brenegoci\w* .{0,30}\bcomigo\b")
_ACT_CREDIT = re.compile(r"\b(credito|emprestimo|prestac\w*|taxa|contrato|banco|divida\w*)\b")
_ACT_TAX = re.compile(r"\b(irs|declarac\w*|financas|impost\w*)\b")

_PRODUCT = re.compile(
    r"\b(qual|que|quais)\b.{0,30}\b(melhor(es)?|recomendas|aconselhas|sugeres)\b.{0,40}"
    r"\b(bancos?|contas?|cartao|cartoes|credito|seguros?|depositos?|app)\b"
    r"|\b(recomenda|aconselha|sugere)\w*\b.{0,30}\b(um|uma|o|a)\b.{0,10}\b(banco|conta|cartao|seguro|deposito)\b"
    r"|\b(qual|que|quais)\b.{0,5}\b(bancos?|contas?|cartao|cartoes|seguros?|depositos?)\b.{0,40}"
    r"\b(recomendas|aconselhas|sugeres|e melhor|sao melhores)\b")


def check_scope(text: str) -> list[ScopeHit]:
    t = _norm(text)
    hits: list[ScopeHit] = []
    if _INVEST.search(t):
        hits.append(ScopeHit(
            "investimento",
            "A pergunta pede aconselhamento de investimento ou especulação. Recusa com educação "
            "e diz que está fora do teu âmbito. Não comentes ativos, ações ou criptomoedas concretos. "
            "Reencaminha para os materiais da CMVM e explica a importância de ter primeiro um fundo de emergência.",
            [CMVM]))
    if _ACT.search(t):
        refs = ([BDP, DECO] if _ACT_CREDIT.search(t) else []) + ([FINANCAS] if _ACT_TAX.search(t) else [])
        hits.append(ScopeHit(
            "acao_externa",
            "O utilizador pede que trates de um contrato, negociação ou declaração por ele. Esclarece que "
            "não tens capacidade legal nem técnica para isso. Responde a cada parte do pedido, reencaminha "
            "para a entidade certa e explica em termos gerais o que pode preparar antes de lá ir.",
            refs or [BDP, FINANCAS]))
    if _PRODUCT.search(t):
        hits.append(ScopeHit(
            "produto",
            "A pergunta pede para recomendares um banco ou produto concreto. Não recomendes nenhum. "
            "Explica critérios de comparação (comissões, TAEG, condições para jovens, ficha de "
            "informação normalizada) e sugere os comparadores oficiais do Portal do Cliente Bancário.",
            [BDP]))
    return hits
