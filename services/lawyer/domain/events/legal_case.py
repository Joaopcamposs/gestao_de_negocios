"""Módulo de eventos do domínio LegalCase no contexto advogado."""

from dataclasses import dataclass
from uuid import UUID

from messagebus.entities import AuditableEvent
from messagebus.messagebus import Event


@dataclass(kw_only=True)
class LegalCaseCreated(AuditableEvent, Event):
    """Evento emitido quando um processo jurídico é criado."""

    id: UUID
    company: UUID


@dataclass(kw_only=True)
class LegalCaseUpdated(AuditableEvent, Event):
    """Evento emitido quando um processo jurídico é atualizado."""

    id: UUID
    company: UUID


@dataclass(kw_only=True)
class LegalCaseDeleted(AuditableEvent, Event):
    """Evento emitido quando um processo jurídico é excluído."""

    id: UUID
    company: UUID
