"""Módulo de handlers de comandos e eventos do domínio CreditCard."""

from typing import cast
from uuid import UUID

from shared_core.adapters.repository.domain_repo.credit_card import CreditCardDomainRepo
from shared_core.domain.commands.credit_card import CreateCreditCard, DeleteCreditCard
from shared_core.domain.events.credit_card import CreditCardCreated, CreditCardDeleted
from shared_core.domains import Domain
from messagebus.messagebus import logger
from messagebus.unity_of_work import UnitOfWork


async def create_credit_card(command: CreateCreditCard, uow: UnitOfWork) -> UUID:
    """Handler para criação de cartão de crédito."""
    async with uow(Domain.credit_card) as uow:
        domain_repo: CreditCardDomainRepo = cast(CreditCardDomainRepo, uow.domain_repo)

        card = await domain_repo.create_aggregate(
            user_id=command.user_id,
            number=command.number,
            expiry=command.expiry,
            cvv=command.cvv,
            cpf=command.cpf,
            holder_name=command.holder_name,
        )
        card.create(user_id=uow.user_id)

        await domain_repo.add(card)
        await uow.commit()

        return card.id


async def delete_credit_card(command: DeleteCreditCard, uow: UnitOfWork) -> None:
    """Handler para exclusão (soft delete) de cartão de crédito."""
    async with uow(Domain.credit_card) as uow:
        domain_repo: CreditCardDomainRepo = cast(CreditCardDomainRepo, uow.domain_repo)

        card = await domain_repo.get_by_id(card_id=command.card_id)
        card.delete(user_id=uow.user_id)

        await domain_repo.remove(card)
        await uow.commit()


async def credit_card_created(event: CreditCardCreated, uow: UnitOfWork) -> None:
    """Handler para o evento de cartão de crédito criado."""
    logger.info(f"Event CreditCardCreated for card: {event.id} user: {event.user_id}")


async def credit_card_deleted(event: CreditCardDeleted, uow: UnitOfWork) -> None:
    """Handler para o evento de cartão de crédito excluído."""
    logger.info(f"Event CreditCardDeleted for card: {event.id} user: {event.user_id}")
