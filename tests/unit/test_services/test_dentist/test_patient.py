"""Testes unitários para o agregado Patient do contexto dentista."""

from datetime import date

import uuid7

from messagebus.entities import OperationType
from services.dentist.domain.aggregate.patient import Patient
from services.dentist.domain.commands.patient import (
    CreatePatient,
    DeletePatient,
    UpdatePatient,
)
from services.dentist.domain.entities.patient import Patient as PatientEntity
from services.dentist.domain.events.patient import (
    PatientCreated,
    PatientDeleted,
    PatientUpdated,
)
from services.dentist.domain.exceptions import PatientAlreadyRegistered, PatientNotFound

_TEST_COMPANY_ID = uuid7.create()


class TestPatientAggregate:
    """Testes para o agregado Patient."""

    def test_create_aggregate_returns_patient(self) -> None:
        """Verifica que create_aggregate retorna um Patient com ID gerado."""
        patient = Patient.create_aggregate(
            company=_TEST_COMPANY_ID,
            name="João Silva",
            cpf="12345678901",
        )

        assert patient.name == "João Silva"
        assert patient.cpf == "12345678901"
        assert patient.company == _TEST_COMPANY_ID
        assert patient.id is not None
        assert patient.is_deleted is False

    def test_create_aggregate_with_all_fields(self) -> None:
        """Verifica que create_aggregate aceita todos os campos opcionais."""
        birth = date(1990, 5, 15)
        patient = Patient.create_aggregate(
            company=_TEST_COMPANY_ID,
            name="Maria Souza",
            cpf="98765432100",
            phone="11999887766",
            birth_date=birth,
            notes="Alérgica a anestésico",
        )

        assert patient.phone == "11999887766"
        assert patient.birth_date == birth
        assert patient.notes == "Alérgica a anestésico"

    def test_create_sets_operation_type_insert(self) -> None:
        """Verifica que create() define operation_type como INSERT."""
        patient = Patient.create_aggregate(
            company=_TEST_COMPANY_ID, name="Test", cpf="11111111111"
        )
        patient.create()

        assert patient.operation_type == OperationType.INSERT

    def test_create_emits_patient_created_event(self) -> None:
        """Verifica que create() emite evento PatientCreated."""
        patient = Patient.create_aggregate(
            company=_TEST_COMPANY_ID, name="Test", cpf="11111111111"
        )
        patient.create()

        assert len(patient.events) == 1
        event = patient.events[0]
        assert isinstance(event, PatientCreated)
        assert event.id == patient.id
        assert event.company == _TEST_COMPANY_ID

    def test_update_changes_fields(self) -> None:
        """Verifica que update() altera os campos informados."""
        patient = Patient.create_aggregate(
            company=_TEST_COMPANY_ID, name="Old Name", cpf="11111111111"
        )
        patient.update(name="New Name", phone="11888776655")

        assert patient.name == "New Name"
        assert patient.phone == "11888776655"
        assert patient.operation_type == OperationType.UPDATE

    def test_update_emits_patient_updated_event(self) -> None:
        """Verifica que update() emite evento PatientUpdated."""
        patient = Patient.create_aggregate(
            company=_TEST_COMPANY_ID, name="Test", cpf="11111111111"
        )
        patient.update(name="Updated")

        assert len(patient.events) == 1
        assert isinstance(patient.events[0], PatientUpdated)

    def test_update_does_not_change_none_fields(self) -> None:
        """Verifica que update() não altera campos não informados."""
        patient = Patient.create_aggregate(
            company=_TEST_COMPANY_ID,
            name="Original",
            cpf="11111111111",
            phone="11999999999",
        )
        patient.update(name="Changed")

        assert patient.name == "Changed"
        assert patient.phone == "11999999999"

    def test_delete_sets_deleted_at(self) -> None:
        """Verifica que delete() preenche deleted_at com a data atual."""
        patient = Patient.create_aggregate(
            company=_TEST_COMPANY_ID, name="Test", cpf="11111111111"
        )
        patient.delete()

        assert patient.is_deleted is True
        assert patient.deleted_at is not None
        assert patient.operation_type == OperationType.DELETE

    def test_delete_emits_patient_deleted_event(self) -> None:
        """Verifica que delete() emite evento PatientDeleted."""
        patient = Patient.create_aggregate(
            company=_TEST_COMPANY_ID, name="Test", cpf="11111111111"
        )
        patient.delete()

        assert len(patient.events) == 1
        assert isinstance(patient.events[0], PatientDeleted)

    def test_patient_hash_by_id(self) -> None:
        """Verifica que hash do Patient é baseado no ID."""
        patient = Patient.create_aggregate(
            company=_TEST_COMPANY_ID, name="Test", cpf="11111111111"
        )
        assert hash(patient) == hash(patient.id)


class TestPatientCommands:
    """Testes para os comandos do Patient."""

    def test_create_patient_command(self) -> None:
        """Verifica que CreatePatient tem os campos esperados."""
        cmd = CreatePatient(
            company=_TEST_COMPANY_ID, name="João", cpf="12345678901", phone="11999999999"
        )

        assert cmd.company == _TEST_COMPANY_ID
        assert cmd.name == "João"
        assert cmd.cpf == "12345678901"
        assert cmd.phone == "11999999999"
        assert cmd.birth_date is None
        assert cmd.notes is None

    def test_update_patient_command(self) -> None:
        """Verifica que UpdatePatient tem os campos esperados."""
        cmd = UpdatePatient(company=_TEST_COMPANY_ID, cpf="12345678901", new_name="Maria")

        assert cmd.company == _TEST_COMPANY_ID
        assert cmd.cpf == "12345678901"
        assert cmd.new_name == "Maria"
        assert cmd.new_phone is None

    def test_delete_patient_command(self) -> None:
        """Verifica que DeletePatient tem os campos esperados."""
        cmd = DeletePatient(company=_TEST_COMPANY_ID, cpf="12345678901")
        assert cmd.company == _TEST_COMPANY_ID
        assert cmd.cpf == "12345678901"


class TestPatientEvents:
    """Testes para os eventos do Patient."""

    def test_patient_created_event(self) -> None:
        """Verifica os campos do evento PatientCreated."""
        event = PatientCreated(id=uuid7.create(), company=_TEST_COMPANY_ID)

        assert event.id is not None
        assert event.company == _TEST_COMPANY_ID

    def test_patient_updated_event(self) -> None:
        """Verifica os campos do evento PatientUpdated."""
        event = PatientUpdated(id=uuid7.create(), company=_TEST_COMPANY_ID)

        assert event.id is not None
        assert event.company == _TEST_COMPANY_ID

    def test_patient_deleted_event(self) -> None:
        """Verifica os campos do evento PatientDeleted."""
        event = PatientDeleted(id=uuid7.create(), company=_TEST_COMPANY_ID)

        assert event.id is not None
        assert event.company == _TEST_COMPANY_ID


class TestPatientEntity:
    """Testes para a entidade de leitura Patient."""

    def test_patient_entity_inherits_audit_base(self) -> None:
        """Verifica que a entidade Patient herda os campos de auditoria de AuditBase."""
        from messagebus.entities import AuditBase

        entity = PatientEntity(
            id=uuid7.create(),
            company=_TEST_COMPANY_ID,
            name="Test",
            cpf="11111111111",
        )

        assert isinstance(entity, AuditBase)
        assert entity.created_at is None
        assert entity.updated_at is None
        assert entity.deleted_at is None
        assert entity.deleted_by is None

    def test_patient_entity_with_optional_fields(self) -> None:
        """Verifica que campos opcionais têm valor None por padrão."""
        entity = PatientEntity(
            id=uuid7.create(),
            company=_TEST_COMPANY_ID,
            name="Test",
            cpf="11111111111",
        )

        assert entity.phone is None
        assert entity.birth_date is None
        assert entity.notes is None


class TestPatientExceptions:
    """Testes para as exceções do domínio Patient."""

    def test_patient_already_registered(self) -> None:
        """Verifica a exceção PatientAlreadyRegistered."""
        exc = PatientAlreadyRegistered()
        assert exc.status_code == 409
        assert exc.detail == "Patient CPF already registered"

    def test_patient_not_found(self) -> None:
        """Verifica a exceção PatientNotFound."""
        exc = PatientNotFound()
        assert exc.status_code == 404
        assert exc.detail == "Patient not found"
