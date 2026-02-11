"""Módulo de comandos do domínio Patient no contexto dentista."""

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from messagebus.messagebus import Command


@dataclass
class CreatePatient(Command):
    """Comando para criar um novo paciente."""

    company: UUID
    name: str
    cpf: str
    phone: str | None = None
    birth_date: date | None = None
    notes: str | None = None


@dataclass
class UpdatePatient(Command):
    """Comando para atualizar um paciente existente."""

    company: UUID
    cpf: str
    new_name: str | None = None
    new_phone: str | None = None
    new_birth_date: date | None = None
    new_notes: str | None = None


@dataclass
class DeletePatient(Command):
    """Comando para excluir um paciente."""

    company: UUID
    cpf: str
