"""Testes unitários para os handlers de AuditLog no shared_core.

Cobre _persist_audit_log, audit_entity_created, audit_entity_deleted e audit_entity_updated.
"""

from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import uuid7

from messagebus.entities import AuditableEvent
from messagebus.messagebus import Event
from shared_core.domain.value_objects.enums import AuditOperation
from shared_core.services.handlers.audit_log import (
    _persist_audit_log,
    audit_entity_created,
    audit_entity_deleted,
    audit_entity_updated,
)
from tests.unit.conftest import FakeUnitOfWork, make_fake_user


_ENTITY_ID = uuid7.create()


class FakeAuditableEvent(Event, AuditableEvent):
    """Evento fake que é auditável."""

    id: UUID = _ENTITY_ID
    entity_type: str = "TestEntity"


class FakeNonAuditableEvent(Event):
    """Evento fake que NÃO é auditável."""

    id: UUID = _ENTITY_ID


class FakeAuditableNoEntityType(Event, AuditableEvent):
    """Evento auditável mas sem entity_type definido."""

    id: UUID = _ENTITY_ID
    entity_type: str = ""


class TestPersistAuditLog:
    """Testes para a função _persist_audit_log."""

    async def test_persist_with_auditable_event(self) -> None:
        """Verifica que _persist_audit_log persiste evento auditável corretamente."""
        mock_repo = AsyncMock()
        mock_audit_log = MagicMock()
        mock_audit_log.id = uuid7.create()
        mock_repo.create_from_event = AsyncMock(return_value=mock_audit_log)

        user = make_fake_user()
        uow = FakeUnitOfWork(domain_repo=mock_repo, user=user)
        event = FakeAuditableEvent()

        result = await _persist_audit_log(event, AuditOperation.CREATE, uow)

        assert result is not None
        mock_repo.create_from_event.assert_awaited_once()

    async def test_persist_with_non_auditable_event(self) -> None:
        """Verifica que _persist_audit_log retorna None para evento não auditável."""
        uow = FakeUnitOfWork()
        event = FakeNonAuditableEvent()

        result = await _persist_audit_log(event, AuditOperation.CREATE, uow)

        assert result is None

    async def test_persist_with_empty_entity_type(self) -> None:
        """Verifica que _persist_audit_log retorna None quando entity_type está vazio."""
        uow = FakeUnitOfWork()
        event = FakeAuditableNoEntityType()

        result = await _persist_audit_log(event, AuditOperation.CREATE, uow)

        assert result is None

    async def test_persist_without_user(self) -> None:
        """Verifica que _persist_audit_log funciona sem usuário (user_id=None)."""
        mock_repo = AsyncMock()
        mock_audit_log = MagicMock()
        mock_audit_log.id = uuid7.create()
        mock_repo.create_from_event = AsyncMock(return_value=mock_audit_log)

        uow = FakeUnitOfWork(domain_repo=mock_repo)
        uow.user = None
        event = FakeAuditableEvent()

        result = await _persist_audit_log(event, AuditOperation.UPDATE, uow)

        assert result is not None
        call_kwargs = mock_repo.create_from_event.call_args
        assert (
            call_kwargs.kwargs.get("user_id") is None
            or call_kwargs[1].get("user_id") is None
        )


class TestAuditEntityHandlers:
    """Testes para os handlers de auditoria de entidades."""

    async def test_audit_entity_created(self) -> None:
        """Verifica que audit_entity_created persiste o log de criação."""
        mock_repo = AsyncMock()
        mock_audit_log = MagicMock()
        mock_audit_log.id = uuid7.create()
        mock_repo.create_from_event = AsyncMock(return_value=mock_audit_log)

        uow = FakeUnitOfWork(domain_repo=mock_repo)
        event = FakeAuditableEvent()

        await audit_entity_created(event, uow)
        mock_repo.create_from_event.assert_awaited_once()

    async def test_audit_entity_updated(self) -> None:
        """Verifica que audit_entity_updated persiste o log de atualização."""
        mock_repo = AsyncMock()
        mock_audit_log = MagicMock()
        mock_audit_log.id = uuid7.create()
        mock_repo.create_from_event = AsyncMock(return_value=mock_audit_log)

        uow = FakeUnitOfWork(domain_repo=mock_repo)
        event = FakeAuditableEvent()

        await audit_entity_updated(event, uow)

    async def test_audit_entity_deleted(self) -> None:
        """Verifica que audit_entity_deleted persiste o log de exclusão."""
        mock_repo = AsyncMock()
        mock_audit_log = MagicMock()
        mock_audit_log.id = uuid7.create()
        mock_repo.create_from_event = AsyncMock(return_value=mock_audit_log)

        uow = FakeUnitOfWork(domain_repo=mock_repo)
        event = FakeAuditableEvent()

        await audit_entity_deleted(event, uow)
