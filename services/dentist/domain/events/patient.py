"""Módulo de eventos do domínio Patient no contexto dentista."""

from dataclasses import dataclass
from uuid import UUID

from messagebus.entities import AuditableEvent
from messagebus.messagebus import Event


@dataclass(kw_only=True)
class PatientCreated(AuditableEvent, Event):
    """Evento emitido quando um paciente é criado."""

    id: UUID
    company: UUID


@dataclass(kw_only=True)
class PatientUpdated(AuditableEvent, Event):
    """Evento emitido quando um paciente é atualizado."""

    id: UUID
    company: UUID


@dataclass(kw_only=True)
class PatientDeleted(AuditableEvent, Event):
    """Evento emitido quando um paciente é excluído."""

    id: UUID
    company: UUID
