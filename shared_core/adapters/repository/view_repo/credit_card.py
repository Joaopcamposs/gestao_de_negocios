"""Módulo do repositório de consulta de CreditCard."""

from uuid import UUID

from sqlalchemy import select

from shared_core.domain.aggregate.credit_card import CreditCard as CreditCardAggregate
from shared_core.domain.entities.credit_card import CreditCard
from messagebus.entities import ViewRepository


class CreditCardViewRepo(ViewRepository):
    """Repositório de consulta para CreditCard."""

    async def get_by_id(self, card_id: UUID) -> CreditCard | None:
        """
        Busca um cartão pelo ID (somente leitura).

        Args:
            card_id: UUID do cartão.

        Returns:
            Entidade CreditCard ou None se não encontrado.
        """
        async with self.session as session:
            card = (
                await session.execute(
                    select(CreditCardAggregate).where(
                        CreditCardAggregate.id == card_id,
                        CreditCardAggregate.deleted_at.is_(None),
                    )
                )
            ).scalar_one_or_none()
            if not card:
                return None

            return CreditCard(
                id=card.id,
                user_id=card.user_id,
                card_key_encrypted=card.card_key_encrypted,
                number_encrypted=card.number_encrypted,
                expiry_encrypted=card.expiry_encrypted,
                cvv_encrypted=card.cvv_encrypted,
                cpf_encrypted=card.cpf_encrypted,
                holder_name_encrypted=card.holder_name_encrypted,
                created_at=card.created_at,
                created_by=card.created_by,
                updated_at=card.updated_at,
                updated_by=card.updated_by,
                deleted_at=card.deleted_at,
                deleted_by=card.deleted_by,
            )

    async def get_all_by_user(self, user_id: UUID) -> list[CreditCard]:
        """
        Busca todos os cartões de um usuário (somente leitura).

        Args:
            user_id: UUID do usuário.

        Returns:
            Lista de entidades CreditCard do usuário.
        """
        async with self.session as session:
            cards = (
                (
                    await session.execute(
                        select(CreditCardAggregate).where(
                            CreditCardAggregate.user_id == user_id,
                            CreditCardAggregate.deleted_at.is_(None),
                        )
                    )
                )
                .scalars()
                .all()
            )
            return [
                CreditCard(
                    id=c.id,
                    user_id=c.user_id,
                    card_key_encrypted=c.card_key_encrypted,
                    number_encrypted=c.number_encrypted,
                    expiry_encrypted=c.expiry_encrypted,
                    cvv_encrypted=c.cvv_encrypted,
                    cpf_encrypted=c.cpf_encrypted,
                    holder_name_encrypted=c.holder_name_encrypted,
                    created_at=c.created_at,
                    created_by=c.created_by,
                    updated_at=c.updated_at,
                    updated_by=c.updated_by,
                    deleted_at=c.deleted_at,
                    deleted_by=c.deleted_by,
                )
                for c in cards
            ]
