import sys
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from judge import MAX_QUESTIONS, assess, clarify_instruction, parse  # noqa: E402


def test_parse_tolera_texto_a_volta():
    a = parse('Aqui vai:\n```json\n{"completa": false, "em_falta": ["prazo"], "perguntas": ["Em quantos meses?"], "motivo": "x"}\n```')
    assert a.complete is False and a.missing == ["prazo"] and a.questions == ["Em quantos meses?"]


def test_parse_limita_perguntas_e_ignora_lixo():
    a = parse('{"completa": false, "perguntas": ["a?", "", 3, "b?", "c?", "d?"]}')
    assert a.questions == ["a?", "b?", "c?"] and len(a.questions) == MAX_QUESTIONS


def test_incompleta_sem_perguntas_conta_como_completa():
    assert parse('{"completa": false, "perguntas": []}').complete is True


def test_completa_limpa_perguntas():
    a = parse('{"completa": true, "em_falta": ["x"], "perguntas": ["y?"]}')
    assert a.complete and a.missing == [] and a.questions == []


@pytest.mark.parametrize("bad", ["sem json", '{"completa": "talvez"}', "{partido"])
def test_parse_invalido_levanta(bad):
    with pytest.raises(ValueError):
        parse(bad)


def test_assess_falha_aberto_e_mede_tempo():
    def boom(messages):
        raise RuntimeError("rede")
    a = assess(boom, "Ganho 900 €", [], None, "salario")
    assert a.complete and a.error and a.ms >= 0


def test_assess_envia_pergunta_perfil_e_historico():
    seen = []

    def fake(messages):
        seen.append(messages)
        return NS(choices=[NS(message=NS(content='{"completa": true}'))])
    assess(fake, "e a 60 meses?", [{"role": "user", "content": "crédito de 8000 € a 9%"}],
           {"rendimento_liquido": 1100}, "credito")
    user = seen[0][1]["content"]
    assert "e a 60 meses?" in user and "crédito de 8000 € a 9%" in user and "1100" in user and "credito" in user


def test_instrucao_tem_as_perguntas_e_proibe_inventar():
    a = parse('{"completa": false, "em_falta": ["despesas fixas"], "perguntas": ["Quanto gastas em renda?"]}')
    txt = clarify_instruction(a)
    assert "Quanto gastas em renda?" in txt and "NÃO inventes" in txt and "despesas fixas" in txt
