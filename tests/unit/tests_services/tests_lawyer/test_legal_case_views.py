"""Testes unitários para as views de LegalCase (lawyer)."""

from unittest.mock import AsyncMock, MagicMock

import uuid7

from services.lawyer.adapters.views.legal_case import view_legal_case
from tests.unit.conftest import FakeUnitOfWork


_COMPANY_ID = uuid7.create()


class TestViewLegalCase:
    async def test_view_legal_case_by_number_found(self) -> None:
        mock_case = MagicMock()
        mock_view = AsyncMock()
        mock_view.get_by_case_number = AsyncMock(return_value=mock_case)

        uow = FakeUnitOfWork(view_repo=mock_view)

        result = await view_legal_case(uow, company=_COMPANY_ID, case_number="0001234")
        assert result == [mock_case]

    async def test_view_legal_case_by_number_not_found(self) -> None:
        mock_view = AsyncMock()
        mock_view.get_by_case_number = AsyncMock(return_value=None)

        uow = FakeUnitOfWork(view_repo=mock_view)

        result = await view_legal_case(uow, company=_COMPANY_ID, case_number="9999999")
        assert result == []

    async def test_view_legal_case_all(self) -> None:
        cases = [MagicMock()]
        mock_view = AsyncMock()
        mock_view.get_all = AsyncMock(return_value=cases)

        uow = FakeUnitOfWork(view_repo=mock_view)

        result = await view_legal_case(uow, company=_COMPANY_ID)
        assert result == cases

    async def test_view_legal_case_include_deleted(self) -> None:
        mock_view = AsyncMock()
        mock_view.get_all = AsyncMock(return_value=[])

        uow = FakeUnitOfWork(view_repo=mock_view)

        await view_legal_case(uow, company=_COMPANY_ID, include_deleted=True)
        mock_view.get_all.assert_awaited_once_with(
            company=_COMPANY_ID, include_deleted=True
        )
