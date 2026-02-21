"""Testes unitários para libs/basic_types.py.

Cobre os tipos básicos CPF, CNPJ e Email utilizados no sistema.
"""

import pytest

from libs.basic_types import CNPJ, CPF, Email


class TestCPF:
    """Testes para o tipo básico CPF."""

    def test_valid_cpf(self) -> None:
        """Testa criação de CPF válido."""
        valid = CPF.generate()
        cpf = CPF(valid)
        assert cpf.cpf == CPF.digits_only(valid)

    def test_invalid_cpf(self) -> None:
        """Testa que CPF inválido levanta ValueError."""
        with pytest.raises(ValueError, match="CPF inválido"):
            CPF("00000000000")

    def test_digits_only(self) -> None:
        """Testa extração de apenas dígitos do CPF formatado."""
        assert CPF.digits_only("123.456.789-09") == "12345678909"

    def test_generate(self) -> None:
        """Testa que generate retorna um CPF válido com 11 dígitos."""
        generated = CPF.generate()
        assert len(CPF.digits_only(generated)) == 11

    def test_str(self) -> None:
        """Testa representação string do CPF."""
        valid = CPF.generate()
        cpf = CPF(valid)
        assert str(cpf) == cpf.cpf


class TestCNPJ:
    """Testes para o tipo básico CNPJ."""

    def test_cnpj_with_value(self) -> None:
        """Testa CNPJ com valor válido remove formatação."""
        cnpj = CNPJ("12.345.678/0001-00")
        assert cnpj == "12345678000100"

    def test_cnpj_none(self) -> None:
        """Testa CNPJ com None retorna None."""
        result = CNPJ(None)
        assert result is None

    def test_cnpj_empty_string(self) -> None:
        """Testa CNPJ com string vazia retorna None."""
        result = CNPJ("")
        assert result is None

    def test_cnpj_digits_only(self) -> None:
        """Testa extração de dígitos do CNPJ formatado."""
        assert CNPJ.digits_only("12.345.678/0001-00") == "12345678000100"


class TestEmailNonString:
    """Testes para Email com valores não-string."""

    def test_email_with_non_string_returns_none(self) -> None:
        """Verifica que Email retorna None quando recebe valor não-string."""
        result = Email(123)  # type: ignore[arg-type]
        assert result is None


class TestEmail:
    """Testes para o tipo básico Email."""

    def test_email_lowercase(self) -> None:
        """Testa que Email converte para lowercase automaticamente."""
        email = Email("Test@Example.COM")
        assert email == "test@example.com"

    def test_email_string(self) -> None:
        """Testa criação com string normal já em lowercase."""
        email = Email("user@test.com")
        assert email == "user@test.com"
