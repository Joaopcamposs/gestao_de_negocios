"""Testes unitários para os handlers de CreditCard no shared_core.

Cobre create_credit_card, delete_credit_card e handlers de eventos.
"""

from unittest.mock import AsyncMock, MagicMock

import uuid7

from shared_core.domain.commands.credit_card import CreateCreditCard, DeleteCreditCard
from shared_core.domain.events.credit_card import CreditCardCreated, CreditCardDeleted
from shared_core.services.handlers.credit_card import (
    create_credit_card,
    credit_card_created,
    credit_card_deleted,
    delete_credit_card,
)
from tests.unit.conftest import FakeUnitOfWork


_USER_ID = uuid7.create()
_CARD_ID = uuid7.create()


class TestCreateCreditCard:
    """Testes para o handler create_credit_card."""

    async def test_create_credit_card(self) -> None:
        """Verifica que create_credit_card cria o cartão e retorna o ID."""
        mock_repo = AsyncMock()
        mock_card = MagicMock()
        mock_card.id = _CARD_ID
        mock_repo.create_aggregate = AsyncMock(return_value=mock_card)

        uow = FakeUnitOfWork(domain_repo=mock_repo)

        command = CreateCreditCard(
            user_id=_USER_ID,
            number="4111111111111111",
            expiry="12/30",
            cvv="123",
            cpf="12345678901",
            holder_name="Test User",
        )

        result = await create_credit_card(command, uow)

        assert result == _CARD_ID
        mock_repo.create_aggregate.assert_awaited_once()
        mock_card.create.assert_called_once()
        mock_repo.add.assert_awaited_once_with(mock_card)


class TestDeleteCreditCard:
    """Testes para o handler delete_credit_card."""

    async def test_delete_credit_card(self) -> None:
        """Verifica que delete_credit_card remove o cartão corretamente."""
        mock_repo = AsyncMock()
        mock_card = MagicMock()
        mock_repo.get_by_id = AsyncMock(return_value=mock_card)

        uow = FakeUnitOfWork(domain_repo=mock_repo)

        command = DeleteCreditCard(card_id=_CARD_ID)

        await delete_credit_card(command, uow)

        mock_repo.get_by_id.assert_awaited_once_with(card_id=_CARD_ID)
        mock_card.delete.assert_called_once()
        mock_repo.remove.assert_awaited_once_with(mock_card)


class TestCreditCardEventHandlers:
    """Testes para os handlers de eventos de CreditCard."""

    async def test_credit_card_created(self) -> None:
        """Verifica que credit_card_created é executado sem erros."""
        event = CreditCardCreated(id=_CARD_ID, user_id=_USER_ID)
        uow = FakeUnitOfWork()
        await credit_card_created(event, uow)

    async def test_credit_card_deleted(self) -> None:
        """Verifica que credit_card_deleted é executado sem erros."""
        event = CreditCardDeleted(id=_CARD_ID, user_id=_USER_ID)
        uow = FakeUnitOfWork()
        await credit_card_deleted(event, uow)
