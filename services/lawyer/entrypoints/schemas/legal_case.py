"""Módulo de schemas de entrada/saída para LegalCase no contexto advogado."""

from datetime import date
from uuid import UUID

from pydantic import BaseModel

from shared_core.entrypoints.schemas.base import ReadAuditSchema


class CreateLegalCaseSchema(BaseModel):
    """Schema para criação de processo jurídico."""

    case_number: str
    client_name: str
    description: str | None = None
    status: str = "open"
    open_date: date | None = None
    notes: str | None = None


class UpdateLegalCaseSchema(BaseModel):
    """Schema para atualização de processo jurídico."""

    case_number: str
    new_client_name: str | None = None
    new_description: str | None = None
    new_status: str | None = None
    new_notes: str | None = None


class ReadLegalCaseSchema(ReadAuditSchema):
    """Schema de leitura de processo jurídico."""

    id: UUID
    company: UUID
    case_number: str
    client_name: str
    description: str | None = None
    status: str = "open"
    open_date: date | None = None
    notes: str | None = None
