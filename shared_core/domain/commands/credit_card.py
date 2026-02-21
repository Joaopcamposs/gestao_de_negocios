"""Módulo de comandos do domínio CreditCard."""

from dataclasses import dataclass
from uuid import UUID

from messagebus.messagebus import Command


@dataclass
class CreateCreditCard(Command):
    """Comando para adicionar um cartão de crédito a um usuário."""

    user_id: UUID
    number: str
    expiry: str
    cvv: str
    cpf: str
    holder_name: str


@dataclass
class DeleteCreditCard(Command):
    """Comando para excluir um cartão de crédito."""

    card_id: UUID
