"""Módulo da entidade de leitura Patient no contexto dentista."""

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from messagebus.entities import AuditReadBase


@dataclass(frozen=True, kw_only=True)
class Patient(AuditReadBase):
    """Entidade de leitura que representa um paciente."""

    id: UUID
    company: UUID
    name: str
    cpf: str
    phone: str | None = None
    birth_date: date | None = None
    notes: str | None = None
