"""Módulo de eventos do domínio Payment."""

from dataclasses import dataclass
from uuid import UUID

from messagebus.entities import AuditableEvent
from messagebus.messagebus import Event


@dataclass(kw_only=True)
class PaymentCreated(AuditableEvent, Event):
    """Evento emitido quando um pagamento é criado."""

    id: UUID
    company: UUID


@dataclass(kw_only=True)
class PaymentUpdated(AuditableEvent, Event):
    """Evento emitido quando um pagamento é atualizado."""

    id: UUID
    company: UUID


@dataclass
class CompanyPaymentPaid(Event):
    """Evento emitido quando um pagamento de empresa é confirmado."""

    company: UUID
    payment_id: UUID


@dataclass
class CompanyPaymentOverdue(Event):
    """Evento emitido quando um pagamento de empresa está em atraso."""

    company: UUID


@dataclass
class CompanyAndUsersDeactivated(Event):
    """Evento emitido quando empresa e usuários são inativados por atraso de pagamento superior a 30 dias."""

    company: UUID
