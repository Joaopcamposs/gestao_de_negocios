"""Módulo da entidade de leitura Company."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class Company:
    """Entidade de leitura que representa uma empresa."""

    id: UUID
    legal_name: str
    responsible_name: str
    email: str
    cpf: str
    active: bool
    deleted_at: datetime | None = None
    deleted_by: UUID | None = None
    created_at: datetime | None = None
    created_by: UUID | None = None
    updated_at: datetime | None = None
    updated_by: UUID | None = None
    trade_name: str | None = None
    cnpj: str | None = None
