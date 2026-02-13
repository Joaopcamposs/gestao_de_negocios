"""Testes de integração para o fluxo de Patient no contexto dentista."""

from datetime import date
from uuid import UUID

import pytest
import uuid7

from infra.database.unit_of_work import UnitOfWork
from services.dentist.adapters.views.patient import view_patient
from services.dentist.bootstrap import bootstrap_dentist
from services.dentist.domain.commands.patient import (
    CreatePatient,
    DeletePatient,
    UpdatePatient,
)
from services.dentist.domain.exceptions import PatientAlreadyRegistered, PatientNotFound

_TEST_COMPANY_ID = uuid7.create()


def _bootstrap(**kwargs):
    """Bootstrap do dentist para testes, usando schema public."""
    return bootstrap_dentist(raise_event_errors=True, **kwargs)


def _create_patient_cmd(name: str, cpf: str, **overrides) -> CreatePatient:
    """Função auxiliar para criar comando CreatePatient com valores padrão."""
    defaults = dict(company=_TEST_COMPANY_ID, name=name, cpf=cpf)
    defaults.update(overrides)
    return CreatePatient(**defaults)


class TestCreatePatient:
    """Testes de integração para criação de paciente."""

    async def test_create_patient_returns_uuid(self, engine) -> None:
        """Verifica que criar um paciente retorna um UUID válido."""
        bus = _bootstrap()
        command = _create_patient_cmd("João Silva", "12345678901")

        result = await bus.handle(command)

        assert isinstance(result, UUID)

    async def test_create_patient_persists_in_database(self, engine) -> None:
        """Verifica que o paciente é persistido no banco de dados."""
        bus = _bootstrap()
        await bus.handle(_create_patient_cmd("Maria Souza", "98765432100"))

        uow = UnitOfWork()
        patients = await view_patient(uow, company=_TEST_COMPANY_ID, cpf="98765432100")

        assert len(patients) == 1
        assert patients[0].name == "Maria Souza"
        assert patients[0].cpf == "98765432100"
        assert patients[0].deleted_at is None

    async def test_create_patient_with_all_fields(self, engine) -> None:
        """Verifica que todos os campos do paciente são persistidos."""
        bus = _bootstrap()
        birth = date(1990, 5, 15)
        await bus.handle(
            _create_patient_cmd(
                "Carlos Santos",
                "11122233344",
                phone="11999887766",
                birth_date=birth,
                notes="Alérgico a penicilina",
            )
        )

        uow = UnitOfWork()
        patients = await view_patient(uow, company=_TEST_COMPANY_ID, cpf="11122233344")

        assert len(patients) == 1
        p = patients[0]
        assert p.name == "Carlos Santos"
        assert p.phone == "11999887766"
        assert p.birth_date == birth
        assert p.notes == "Alérgico a penicilina"

    async def test_create_duplicate_patient_raises_error(self, engine) -> None:
        """Verifica que criar paciente com CPF duplicado na mesma empresa lança exceção."""
        bus = _bootstrap()
        await bus.handle(_create_patient_cmd("João", "55566677788"))

        bus2 = _bootstrap()
        with pytest.raises(PatientAlreadyRegistered):
            await bus2.handle(_create_patient_cmd("Outro João", "55566677788"))


class TestUpdatePatient:
    """Testes de integração para atualização de paciente."""

    async def test_update_patient_changes_name(self, engine) -> None:
        """Verifica que a atualização altera o nome do paciente."""
        bus = _bootstrap()
        await bus.handle(_create_patient_cmd("Nome Antigo", "44455566677"))

        bus2 = _bootstrap()
        await bus2.handle(
            UpdatePatient(
                company=_TEST_COMPANY_ID, cpf="44455566677", new_name="Nome Novo"
            )
        )

        uow = UnitOfWork()
        patients = await view_patient(uow, company=_TEST_COMPANY_ID, cpf="44455566677")

        assert len(patients) == 1
        assert patients[0].name == "Nome Novo"

    async def test_update_nonexistent_patient_raises_error(self, engine) -> None:
        """Verifica que atualizar paciente inexistente lança exceção."""
        bus = _bootstrap()

        with pytest.raises(PatientNotFound):
            await bus.handle(
                UpdatePatient(
                    company=_TEST_COMPANY_ID, cpf="00000000000", new_name="Ghost"
                )
            )


class TestDeletePatient:
    """Testes de integração para exclusão (soft delete) de paciente."""

    async def test_delete_patient_soft_deletes(self, engine) -> None:
        """Verifica que a exclusão marca o paciente como deletado."""
        bus = _bootstrap()
        await bus.handle(_create_patient_cmd("Para Excluir", "77788899900"))

        bus2 = _bootstrap()
        await bus2.handle(DeletePatient(company=_TEST_COMPANY_ID, cpf="77788899900"))

        uow = UnitOfWork()
        patients = await view_patient(uow, company=_TEST_COMPANY_ID, cpf="77788899900")
        assert patients == []

    async def test_deleted_patient_visible_with_include_deleted(self, engine) -> None:
        """Verifica que paciente deletado é visível com include_deleted=True."""
        bus = _bootstrap()
        await bus.handle(_create_patient_cmd("Soft Deleted", "33344455566"))

        bus2 = _bootstrap()
        await bus2.handle(DeletePatient(company=_TEST_COMPANY_ID, cpf="33344455566"))

        uow = UnitOfWork()
        patients = await view_patient(
            uow, company=_TEST_COMPANY_ID, cpf="33344455566", include_deleted=True
        )

        assert len(patients) == 1
        assert patients[0].deleted_at is not None

    async def test_delete_nonexistent_patient_raises_error(self, engine) -> None:
        """Verifica que excluir paciente inexistente lança exceção."""
        bus = _bootstrap()

        with pytest.raises(PatientNotFound):
            await bus.handle(DeletePatient(company=_TEST_COMPANY_ID, cpf="00000000000"))


class TestViewPatient:
    """Testes de integração para consulta de paciente."""

    async def test_view_all_patients(self, engine) -> None:
        """Verifica que consultar sem filtro retorna todos os pacientes da empresa."""
        bus = _bootstrap()
        await bus.handle(_create_patient_cmd("Patient A", "11111111111"))
        bus2 = _bootstrap()
        await bus2.handle(_create_patient_cmd("Patient B", "22222222222"))

        uow = UnitOfWork()
        patients = await view_patient(uow, company=_TEST_COMPANY_ID)

        assert len(patients) == 2
        names = {p.name for p in patients}
        assert names == {"Patient A", "Patient B"}

    async def test_view_patients_empty_database(self, engine) -> None:
        """Verifica que consultar sem dados retorna lista vazia."""
        uow = UnitOfWork()
        patients = await view_patient(uow, company=_TEST_COMPANY_ID)

        assert patients == []

    async def test_view_patients_excludes_deleted(self, engine) -> None:
        """Verifica que consultar sem include_deleted exclui pacientes deletados."""
        bus = _bootstrap()
        await bus.handle(_create_patient_cmd("Active", "66677788899"))
        bus2 = _bootstrap()
        await bus2.handle(_create_patient_cmd("Deleted", "99988877766"))

        bus3 = _bootstrap()
        await bus3.handle(DeletePatient(company=_TEST_COMPANY_ID, cpf="99988877766"))

        uow = UnitOfWork()
        patients = await view_patient(uow, company=_TEST_COMPANY_ID)

        assert len(patients) == 1
        assert patients[0].name == "Active"
