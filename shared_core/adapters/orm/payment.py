"""Mapeamento ORM da tabela payment."""

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, Table, UUID

from shared_core.domain.aggregate.payment import Payment
from infra.database import mapper_registry

payment = Table(
    "payment",
    mapper_registry.metadata,
    Column("id", UUID, primary_key=True),
    Column("company", UUID, ForeignKey("company.id"), nullable=False),
    Column("amount", Numeric(10, 2), nullable=False),
    Column("due_date", DateTime(timezone=True), nullable=False),
    Column("paid_at", DateTime(timezone=True), nullable=True),
    Column("status", String(20), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=True),
    Column("created_by", UUID, nullable=True),
    Column("updated_at", DateTime(timezone=True), nullable=True),
    Column("updated_by", UUID, nullable=True),
    Column("deleted_at", DateTime(timezone=True), nullable=True),
    Column("deleted_by", UUID, nullable=True),
)

payment_mapper = mapper_registry.map_imperatively(Payment, payment)
