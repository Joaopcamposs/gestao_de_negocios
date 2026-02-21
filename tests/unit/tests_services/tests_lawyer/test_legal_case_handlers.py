"""Testes unitários para os handlers do LegalCase no contexto advogado."""

from unittest.mock import AsyncMock, MagicMock
from datetime import date

import uuid7

from services.lawyer.domain.commands.legal_case import (
    CreateLegalCase,
    DeleteLegalCase,
    UpdateLegalCase,
)
from services.lawyer.domain.events.legal_case import (
    LegalCaseCreated,
    LegalCaseDeleted,
    LegalCaseUpdated,
)
from services.lawyer.services.handlers.legal_case import (
    create_legal_case,
    delete_legal_case,
    legal_case_created,
    legal_case_deleted,
    legal_case_updated,
    update_legal_case,
)
from tests.unit.conftest import FakeUnitOfWork


_COMPANY_ID = uuid7.create()
_CASE_ID = uuid7.create()


class TestCreateLegalCase:
    async def test_create_legal_case(self) -> None:
        mock_repo = AsyncMock()
        mock_case = MagicMock()
        mock_case.id = _CASE_ID
        mock_repo.create_aggregate = AsyncMock(return_value=mock_case)

        uow = FakeUnitOfWork(domain_repo=mock_repo)

        command = CreateLegalCase(
            company=_COMPANY_ID,
            case_number="0001234-56.2026.8.26.0100",
            client_name="Cliente A",
            description="Processo cível",
            status="Em andamento",
            open_date=date(2026, 1, 15),
            notes="Urgente",
        )

        result = await create_legal_case(command, uow)

        assert result == _CASE_ID
        mock_repo.create_aggregate.assert_awaited_once()
        mock_case.create.assert_called_once()
        mock_repo.add.assert_awaited_once()


class TestUpdateLegalCase:
    async def test_update_legal_case(self) -> None:
        mock_repo = AsyncMock()
        mock_case = MagicMock()
        mock_repo.get_by_case_number = AsyncMock(return_value=mock_case)

        uow = FakeUnitOfWork(domain_repo=mock_repo)

        command = UpdateLegalCase(
            company=_COMPANY_ID,
            case_number="0001234-56.2026.8.26.0100",
            new_client_name="Cliente B",
            new_status="Finalizado",
        )

        await update_legal_case(command, uow)

        mock_repo.get_by_case_number.assert_awaited_once()
        mock_case.update.assert_called_once()
        mock_repo.add.assert_awaited_once()


class TestDeleteLegalCase:
    async def test_delete_legal_case(self) -> None:
        mock_repo = AsyncMock()
        mock_case = MagicMock()
        mock_repo.get_by_case_number = AsyncMock(return_value=mock_case)

        uow = FakeUnitOfWork(domain_repo=mock_repo)

        command = DeleteLegalCase(
            company=_COMPANY_ID,
            case_number="0001234-56.2026.8.26.0100",
        )

        await delete_legal_case(command, uow)

        mock_case.delete.assert_called_once()
        mock_repo.remove.assert_awaited_once()


class TestLegalCaseEventHandlers:
    async def test_legal_case_created(self) -> None:
        event = LegalCaseCreated(id=_CASE_ID, company=_COMPANY_ID)
        uow = FakeUnitOfWork()
        await legal_case_created(event, uow)

    async def test_legal_case_updated(self) -> None:
        event = LegalCaseUpdated(id=_CASE_ID, company=_COMPANY_ID)
        uow = FakeUnitOfWork()
        await legal_case_updated(event, uow)

    async def test_legal_case_deleted(self) -> None:
        event = LegalCaseDeleted(id=_CASE_ID, company=_COMPANY_ID)
        uow = FakeUnitOfWork()
        await legal_case_deleted(event, uow)
