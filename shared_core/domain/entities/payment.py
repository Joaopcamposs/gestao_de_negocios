"""Módulo da entidade de leitura Payment."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from messagebus.entities import AuditReadBase


@dataclass(frozen=True, kw_only=True)
class Payment(AuditReadBase):
    """Entidade de leitura que representa um pagamento de empresa."""

    id: UUID
    company: UUID
    amount: float
    due_date: datetime
    status: str
    paid_at: datetime | None = None
