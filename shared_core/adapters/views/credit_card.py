"""Módulo de views de consulta de CreditCard."""

from typing import cast
from uuid import UUID

from shared_core.adapters.repository.view_repo.credit_card import CreditCardViewRepo
from shared_core.entrypoints.schemas.credit_card import ReadCreditCardSchema
from shared_core.domains import Domain
from messagebus.unity_of_work import UnitOfWork


async def view_credit_cards(
    uow: UnitOfWork,
    user_id: UUID,
) -> list[ReadCreditCardSchema]:
    """
    Consulta os cartões de crédito de um usuário com dados descriptografados.

    Args:
        uow: Unit of Work para gerenciar a sessão.
        user_id: UUID do usuário cujos cartões serão listados.

    Returns:
        Lista de schemas de cartão de crédito com dados descriptografados.
    """
    async with uow(Domain.credit_card) as uow:
        view_repo: CreditCardViewRepo = cast(CreditCardViewRepo, uow.view_repo)
        cards = await view_repo.get_all_by_user(user_id=user_id)

    result = []
    for card in cards:
        decrypted = card.decrypt_fields()
        result.append(
            ReadCreditCardSchema(
                id=card.id,
                user_id=card.user_id,
                number=decrypted["number"],
                expiry=decrypted["expiry"],
                cvv=decrypted["cvv"],
                cpf=decrypted["cpf"],
                holder_name=decrypted["holder_name"],
                active=card.active,
                created_at=card.created_at,
                created_by=card.created_by,
                updated_at=card.updated_at,
                updated_by=card.updated_by,
                deleted_at=card.deleted_at,
                deleted_by=card.deleted_by,
            )
        )
    return result
