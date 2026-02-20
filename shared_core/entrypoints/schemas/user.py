"""Módulo de schemas de entrada/saída para User."""

from uuid import UUID

from pydantic import BaseModel

from shared_core.entrypoints.schemas.base import ReadAuditSchema


class CreateUserSchema(BaseModel):
    """Schema para criação de usuário."""

    email: str
    password: str
    cpf: str
    active: bool
    admin: bool
    name: str | None = None


class UpdateUserSchema(BaseModel):
    """Schema para atualização de usuário."""

    email: str
    new_email: str | None = None
    new_password: str | None = None
    new_cpf: str | None = None
    new_active: bool | None = None
    new_admin: bool | None = None
    new_name: str | None = None
    new_street: str | None = None
    new_number: str | None = None
    new_zip_code: str | None = None
    new_district: str | None = None
    new_city: str | None = None
    new_state: str | None = None
    new_country: str | None = None


class ReadUserSchema(ReadAuditSchema):
    """Schema de leitura de usuário."""

    id: UUID
    company: UUID
    email: str
    cpf: str
    active: bool
    admin: bool
    is_owner: bool = False
    name: str | None = None
    street: str | None = None
    number: str | None = None
    zip_code: str | None = None
    district: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
