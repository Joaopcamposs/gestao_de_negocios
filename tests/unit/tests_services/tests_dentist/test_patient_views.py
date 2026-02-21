"""Testes unitários para as views de Patient (dentist)."""

from unittest.mock import AsyncMock, MagicMock

import uuid7

from services.dentist.adapters.views.patient import view_patient
from tests.unit.conftest import FakeUnitOfWork


_COMPANY_ID = uuid7.create()


class TestViewPatient:
    async def test_view_patient_by_cpf_found(self) -> None:
        mock_patient = MagicMock()
        mock_view = AsyncMock()
        mock_view.get_by_cpf = AsyncMock(return_value=mock_patient)

        uow = FakeUnitOfWork(view_repo=mock_view)

        result = await view_patient(uow, company=_COMPANY_ID, cpf="12345678901")
        assert result == [mock_patient]

    async def test_view_patient_by_cpf_not_found(self) -> None:
        mock_view = AsyncMock()
        mock_view.get_by_cpf = AsyncMock(return_value=None)

        uow = FakeUnitOfWork(view_repo=mock_view)

        result = await view_patient(uow, company=_COMPANY_ID, cpf="00000000000")
        assert result == []

    async def test_view_patient_all(self) -> None:
        patients = [MagicMock(), MagicMock()]
        mock_view = AsyncMock()
        mock_view.get_all = AsyncMock(return_value=patients)

        uow = FakeUnitOfWork(view_repo=mock_view)

        result = await view_patient(uow, company=_COMPANY_ID)
        assert result == patients

    async def test_view_patient_include_deleted(self) -> None:
        mock_view = AsyncMock()
        mock_view.get_all = AsyncMock(return_value=[])

        uow = FakeUnitOfWork(view_repo=mock_view)

        await view_patient(uow, company=_COMPANY_ID, include_deleted=True)
        mock_view.get_all.assert_awaited_once_with(
            company=_COMPANY_ID, include_deleted=True
        )
