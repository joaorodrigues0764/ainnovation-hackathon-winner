import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from privacy import mask_pii


def test_iban_pt_com_e_sem_espacos():
    r = mask_pii("O meu IBAN é PT50 0035 0123 45678901234 56 e PT50003501234567890123456")
    assert "PT50" not in r.text and r.found == {"IBAN": 2}


def test_l2_iban_e_codigo():
    r = mask_pii("O meu IBAN é PT50003501234567890123456 e o código do cartão é 1234, ajuda-me")
    assert "1234" not in r.text and "PT50" not in r.text
    assert r.text.count("[IBAN]") == 1 and "[CODIGO]" in r.text


def test_cartao_so_com_luhn():
    assert mask_pii("cartão 4539 1488 0343 6467").found == {"CARTAO": 1}   # Luhn válido
    assert "CARTAO" not in mask_pii("número 4539 1488 0343 6468").found    # Luhn inválido


def test_nove_digitos_e_telefone_351():
    r = mask_pii("O meu NIF é 123456789 e ligo de +351 912 345 678")
    assert r.text == "O meu NIF é [NIF_OU_TELEMOVEL] e ligo de [NIF_OU_TELEMOVEL]"


def test_email():
    assert mask_pii("escreve para ana.silva@exemplo.pt").text == "escreve para [EMAIL]"


def test_nao_mexe_em_perguntas_normais():
    for q in ["Recebo 400 € por mês, gasto 150 em transportes", "Quero 600 € em 8 meses e já tenho 120 €",
              "Telemóvel de 900 € em 12 prestações com TAEG de 18%", "o que é a inflação", "Ano de 2026, taxa 3,5%"]:
        r = mask_pii(q)
        assert r.text == q and r.found == {}, q


def test_found_nao_contem_valores():
    r = mask_pii("PT50003501234567890123456")
    assert all(isinstance(k, str) and isinstance(v, int) for k, v in r.found.items())
    assert "0035" not in str(r.found)


def test_vazio():
    assert mask_pii("").text == ""


def test_uc10_iban_ficticio_incompleto():
    r = mask_pii("O meu NIF é 123456789 e o meu IBAN é PT50 0000 1234 5678 9012 3. Podem ver o IRS Jovem?")
    assert r.text == "O meu NIF é [NIF_OU_TELEMOVEL] e o meu IBAN é [IBAN]. Podem ver o IRS Jovem?"
    assert r.found == {"IBAN": 1, "NIF_OU_TELEMOVEL": 1}
