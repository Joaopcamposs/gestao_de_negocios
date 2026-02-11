"""Mapeamento ORM da tabela patient no contexto dentista."""

from sqlalchemy import UUID, Boolean, Column, Date, Index, String, Table, Text, text

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
    Column("deleted", Boolean, nullable=False, default=False),
    Index(
        "ix_patient_cpf_company_deleted",
        "cpf",
        "company",
        unique=True,
        postgresql_where=text("deleted = false"),
    ),
)

patient_mapper = mapper_registry.map_imperatively(Patient, patient)
