"""Testes unitários para messagebus/unity_of_work.py.

Cobre AbstractUnitOfWork, UnitOfWork, coleta de eventos e tratamento de erros.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
import uuid7

from messagebus.entities import UserBase
from messagebus.unity_of_work import (
    UnitOfWork,
    UnitOfWorkContextAlreadyOpen,
    UnitOfWorkWithProblem,
)


_COMPANY_ID = uuid7.create()
_USER_ID = uuid7.create()


def _make_user(company=None, user_id=None) -> UserBase:
    """Cria um UserBase fake para testes de UnitOfWork."""
    return UserBase(
        company=company or _COMPANY_ID,
        id=user_id or _USER_ID,
    )


class TestAbstractUnitOfWork:
    """Testes para o comportamento base do UnitOfWork."""

    def test_init_basic(self) -> None:
        """Verifica inicialização básica com user e session_factory."""
        user = _make_user()
        mock_factory = MagicMock()
        uow = UnitOfWork(session_factory=mock_factory, user=user)
        assert uow.user == user
        assert uow.schema == str(_COMPANY_ID)
        assert uow.create_schema is False

    def test_init_without_user(self) -> None:
        """Verifica inicialização sem usuário define schema como None."""
        mock_factory = MagicMock()
        uow = UnitOfWork(session_factory=mock_factory)
        assert uow.user is None
        assert uow.schema is None

    def test_init_with_explicit_schema(self) -> None:
        """Verifica que schema explícito é aceito quando pertence ao usuário."""
        user = _make_user()
        mock_factory = MagicMock()
        uow = UnitOfWork(session_factory=mock_factory, user=user, schema=str(_COMPANY_ID))
        assert uow.schema == str(_COMPANY_ID)

    def test_init_user_schema_mismatch_raises(self) -> None:
        """Verifica que schema de outra empresa levanta UnitOfWorkWithProblem."""
        user = _make_user()
        other_company = uuid7.create()
        mock_factory = MagicMock()

        with pytest.raises(UnitOfWorkWithProblem, match="does not belong"):
            UnitOfWork(
                session_factory=mock_factory,
                user=user,
                schema=str(other_company),
            )

    def test_init_user_schema_mismatch_allowed_with_create(self) -> None:
        """Verifica que create_schema=True permite schema de outra empresa."""
        user = _make_user()
        other_company = uuid7.create()
        mock_factory = MagicMock()

        uow = UnitOfWork(
            session_factory=mock_factory,
            user=user,
            schema=str(other_company),
            create_schema=True,
        )
        assert uow.create_schema is True

    def test_call_sets_repos(self) -> None:
        """Verifica que chamar uow(domain) configura domain_repo e view_repo."""
        mock_factory = MagicMock()
        uow = UnitOfWork(session_factory=mock_factory)

        mock_domain_class = MagicMock()
        mock_view_class = MagicMock()
        domain = MagicMock()
        domain.value = (mock_domain_class, mock_view_class)

        result = uow(domain)
        assert result is uow
        assert uow.domain_repo == mock_domain_class
        assert uow.view_repo == mock_view_class

    def test_call_without_domain(self) -> None:
        """Verifica que chamar uow() sem domínio retorna o próprio uow."""
        mock_factory = MagicMock()
        uow = UnitOfWork(session_factory=mock_factory)
        result = uow()
        assert result is uow

    async def test_aenter_sets_committed_false(self) -> None:
        """Verifica que __aenter__ inicializa committed como False."""
        mock_factory = AsyncMock()
        mock_session = AsyncMock()
        mock_factory.return_value = mock_session

        user = _make_user()
        uow = UnitOfWork(session_factory=mock_factory, user=user)
        uow.domain_repo = None
        uow.view_repo = None

        entered = await uow.__aenter__()
        assert entered.committed is False

    async def test_aenter_double_open_raises(self) -> None:
        """Verifica que abrir o contexto duas vezes levanta UnitOfWorkContextAlreadyOpen."""
        mock_factory = AsyncMock()
        mock_session = AsyncMock()
        mock_factory.return_value = mock_session

        user = _make_user()
        uow = UnitOfWork(session_factory=mock_factory, user=user)
        uow.domain_repo = None
        uow.view_repo = None

        await uow.__aenter__()

        with pytest.raises(UnitOfWorkContextAlreadyOpen):
            await uow.__aenter__()

    def test_user_id_with_user(self) -> None:
        """Verifica que user_id retorna o ID do usuário quando presente."""
        mock_factory = MagicMock()
        user = _make_user()
        uow = UnitOfWork(session_factory=mock_factory, user=user)
        assert uow.user_id == _USER_ID

    def test_user_id_without_user(self) -> None:
        """Verifica que user_id retorna None quando não há usuário."""
        mock_factory = MagicMock()
        uow = UnitOfWork(session_factory=mock_factory)
        assert uow.user_id is None

    async def test_commit(self) -> None:
        """Verifica que commit() marca o UoW como committed."""
        mock_factory = AsyncMock()
        mock_session = AsyncMock()
        mock_factory.return_value = mock_session

        user = _make_user()
        uow = UnitOfWork(session_factory=mock_factory, user=user)
        uow.domain_repo = None
        uow.view_repo = None

        await uow.__aenter__()
        await uow.commit()
        assert uow.committed is True

    async def test_rollback(self) -> None:
        """Verifica que rollback() chama rollback na sessão."""
        mock_factory = AsyncMock()
        mock_session = AsyncMock()
        mock_factory.return_value = mock_session

        user = _make_user()
        uow = UnitOfWork(session_factory=mock_factory, user=user)
        uow.domain_repo = None
        uow.view_repo = None

        await uow.__aenter__()
        await uow.rollback()
        mock_session.rollback.assert_awaited_once()


class TestCollectNewEvents:
    """Testes para a coleta de novos eventos do UnitOfWork."""

    def test_collect_events_from_aggregates(self) -> None:
        """Verifica que eventos dos agregados vistos são coletados e removidos."""
        mock_factory = MagicMock()
        uow = UnitOfWork(session_factory=mock_factory)

        mock_event = MagicMock()
        agg = MagicMock()
        agg.events = [mock_event]

        mock_repo = MagicMock()
        mock_repo.seen = {agg}
        uow.domain_repo = mock_repo

        events = list(uow.collect_new_events())
        assert mock_event in events
        assert agg.events == []

    def test_collect_no_events_without_repo(self) -> None:
        """Verifica que collect_new_events retorna vazio sem domain_repo."""
        mock_factory = MagicMock()
        uow = UnitOfWork(session_factory=mock_factory)
        if hasattr(uow, "domain_repo"):
            delattr(uow, "domain_repo")
        events = list(uow.collect_new_events())
        assert events == []

    def test_collect_no_events_with_empty_seen(self) -> None:
        """Verifica que collect_new_events retorna vazio quando seen está vazio."""
        mock_factory = MagicMock()
        uow = UnitOfWork(session_factory=mock_factory)

        mock_repo = MagicMock()
        mock_repo.seen = set()
        uow.domain_repo = mock_repo

        events = list(uow.collect_new_events())
        assert events == []


class TestConcreteUnitOfWork:
    """Testes para o UnitOfWork concreto."""

    def test_init_read_only(self) -> None:
        """Verifica que read_only=True é armazenado corretamente."""
        mock_factory = MagicMock()
        uow = UnitOfWork(session_factory=mock_factory, read_only=True)
        assert uow.read_only is True

    def test_init_create_schema_imports(self) -> None:
        """Verifica que create_schema=True disponibiliza create_full_schema_within_transaction."""
        mock_factory = MagicMock()
        user = _make_user()
        uow = UnitOfWork(
            session_factory=mock_factory,
            user=user,
            schema=str(_COMPANY_ID),
            create_schema=True,
        )
        assert uow.create_full_schema_within_transaction is not None

    async def test_aenter_with_repos(self) -> None:
        """Verifica que __aenter__ instancia domain_repo e view_repo corretamente."""
        mock_factory = AsyncMock()
        mock_write_session = AsyncMock()
        mock_read_session = AsyncMock()
        mock_factory.side_effect = [mock_write_session, mock_read_session]

        user = _make_user()
        uow = UnitOfWork(session_factory=mock_factory, user=user)

        mock_domain_class = MagicMock(return_value="domain_instance")
        mock_view_class = MagicMock(return_value="view_instance")
        uow.domain_repo = mock_domain_class
        uow.view_repo = mock_view_class

        entered = await uow.__aenter__()
        assert entered.domain_repo == "domain_instance"
        assert entered.view_repo == "view_instance"

    async def test_aenter_with_create_schema(self) -> None:
        """Verifica que __aenter__ com create_schema=True cria o schema antes."""
        mock_factory = AsyncMock()
        mock_read_session = AsyncMock()
        mock_factory.return_value = mock_read_session

        mock_schema_session = AsyncMock()
        mock_schema_creator = AsyncMock(return_value=mock_schema_session)

        user = _make_user()
        uow = UnitOfWork(
            session_factory=mock_factory,
            user=user,
            schema=str(_COMPANY_ID),
            create_schema=True,
        )
        uow.create_full_schema_within_transaction = mock_schema_creator
        uow.domain_repo = None
        uow.view_repo = None

        await uow.__aenter__()
        mock_schema_creator.assert_awaited_once()
        assert uow.session == mock_schema_session
        assert uow.create_schema is False

    async def test_aenter_read_only_skips_domain_repo(self) -> None:
        """Verifica que read_only=True não instancia domain_repo."""
        mock_factory = AsyncMock()
        mock_session = AsyncMock()
        mock_factory.return_value = mock_session

        user = _make_user()
        uow = UnitOfWork(session_factory=mock_factory, user=user, read_only=True)

        mock_domain_class = MagicMock()
        mock_view_class = MagicMock(return_value="view_instance")
        uow.domain_repo = mock_domain_class
        uow.view_repo = mock_view_class

        await uow.__aenter__()
        mock_domain_class.assert_not_called()

    async def test_aexit_closes_sessions(self) -> None:
        """Verifica que __aexit__ fecha as sessões após commit."""
        mock_factory = AsyncMock()
        mock_write_session = AsyncMock()
        mock_write_session.bind = AsyncMock()
        mock_read_session = AsyncMock()
        mock_read_session.bind = AsyncMock()
        mock_factory.side_effect = [mock_write_session, mock_read_session]

        user = _make_user()
        uow = UnitOfWork(session_factory=mock_factory, user=user)
        uow.domain_repo = None
        uow.view_repo = None

        await uow.__aenter__()
        await uow.commit()
        await uow.__aexit__()

        mock_read_session.close.assert_awaited_once()
        mock_write_session.close.assert_awaited_once()

    async def test_aexit_rollback_when_not_committed(self) -> None:
        """Verifica que __aexit__ faz rollback quando não houve commit."""
        mock_factory = AsyncMock()
        mock_write_session = AsyncMock()
        mock_write_session.bind = AsyncMock()
        mock_read_session = AsyncMock()
        mock_read_session.bind = AsyncMock()
        mock_factory.side_effect = [mock_write_session, mock_read_session]

        user = _make_user()
        uow = UnitOfWork(session_factory=mock_factory, user=user)
        uow.domain_repo = None
        uow.view_repo = None

        await uow.__aenter__()
        await uow.__aexit__()

        mock_write_session.rollback.assert_awaited_once()
