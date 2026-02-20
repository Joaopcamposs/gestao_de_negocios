"""Módulo de endpoints da API para CreditCard."""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from shared_core.adapters.views.credit_card import view_credit_cards
from shared_core.domain.commands.credit_card import CreateCreditCard, DeleteCreditCard
from shared_core.entrypoints.schemas.credit_card import (
    CreateCreditCardSchema,
    ReadCreditCardSchema,
)
from shared_core.services.handlers.security import current_user, get_current_user
from shared_core.bootstrap import bootstrap
from shared_core.consts import SERVICE_TYPE
from messagebus.unity_of_work import UnitOfWork

router = APIRouter(
    prefix="/v1", tags=["CreditCards"], dependencies=[Depends(get_current_user)]
)


@router.post("/credit-card", response_model=UUID, status_code=status.HTTP_201_CREATED)
async def post_credit_card(body: CreateCreditCardSchema) -> UUID:
    """Adiciona um cartão de crédito ao usuário autenticado."""
    bus = bootstrap(user=current_user.get(), service_type=SERVICE_TYPE)

    command = CreateCreditCard(
        user_id=current_user.get().id,
        number=body.number,
        expiry=body.expiry,
        cvv=body.cvv,
        cpf=body.cpf,
        holder_name=body.holder_name,
    )
    card_id: UUID = await bus.handle(command)
    return card_id


@router.get("/credit-card", response_model=list[ReadCreditCardSchema])
async def get_credit_cards() -> list[ReadCreditCardSchema]:
    """Lista os cartões de crédito do usuário autenticado."""
    uow = UnitOfWork(user=current_user.get(), service_type=SERVICE_TYPE)
    return await view_credit_cards(uow, user_id=current_user.get().id)


@router.delete("/credit-card/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_credit_card(card_id: UUID) -> None:
    """Exclui um cartão de crédito pelo ID."""
    bus = bootstrap(user=current_user.get(), service_type=SERVICE_TYPE)

    command = DeleteCreditCard(card_id=card_id)
    await bus.handle(command)
