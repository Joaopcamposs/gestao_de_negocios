"""Módulo de comandos do domínio LegalCase no contexto advogado."""

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from messagebus.messagebus import Command


@dataclass
class CreateLegalCase(Command):
    """Comando para criar um novo processo jurídico."""

    company: UUID
    case_number: str
    client_name: str
    description: str | None = None
    status: str = "open"
    open_date: date | None = None
    notes: str | None = None


@dataclass
class UpdateLegalCase(Command):
    """Comando para atualizar um processo jurídico existente."""

    company: UUID
    case_number: str
    new_client_name: str | None = None
    new_description: str | None = None
    new_status: str | None = None
    new_notes: str | None = None


@dataclass
class DeleteLegalCase(Command):
    """Comando para excluir um processo jurídico."""

    company: UUID
    case_number: str
