"""Módulo da entidade de leitura Patient no contexto dentista."""

from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(frozen=True)
class Patient:
    """Entidade de leitura que representa um paciente."""

    id: UUID
    company: UUID
    name: str
    cpf: str
    deleted: bool
    phone: str | None = None
    birth_date: date | None = None
    notes: str | None = None
