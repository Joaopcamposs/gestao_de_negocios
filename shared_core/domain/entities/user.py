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


@dataclass(kw_only=True)
class PublicUser(UserSecurity):
    """Entidade de leitura que representa um usuário público (dados criptografados)."""

    id: UUID
    company: UUID
    active: bool
    email_encrypted: bytes
    email_hash: str
