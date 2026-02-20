"""Testes unitários para os handlers do Patient no contexto dentista."""

from unittest.mock import AsyncMock, MagicMock
from datetime import date

import uuid7

from services.dentist.domain.commands.patient import (
    CreatePatient,
    DeletePatient,
    UpdatePatient,
)
from services.dentist.domain.events.patient import (
    PatientCreated,
    PatientDeleted,
    PatientUpdated,
)
from services.dentist.services.handlers.patient import (
    create_patient,
    delete_patient,
    patient_created,
    patient_deleted,
    patient_updated,
    update_patient,
)
from tests.unit.conftest import FakeUnitOfWork


_COMPANY_ID = uuid7.create()
_PATIENT_ID = uuid7.create()


class TestCreatePatient:
    async def test_create_patient(self) -> None:
        mock_repo = AsyncMock()
        mock_patient = MagicMock()
        mock_patient.id = _PATIENT_ID
        mock_repo.create_aggregate = AsyncMock(return_value=mock_patient)

        uow = FakeUnitOfWork(domain_repo=mock_repo)

        command = CreatePatient(
            company=_COMPANY_ID,
            name="João Silva",
            cpf="12345678901",
            phone="11999999999",
            birth_date=date(1990, 1, 1),
            notes="Alérgico",
        )

        result = await create_patient(command, uow)

        assert result == _PATIENT_ID
        mock_repo.create_aggregate.assert_awaited_once()
        mock_patient.create.assert_called_once()
        mock_repo.add.assert_awaited_once()


class TestUpdatePatient:
    async def test_update_patient(self) -> None:
        mock_repo = AsyncMock()
        mock_patient = MagicMock()
        mock_repo.get_by_cpf = AsyncMock(return_value=mock_patient)

        uow = FakeUnitOfWork(domain_repo=mock_repo)

        command = UpdatePatient(
            company=_COMPANY_ID,
            cpf="12345678901",
            new_name="Maria Souza",
        )

        await update_patient(command, uow)

        mock_repo.get_by_cpf.assert_awaited_once()
        mock_patient.update.assert_called_once()
        mock_repo.add.assert_awaited_once()


class TestDeletePatient:
    async def test_delete_patient(self) -> None:
        mock_repo = AsyncMock()
        mock_patient = MagicMock()
        mock_repo.get_by_cpf = AsyncMock(return_value=mock_patient)

        uow = FakeUnitOfWork(domain_repo=mock_repo)

        command = DeletePatient(company=_COMPANY_ID, cpf="12345678901")

        await delete_patient(command, uow)

        mock_patient.delete.assert_called_once()
        mock_repo.remove.assert_awaited_once()


class TestPatientEventHandlers:
    async def test_patient_created(self) -> None:
        event = PatientCreated(id=_PATIENT_ID, company=_COMPANY_ID)
        uow = FakeUnitOfWork()
        await patient_created(event, uow)

    async def test_patient_updated(self) -> None:
        event = PatientUpdated(id=_PATIENT_ID, company=_COMPANY_ID)
        uow = FakeUnitOfWork()
        await patient_updated(event, uow)

    async def test_patient_deleted(self) -> None:
        event = PatientDeleted(id=_PATIENT_ID, company=_COMPANY_ID)
        uow = FakeUnitOfWork()
        await patient_deleted(event, uow)
