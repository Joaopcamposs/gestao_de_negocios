"""Módulo da entidade de leitura Company."""

from dataclasses import dataclass
from uuid import UUID

from messagebus.entities import AuditBase


@dataclass(kw_only=True)
class Company(AuditBase):
    """Entidade de leitura que representa uma empresa."""

    id: UUID
    legal_name: str
    responsible_name: str
    email: str
    cpf: str
    trade_name: str | None = None
    cnpj: str | None = None
