"""Módulo de schemas de entrada/saída para User."""

from datetime import date
from uuid import UUID

from pydantic import BaseModel

from shared_core.entrypoints.schemas.base import ReadAuditSchema


class AddressSchema(BaseModel):
    """Schema para representação de endereço."""

    street: str
    number: str
    zip_code: str
    district: str
    city: str
    state: str
    country: str
    complement: str | None = None

    def to_value_object(self):
        """Converte para o value object Address do domínio."""
        from shared_core.domain.value_objects.address import Address

        return Address(
            street=self.street,
            number=self.number,
            zip_code=self.zip_code,
            district=self.district,
            city=self.city,
            state=self.state,
            country=self.country,
            complement=self.complement,
        )


class CreateUserSchema(BaseModel):
    """Schema para criação de usuário."""

    email: str
    password: str
    cpf: str
    name: str
    phone: str
    address: AddressSchema
    active: bool = True
    admin: bool = False
    birth_date: date | None = None


class UpdateUserSchema(BaseModel):
    """Schema para atualização de usuário."""

    new_email: str | None = None
    new_password: str | None = None
    new_active: bool | None = None
    new_admin: bool | None = None
    new_name: str | None = None
    new_phone: str | None = None
    new_birth_date: date | None = None
    new_address: AddressSchema | None = None


class ReadAddressSchema(BaseModel):
    """Schema de leitura de endereço."""

    street: str
    number: str
    zip_code: str
    district: str
    city: str
    state: str
    country: str
    complement: str | None = None


class ReadUserSchema(ReadAuditSchema):
    """Schema de leitura de usuário."""

    id: UUID
    company: UUID
    email: str
    cpf: str
    name: str
    phone: str
    street: str
    number: str
    zip_code: str
    district: str
    city: str
    state: str
    country: str
    active: bool
    admin: bool
    complement: str | None = None
    is_owner: bool = False
    birth_date: date | None = None
