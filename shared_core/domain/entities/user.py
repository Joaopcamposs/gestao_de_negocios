"""Módulo da entidade de leitura User."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from messagebus.entities import UserBase
from shared_core.security import UserSecurity


@dataclass(kw_only=True)
class User(UserBase, UserSecurity):
    """Entidade de leitura que representa um usuário."""

    id: UUID
    company: UUID
    email: str
    cpf: str
    active: bool
    admin: bool
    deleted_at: datetime | None = None


@dataclass(kw_only=True)
class PublicUser(UserSecurity):
    """Entidade de leitura que representa um usuário público (dados criptografados)."""

    id: UUID
    company: UUID
    active: bool
    email_encrypted: bytes
    email_hash: str
