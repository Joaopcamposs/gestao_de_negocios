"""Módulo do repositório de domínio de CreditCard."""

from abc import abstractmethod
from typing import Any
from uuid import UUID

from sqlalchemy import select

from shared_core.adapters.repository.mixins.upsert import UpsertMixin
from shared_core.domain.aggregate.credit_card import CreditCard
from shared_core.domain.excecoes import CreditCardNotFound
from messagebus.entities import DomainRepository


class AbstractCreditCardDomainRepo(DomainRepository):
    """Repositório abstrato de domínio para CreditCard."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.seen: set[CreditCard] = set()

    async def add(self, card: CreditCard) -> None:
        """
        Adiciona um cartão ao repositório e à lista de rastreados.

        Args:
            card: Agregado CreditCard a ser adicionado.
        """
        self.seen.add(card)
        await self._add(card)

    @abstractmethod
    async def _add(self, card: CreditCard) -> None:
        """Implementação interna de adição."""
        raise NotImplementedError

    async def remove(self, card: CreditCard) -> None:
        """
        Remove um cartão do repositório (soft delete).

        Args:
            card: Agregado CreditCard a ser removido.
        """
        self.seen.add(card)
        await self._remove(card)

    @abstractmethod
    async def _remove(self, card: CreditCard) -> None:
        """Implementação interna de remoção."""
        raise NotImplementedError


class CreditCardDomainRepo(AbstractCreditCardDomainRepo, UpsertMixin):
    """Implementação concreta do repositório de domínio de CreditCard."""

    async def create_aggregate(
        self,
        user_id: UUID,
        number: str,
        expiry: str,
        cvv: str,
        cpf: str,
        holder_name: str,
    ) -> CreditCard:
        """
        Cria um novo agregado CreditCard com campos criptografados.

        Args:
            user_id: ID do usuário proprietário do cartão.
            number: Número do cartão.
            expiry: Data de vencimento.
            cvv: Código de segurança.
            cpf: CPF do titular.
            holder_name: Nome do titular.

        Returns:
            Nova instância do agregado CreditCard.
        """
        return CreditCard.create_aggregate(
            user_id=user_id,
            number=number,
            expiry=expiry,
            cvv=cvv,
            cpf=cpf,
            holder_name=holder_name,
        )

    async def get_by_id(self, card_id: UUID) -> CreditCard:
        """
        Busca um cartão pelo ID.

        Args:
            card_id: UUID do cartão.

        Returns:
            Agregado CreditCard encontrado.

        Raises:
            CreditCardNotFound: Se o cartão não for encontrado.
        """
        async with self.session as session:
            card = (
                await session.execute(
                    select(CreditCard).where(
                        CreditCard.id == card_id,
                        CreditCard.deleted_at.is_(None),
                    )
                )
            ).scalar_one_or_none()
            if not card:
                raise CreditCardNotFound

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
        Busca todos os cartões de um usuário.

        Args:
            user_id: UUID do usuário.

        Returns:
            Lista de agregados CreditCard do usuário.
        """
        async with self.session as session:
            cards = (
                (
                    await session.execute(
                        select(CreditCard).where(
                            CreditCard.user_id == user_id,
                            CreditCard.deleted_at.is_(None),
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

    async def _add(self, card: CreditCard) -> None:
        """Persiste um cartão no banco de dados (inserção)."""
        data = {
            "id": card.id,
            "user_id": card.user_id,
            "card_key_encrypted": card.card_key_encrypted,
            "number_encrypted": card.number_encrypted,
            "expiry_encrypted": card.expiry_encrypted,
            "cvv_encrypted": card.cvv_encrypted,
            "cpf_encrypted": card.cpf_encrypted,
            "holder_name_encrypted": card.holder_name_encrypted,
            "created_at": card.created_at,
            "created_by": card.created_by,
            "updated_at": card.updated_at,
            "updated_by": card.updated_by,
            "deleted_at": card.deleted_at,
            "deleted_by": card.deleted_by,
        }
        await self._execute_upsert(CreditCard, card, data)

    async def _remove(self, card: CreditCard) -> None:
        """Marca um cartão como deletado no banco de dados (soft delete)."""
        await self._execute_soft_delete(CreditCard, card)
