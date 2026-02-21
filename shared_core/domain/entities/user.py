"""Módulo da entidade de leitura User."""

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from messagebus.entities import AuditBase, UserBase
from shared_core.domain.value_objects.address import Address
from shared_core.security import UserSecurity


@dataclass(kw_only=True)
class User(AuditBase, UserBase, UserSecurity):
    """
    Entidade de leitura que representa um usuário.

    Os campos de endereço são armazenados de forma plana para compatibilidade
    com o mapeamento ORM. O endereço é exposto como value object via propriedade.
    """

    id: UUID
    company: UUID
    email: str
    cpf: str
    name: str
    phone: str
    street: str
    number: str
    zip_code: str
    district: str
    city: str
    state: str
    country: str
    admin: bool
    complement: str | None = None
    is_owner: bool = False
    birth_date: date | None = None

    @property
    def address(self) -> Address:
        """Retorna o endereço como value object imutável."""
        return Address(
            street=self.street,
            number=self.number,
            zip_code=self.zip_code,
            district=self.district,
            city=self.city,
            state=self.state,
            country=self.country,
            complement=self.complement,
        )


@dataclass(kw_only=True)
class PublicUser(UserSecurity):
    """Entidade de leitura que representa um usuário público (dados criptografados)."""

    id: UUID
    company: UUID
    active: bool
    email_encrypted: bytes
    email_hash: str
