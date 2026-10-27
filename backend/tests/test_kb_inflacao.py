"""Regressão do caso reportado: pergunta de inflação num chat sem histórico.

Usa a KB e o RAG reais, sem embeddings nem chamadas ao modelo externo.
"""
import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from rag import JOURNEYS, RAG  # noqa: E402


@pytest.fixture(scope="module")
def inflation_rag():
    return RAG(BACKEND / "kb", use_embeddings=False)


@pytest.mark.parametrize("journey", [None, *JOURNEYS])
@pytest.mark.parametrize("question,expected", [
    ("Sabes o que é inflação?", "bdp-inflacao.md"),
    ("O que é a inflação?", "bdp-inflacao.md"),
    ("Explica-me a inflação de forma simples.", "bdp-inflacao.md"),
    ("O que é o IPC?", "bdp-inflacao.md"),
    ("Porque é que o mesmo dinheiro compra menos coisas?", "bdp-inflacao-poder-compra.md"),
    ("Se o meu salário subir menos do que os preços, perco poder de compra?", "bdp-inflacao-poder-compra.md"),
    ("O que é um cabaz de compras?", "bce-inflacao-cabaz.md"),
    ("Porque é que cada pessoa sente a inflação de forma diferente?", "bce-inflacao-cabaz.md"),
])
def test_inflacao_disponivel_sem_contexto_anterior(inflation_rag, journey, question, expected):
    hits = inflation_rag.retrieve(question, journey=journey)
    assert expected in [hit["chunk"].file for hit in hits]


@pytest.mark.parametrize("journey", [None, *JOURNEYS])
def test_chat_novo_tem_contexto_citavel_de_inflacao(inflation_rag, journey):
    prepared = inflation_rag._prepare(
        "Sabes o que é inflação?", journey, None, None, 5, [], None, None, False,
    )
    assert prepared is not None
    hits, messages, sources = prepared
    assert any(hit["chunk"].file == "bdp-inflacao.md" for hit in hits)
    assert any(source["url"].endswith("/inflacao-o-que-e") for source in sources)
    assert [message["role"] for message in messages] == ["system", "user"]
    assert "subida generalizada" in messages[-1]["content"]
