"""Módulo de schemas de entrada/saída para Payment."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from shared_core.entrypoints.schemas.base import ReadAuditSchema


class CreatePaymentSchema(BaseModel):
    """Schema para criação de pagamento."""

    company: UUID
    amount: float
    due_date: datetime


class ReadPaymentSchema(ReadAuditSchema):
    """Schema de leitura de pagamento."""

    id: UUID
    company: UUID
    amount: float
    due_date: datetime
    status: str
    paid_at: datetime | None = None
