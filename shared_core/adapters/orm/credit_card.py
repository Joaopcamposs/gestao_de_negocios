"""Mapeamento ORM da tabela credit_card."""

from sqlalchemy import Column, DateTime, ForeignKey, LargeBinary, Table, UUID

from shared_core.domain.aggregate.credit_card import CreditCard
from infra.database import mapper_registry

credit_card = Table(
    "credit_card",
    mapper_registry.metadata,
    Column("id", UUID, primary_key=True),
    Column("user_id", UUID, ForeignKey("user.id"), nullable=False),
    Column("card_key_encrypted", LargeBinary, nullable=False),
    Column("number_encrypted", LargeBinary, nullable=False),
    Column("expiry_encrypted", LargeBinary, nullable=False),
    Column("cvv_encrypted", LargeBinary, nullable=False),
    Column("cpf_encrypted", LargeBinary, nullable=False),
    Column("holder_name_encrypted", LargeBinary, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=True),
    Column("created_by", UUID, nullable=True),
    Column("updated_at", DateTime(timezone=True), nullable=True),
    Column("updated_by", UUID, nullable=True),
    Column("deleted_at", DateTime(timezone=True), nullable=True),
    Column("deleted_by", UUID, nullable=True),
)

credit_card_mapper = mapper_registry.map_imperatively(CreditCard, credit_card)
