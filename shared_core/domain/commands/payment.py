"""Módulo de comandos do domínio Payment."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from messagebus.messagebus import Command


@dataclass
class CreatePayment(Command):
    """Comando para registrar um novo pagamento para uma empresa."""

    company: UUID
    amount: float
    due_date: datetime


@dataclass
class MarkPaymentAsPaid(Command):
    """Comando para registrar um pagamento como realizado."""

    payment_id: UUID


@dataclass
class MarkPaymentAsOverdue(Command):
    """Comando para marcar um pagamento como em atraso."""

    payment_id: UUID


@dataclass
class CheckAndDeactivateOverdueCompanies(Command):
    """Comando para verificar e inativar empresas com atraso de pagamento superior a 30 dias."""
