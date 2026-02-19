"""Módulo da entidade de leitura Patient no contexto dentista."""

from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID


@dataclass(frozen=True)
class Patient:
    """Entidade de leitura que representa um paciente."""

    id: UUID
    company: UUID
    name: str
    cpf: str
    active: bool = True
    deleted_at: datetime | None = None
    deleted_by: UUID | None = None
    created_at: datetime | None = None
    created_by: UUID | None = None
    updated_at: datetime | None = None
    updated_by: UUID | None = None
    phone: str | None = None
    birth_date: date | None = None
    notes: str | None = None
