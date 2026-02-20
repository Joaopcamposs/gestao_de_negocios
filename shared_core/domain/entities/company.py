"""Módulo da entidade de leitura Company."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from messagebus.entities import AuditReadBase


@dataclass(frozen=True, kw_only=True)
class Company(AuditReadBase):
    """Entidade de leitura que representa uma empresa."""

    id: UUID
    legal_name: str
    responsible_name: str
    email: str
    cpf: str
    trade_name: str | None = None
    cnpj: str | None = None
    payment_up_to_date: bool = True
    last_payment_date: datetime | None = None
