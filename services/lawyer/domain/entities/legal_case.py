"""Módulo da entidade de leitura LegalCase no contexto advogado."""

from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

from services.lawyer.domain.value_objects.enums import LegalCaseStatus


@dataclass(frozen=True)
class LegalCase:
    """Entidade de leitura que representa um processo jurídico."""

    id: UUID
    company: UUID
    case_number: str
    client_name: str
    active: bool = True
    deleted_at: datetime | None = None
    deleted_by: UUID | None = None
    created_at: datetime | None = None
    created_by: UUID | None = None
    updated_at: datetime | None = None
    updated_by: UUID | None = None
    description: str | None = None
    status: LegalCaseStatus = LegalCaseStatus.OPEN
    open_date: date | None = None
    notes: str | None = None
