"""Módulo da entidade de leitura LegalCase no contexto advogado."""

from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(frozen=True)
class LegalCase:
    """Entidade de leitura que representa um processo jurídico."""

    id: UUID
    company: UUID
    case_number: str
    client_name: str
    deleted: bool
    description: str | None = None
    status: str = "open"
    open_date: date | None = None
    notes: str | None = None
