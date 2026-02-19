"""Módulo da entidade de leitura LegalCase no contexto advogado."""

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from messagebus.entities import AuditBase
from services.lawyer.domain.value_objects.enums import LegalCaseStatus


@dataclass(kw_only=True)
class LegalCase(AuditBase):
    """Entidade de leitura que representa um processo jurídico."""

    id: UUID
    company: UUID
    case_number: str
    client_name: str
    description: str | None = None
    status: LegalCaseStatus = LegalCaseStatus.OPEN
    open_date: date | None = None
    notes: str | None = None
