"""Módulo de schemas de entrada/saída para Patient no contexto dentista."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class CreatePatientSchema(BaseModel):
    """Schema para criação de paciente."""

    name: str
    cpf: str
    phone: str | None = None
    birth_date: date | None = None
    notes: str | None = None


class UpdatePatientSchema(BaseModel):
    """Schema para atualização de paciente."""

    cpf: str
    new_name: str | None = None
    new_phone: str | None = None
    new_birth_date: date | None = None
    new_notes: str | None = None


class ReadPatientSchema(BaseModel):
    """Schema de leitura de paciente."""

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
