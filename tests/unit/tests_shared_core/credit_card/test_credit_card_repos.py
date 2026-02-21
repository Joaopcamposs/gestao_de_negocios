"""Testes unitários para os repositórios concretos de CreditCard (domain + view)."""

from unittest.mock import AsyncMock, MagicMock

import pytest
import uuid7

from shared_core.domain.aggregate.credit_card import CreditCard
from shared_core.domain.excecoes import CreditCardNotFound


_COMPANY_ID = uuid7.create()
_USER_ID = uuid7.create()
_CARD_ID = uuid7.create()


def _make_session():
    """Cria uma sessão SQLAlchemy mockada com async context manager."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    return session


def _make_mock_card_row():
    """Cria uma linha de resultado mockada representando um CreditCard."""
    c = MagicMock()
    c.id = _CARD_ID
    c.user_id = _USER_ID
    c.card_key_encrypted = b"key"
    c.number_encrypted = b"num"
    c.expiry_encrypted = b"exp"
    c.cvv_encrypted = b"cvv"
    c.cpf_encrypted = b"cpf"
    c.holder_name_encrypted = b"hn"
    c.active = True
    c.created_at = None
    c.created_by = None
    c.updated_at = None
    c.updated_by = None
    c.deleted_at = None
    c.deleted_by = None
    return c


# ─── CreditCardDomainRepo ───


class TestCreditCardDomainRepoConcrete:
    """Testes para o repositório de domínio concreto de CreditCard."""

    async def test_create_aggregate(self) -> None:
        """Verifica que create_aggregate cria um cartão com sucesso."""
        from shared_core.adapters.repository.domain_repo.credit_card import (
            CreditCardDomainRepo,
        )

        session = _make_session()
        repo = CreditCardDomainRepo(session=session)

        card = await repo.create_aggregate(
            user_id=_USER_ID,
            number="4111111111111111",
            expiry="12/30",
            cvv="123",
            cpf="12345678901",
            holder_name="Test",
        )
        assert card.user_id == _USER_ID

    async def test_get_by_id_found(self) -> None:
        """Verifica que get_by_id retorna o cartão quando encontrado."""
        from shared_core.adapters.repository.domain_repo.credit_card import (
            CreditCardDomainRepo,
        )

        session = _make_session()
        mock_c = _make_mock_card_row()
        r = MagicMock()
        r.scalar_one_or_none.return_value = mock_c
        session.execute.return_value = r

        repo = CreditCardDomainRepo(session=session)
        card = await repo.get_by_id(_CARD_ID)
        assert card.id == _CARD_ID

    async def test_get_by_id_not_found(self) -> None:
        """Verifica que get_by_id levanta CreditCardNotFound quando não encontrado."""
        from shared_core.adapters.repository.domain_repo.credit_card import (
            CreditCardDomainRepo,
        )

        session = _make_session()
        r = MagicMock()
        r.scalar_one_or_none.return_value = None
        session.execute.return_value = r

        repo = CreditCardDomainRepo(session=session)
        with pytest.raises(CreditCardNotFound):
            await repo.get_by_id(_CARD_ID)

    async def test_get_all_by_user(self) -> None:
        """Verifica que get_all_by_user retorna cartões do usuário."""
        from shared_core.adapters.repository.domain_repo.credit_card import (
            CreditCardDomainRepo,
        )

        session = _make_session()
        mock_c = _make_mock_card_row()
        sr = MagicMock()
        sr.all.return_value = [mock_c]
        r = MagicMock()
        r.scalars.return_value = sr
        session.execute.return_value = r

        repo = CreditCardDomainRepo(session=session)
        result = await repo.get_all_by_user(_USER_ID)
        assert len(result) == 1

    async def test_add_and_remove(self) -> None:
        """Verifica que _add e _remove executam operações na sessão."""
        from shared_core.adapters.repository.domain_repo.credit_card import (
            CreditCardDomainRepo,
        )

        session = _make_session()
        repo = CreditCardDomainRepo(session=session)

        card = CreditCard.create_aggregate(
            user_id=_USER_ID,
            number="4111111111111111",
            expiry="12/30",
            cvv="123",
            cpf="12345678901",
            holder_name="Test",
        )
        card.create(_USER_ID)
        await repo._add(card)
        session.execute.assert_awaited()

        session.reset_mock()
        card.delete(_USER_ID)
        await repo._remove(card)
        session.execute.assert_awaited()


# ─── CreditCardViewRepo ───


class TestCreditCardViewRepo:
    """Testes para o repositório de view concreto de CreditCard."""

    async def test_get_all_by_user(self) -> None:
        """Verifica que get_all_by_user retorna cartões do usuário."""
        from shared_core.adapters.repository.view_repo.credit_card import (
            CreditCardViewRepo,
        )

        session = _make_session()
        mock_c = _make_mock_card_row()
        sr = MagicMock()
        sr.all.return_value = [mock_c]
        r = MagicMock()
        r.scalars.return_value = sr
        session.execute.return_value = r

        repo = CreditCardViewRepo(session=session)
        result = await repo.get_all_by_user(_USER_ID)
        assert len(result) == 1

    async def test_get_by_id_found(self) -> None:
        """Verifica que get_by_id retorna o cartão quando encontrado."""
        from shared_core.adapters.repository.view_repo.credit_card import (
            CreditCardViewRepo,
        )

        session = _make_session()
        mock_c = _make_mock_card_row()
        r = MagicMock()
        r.scalar_one_or_none.return_value = mock_c
        session.execute.return_value = r

        repo = CreditCardViewRepo(session=session)
        result = await repo.get_by_id(_CARD_ID)
        assert result is not None

    async def test_get_by_id_not_found(self) -> None:
        """Verifica que get_by_id retorna None quando não encontrado."""
        from shared_core.adapters.repository.view_repo.credit_card import (
            CreditCardViewRepo,
        )

        session = _make_session()
        r = MagicMock()
        r.scalar_one_or_none.return_value = None
        session.execute.return_value = r

        repo = CreditCardViewRepo(session=session)
        result = await repo.get_by_id(_CARD_ID)
        assert result is None
