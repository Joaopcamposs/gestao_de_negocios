"""Mapeamento ORM da tabela legal_case no contexto advogado."""

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Index,
    String,
    Table,
    Text,
    text,
    UUID,
)

from infra.database import mapper_registry
from services.lawyer.domain.aggregate.legal_case import LegalCase

legal_case = Table(
    "legal_case",
    mapper_registry.metadata,
    Column("id", UUID, primary_key=True),
    Column("company", UUID, nullable=False),
    Column("case_number", String(100), nullable=False),
    Column("client_name", String(255), nullable=False),
    Column("description", Text, nullable=True),
    Column("status", String(50), nullable=False, default="open"),
    Column("open_date", Date, nullable=True),
    Column("notes", Text, nullable=True),
    Column("active", Boolean, nullable=False, default=True),
    Column("created_at", DateTime(timezone=True), nullable=True),
    Column("created_by", UUID, nullable=True),
    Column("updated_at", DateTime(timezone=True), nullable=True),
    Column("updated_by", UUID, nullable=True),
    Column("deleted_at", DateTime(timezone=True), nullable=True),
    Column("deleted_by", UUID, nullable=True),
    Index(
        "ix_legal_case_number_company_not_deleted",
        "case_number",
        "company",
        unique=True,
        postgresql_where=text("deleted_at IS NULL"),
    ),
)

legal_case_mapper = mapper_registry.map_imperatively(LegalCase, legal_case)
