"""Módulo de comandos do domínio User."""

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from messagebus.messagebus import Command
from shared_core.domain.value_objects.address import Address


@dataclass
class CreateUser(Command):
    """Comando para criar um novo usuário."""

    company: UUID
    email: str
    cpf: str
    password: str
    name: str
    phone: str
    address: Address
    active: bool = True
    admin: bool = False
    is_owner: bool = False
    birth_date: date | None = None


@dataclass
class UpdateUser(Command):
    """Comando para atualizar um usuário existente."""

    email: str
    new_email: str | None = None
    new_password: str | None = None
    new_active: bool | None = None
    new_admin: bool | None = None
    new_name: str | None = None
    new_phone: str | None = None
    new_birth_date: date | None = None
    new_address: Address | None = None


@dataclass
class DeleteUser(Command):
    """Comando para excluir um usuário."""

    email: str
