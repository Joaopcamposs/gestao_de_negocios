"""Módulo de eventos do domínio Patient no contexto dentista."""

from dataclasses import dataclass
from uuid import UUID

from messagebus.messagebus import Event


@dataclass
class PatientCreated(Event):
    """Evento emitido quando um paciente é criado."""

    id: UUID
    company: UUID


@dataclass
class PatientUpdated(Event):
    """Evento emitido quando um paciente é atualizado."""

    id: UUID
    company: UUID


@dataclass
class PatientDeleted(Event):
    """Evento emitido quando um paciente é excluído."""

    id: UUID
    company: UUID
