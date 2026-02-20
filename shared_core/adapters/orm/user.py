"""Mapeamento ORM da tabela user."""

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    LargeBinary,
    String,
    Table,
    text,
    UUID,
)

from shared_core.domain.aggregate.user import PublicUser, User
from infra.database import mapper_registry

user = Table(
    "user",
    mapper_registry.metadata,
    Column("id", UUID, primary_key=True),
    Column("name", String(255), nullable=True),
    Column("email", String(255), nullable=False),
    Column("password_hash", String, nullable=False, key="_password_hash"),
    Column("cpf", String(11), nullable=False),
    Column("active", Boolean, nullable=False),
    Column("admin", Boolean, nullable=False),
    Column("is_owner", Boolean, nullable=False, default=False),
    Column("company", UUID, ForeignKey("company.id"), nullable=False),
    Column("street", String(255), nullable=True),
    Column("number", String(20), nullable=True),
    Column("zip_code", String(10), nullable=True),
    Column("district", String(255), nullable=True),
    Column("city", String(255), nullable=True),
    Column("state", String(100), nullable=True),
    Column("country", String(100), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=True),
    Column("created_by", UUID, nullable=True),
    Column("updated_at", DateTime(timezone=True), nullable=True),
    Column("updated_by", UUID, nullable=True),
    Column("deleted_at", DateTime(timezone=True), nullable=True),
    Column("deleted_by", UUID, nullable=True),
    Index(
        "ix_user_email_not_deleted",
        "email",
        unique=True,
        postgresql_where=text("deleted_at IS NULL"),
    ),
)
user_mapper = mapper_registry.map_imperatively(User, user)

public_user = Table(
    "public_user",
    mapper_registry.metadata,
    Column("id", UUID, primary_key=True),
    Column("company", UUID, nullable=False),
    Column("email_encrypted", LargeBinary, nullable=False),
    Column("email_hash", String(64), nullable=False),
    Column("password_hash", String(128), nullable=False, key="_password_hash"),
    Column("active", Boolean, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=True),
    Column("created_by", UUID, nullable=True),
    Column("updated_at", DateTime(timezone=True), nullable=True),
    Column("updated_by", UUID, nullable=True),
    Column("deleted_at", DateTime(timezone=True), nullable=True),
    Column("deleted_by", UUID, nullable=True),
    Index(
        "ix_public_user_email_not_deleted",
        "email_hash",
        unique=True,
        postgresql_where=text("deleted_at IS NULL"),
    ),
    Index("ix_public_user_email_hash_company", "email_hash", "company"),
    schema="public",
)
public_user_mapper = mapper_registry.map_imperatively(PublicUser, public_user)
