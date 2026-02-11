"""Mapeamento ORM da tabela legal_case no contexto advogado."""

from sqlalchemy import UUID, Boolean, Column, Date, Index, String, Table, Text, text

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
    Column("deleted", Boolean, nullable=False, default=False),
    Index(
        "ix_legal_case_number_company_deleted",
        "case_number",
        "company",
        unique=True,
        postgresql_where=text("deleted = false"),
    ),
)

legal_case_mapper = mapper_registry.map_imperatively(LegalCase, legal_case)
