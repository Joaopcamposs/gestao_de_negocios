"""Módulo de eventos do domínio LegalCase no contexto advogado."""

from dataclasses import dataclass
from uuid import UUID

from messagebus.messagebus import Event


@dataclass
class LegalCaseCreated(Event):
    """Evento emitido quando um processo jurídico é criado."""

    id: UUID
    company: UUID


@dataclass
class LegalCaseUpdated(Event):
    """Evento emitido quando um processo jurídico é atualizado."""

    id: UUID
    company: UUID


@dataclass
class LegalCaseDeleted(Event):
    """Evento emitido quando um processo jurídico é excluído."""

    id: UUID
    company: UUID
