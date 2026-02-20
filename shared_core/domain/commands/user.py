"""Módulo de comandos do domínio User."""

from dataclasses import dataclass
from uuid import UUID

from messagebus.messagebus import Command


@dataclass
class CreateUser(Command):
    """Comando para criar um novo usuário."""

    company: UUID
    email: str
    cpf: str
    password: str
    active: bool = True
    admin: bool = False
    is_owner: bool = False
    name: str | None = None


@dataclass
class UpdateUser(Command):
    """Comando para atualizar um usuário existente."""

    email: str
    new_email: str | None = None
    new_password: str | None = None
    new_active: bool | None = None
    new_admin: bool | None = None
    new_name: str | None = None
    new_street: str | None = None
    new_number: str | None = None
    new_zip_code: str | None = None
    new_district: str | None = None
    new_city: str | None = None
    new_state: str | None = None
    new_country: str | None = None


@dataclass
class DeleteUser(Command):
    """Comando para excluir um usuário."""

    email: str
