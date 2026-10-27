import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from guardrails import check_scope  # noqa: E402


def kinds(q):
    return [h.kind for h in check_scope(q)]


@pytest.mark.parametrize("q", [
    "Tenho 200 € de lado. Quais são as melhores ações para investir hoje para ter lucro rápido?",
    "Ou devo comprar Bitcoin?",
    "vale a pena meter dinheiro em cripto",
    "Onde devo investir os meus 500 €?",
])
def test_investimento(q):
    assert kinds(q) == ["investimento"]


def test_acao_externa_credito_e_irs_juntos():
    hits = check_scope("Tenho um crédito pessoal e as prestações estão muito altas. Podes renegociar a "
                       "taxa de juro comigo ou tratar da minha declaração de IRS no portal?")
    assert [h.kind for h in hits] == ["acao_externa"]
    urls = {r["url"] for r in hits[0].referrals}
    assert {"https://clientebancario.bportugal.pt", "https://www.deco.proteste.pt",
            "https://www.portaldasfinancas.gov.pt"} <= urls


@pytest.mark.parametrize("q", [
    "Qual é o melhor banco para abrir conta?",
    "Que cartão de crédito me recomendas?",
])
def test_produto(q):
    assert kinds(q) == ["produto"]


@pytest.mark.parametrize("q", [
    "Como se entrega o IRS?",                       # pergunta como fazer, não pede para fazer
    "Qual a diferença entre TAEG e TAN?",
    "Quero juntar 600 € em 6 meses para uma viagem",
    "Que ações devo tomar se recebi um SMS do banco a pedir o código?",
    "O IRS Jovem aplica-se a mim?",
    "Vale a pena pedir crédito para o carro?",
])
def test_perguntas_normais_passam(q):
    assert kinds(q) == []
