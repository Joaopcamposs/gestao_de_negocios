"""Módulo de schemas de entrada/saída para CreditCard."""

from uuid import UUID

from pydantic import BaseModel

from shared_core.entrypoints.schemas.base import ReadAuditSchema


class CreateCreditCardSchema(BaseModel):
    """Schema para adição de cartão de crédito."""

    number: str
    expiry: str
    cvv: str
    cpf: str
    holder_name: str


class ReadCreditCardSchema(ReadAuditSchema):
    """Schema de leitura de cartão de crédito (dados descriptografados)."""

    id: UUID
    user_id: UUID
    number: str
    expiry: str
    cvv: str
    cpf: str
    holder_name: str
