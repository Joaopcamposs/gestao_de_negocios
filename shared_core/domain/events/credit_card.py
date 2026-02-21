"""Módulo de eventos do domínio CreditCard."""

from dataclasses import dataclass
from uuid import UUID

from messagebus.entities import AuditableEvent
from messagebus.messagebus import Event


@dataclass(kw_only=True)
class CreditCardCreated(AuditableEvent, Event):
    """Evento emitido quando um cartão de crédito é criado."""

    id: UUID
    user_id: UUID


@dataclass(kw_only=True)
class CreditCardDeleted(AuditableEvent, Event):
    """Evento emitido quando um cartão de crédito é excluído."""

    id: UUID
    user_id: UUID
