"""Módulo de schemas de entrada/saída para User."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CreateUserSchema(BaseModel):
    """Schema para criação de usuário."""

    email: str
    password: str
    cpf: str
    active: bool
    admin: bool


class UpdateUserSchema(BaseModel):
    """Schema para atualização de usuário."""

    email: str
    new_email: str | None = None
    new_password: str | None = None
    new_cpf: str | None = None
    new_active: bool | None = None
    new_admin: bool | None = None


class ReadUserSchema(BaseModel):
    """Schema de leitura de usuário."""

    id: UUID
    company: UUID
    email: str
    cpf: str
    active: bool
    admin: bool
    deleted_at: datetime | None = None
    deleted_by: UUID | None = None
    created_at: datetime | None = None
    created_by: UUID | None = None
    updated_at: datetime | None = None
    updated_by: UUID | None = None
