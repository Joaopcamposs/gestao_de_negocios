"""Módulo do value object Address."""

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class Address:
    """
    Value object imutável que representa um endereço completo.

    Todos os campos são obrigatórios, exceto complement.
    Sendo imutável (frozen), garante que o endereço não seja alterado
    acidentalmente após a criação — uma nova instância deve ser criada.

    Attributes:
        street: Logradouro (rua, avenida, etc.).
        number: Número do imóvel.
        zip_code: CEP no formato de 8 dígitos.
        district: Bairro.
        city: Cidade.
        state: Estado (sigla ou nome completo).
        country: País.
        complement: Complemento do endereço (apto, sala, bloco etc.) — opcional.
    """

    street: str
    number: str
    zip_code: str
    district: str
    city: str
    state: str
    country: str
    complement: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        """
        Converte o endereço para dicionário.

        Returns:
            Dicionário com todos os campos do endereço.
        """
        return {
            "street": self.street,
            "number": self.number,
            "zip_code": self.zip_code,
            "district": self.district,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "complement": self.complement,
        }
