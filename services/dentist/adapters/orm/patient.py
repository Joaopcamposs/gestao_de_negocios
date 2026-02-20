"""Mapeamento ORM da tabela patient no contexto dentista."""

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
from services.dentist.domain.aggregate.patient import Patient

patient = Table(
    "patient",
    mapper_registry.metadata,
    Column("id", UUID, primary_key=True),
    Column("company", UUID, nullable=False),
    Column("name", String(255), nullable=False),
    Column("cpf", String(14), nullable=False),
    Column("phone", String(20), nullable=True),
    Column("birth_date", Date, nullable=True),
    Column("notes", Text, nullable=True),
    Column("active", Boolean, nullable=False, default=True),
    Column("created_at", DateTime(timezone=True), nullable=True),
    Column("created_by", UUID, nullable=True),
    Column("updated_at", DateTime(timezone=True), nullable=True),
    Column("updated_by", UUID, nullable=True),
    Column("deleted_at", DateTime(timezone=True), nullable=True),
    Column("deleted_by", UUID, nullable=True),
    Index(
        "ix_patient_cpf_company_not_deleted",
        "cpf",
        "company",
        unique=True,
        postgresql_where=text("deleted_at IS NULL"),
    ),
)

patient_mapper = mapper_registry.map_imperatively(Patient, patient)
