"""Módulo da entidade de leitura User."""

from dataclasses import dataclass
from uuid import UUID

from messagebus.entities import AuditBase, UserBase
from shared_core.security import UserSecurity


@dataclass(kw_only=True)
class User(AuditBase, UserBase, UserSecurity):
    """Entidade de leitura que representa um usuário."""

    id: UUID
    company: UUID
    email: str
    cpf: str
    admin: bool
    is_owner: bool = False
    name: str | None = None
    street: str | None = None
    number: str | None = None
    zip_code: str | None = None
    district: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None


@dataclass(kw_only=True)
class PublicUser(UserSecurity):
    """Entidade de leitura que representa um usuário público (dados criptografados)."""

    id: UUID
    company: UUID
    active: bool
    email_encrypted: bytes
    email_hash: str
