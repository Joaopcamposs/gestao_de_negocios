"""Testes unitários para o agregado LegalCase do contexto advogado."""

from datetime import date

import pytest
import uuid7

from messagebus.entities import OperationType
from services.lawyer.domain.aggregate.legal_case import LegalCase
from services.lawyer.domain.commands.legal_case import (
    CreateLegalCase,
    DeleteLegalCase,
    UpdateLegalCase,
)
from services.lawyer.domain.entities.legal_case import LegalCase as LegalCaseEntity
from services.lawyer.domain.events.legal_case import (
    LegalCaseCreated,
    LegalCaseDeleted,
    LegalCaseUpdated,
)
from services.lawyer.domain.exceptions import (
    LegalCaseAlreadyRegistered,
    LegalCaseNotFound,
)

_TEST_COMPANY_ID = uuid7.create()


class TestLegalCaseAggregate:
    """Testes para o agregado LegalCase."""

    def test_create_aggregate_returns_legal_case(self) -> None:
        lc = LegalCase.create_aggregate(
            company=_TEST_COMPANY_ID,
            case_number="0001234-56.2024.8.26.0100",
            client_name="João Silva",
        )
        assert lc.case_number == "0001234-56.2024.8.26.0100"
        assert lc.client_name == "João Silva"
        assert lc.company == _TEST_COMPANY_ID
        assert lc.id is not None
        assert lc.deleted is False
        assert lc.status == "open"

    def test_create_aggregate_with_all_fields(self) -> None:
        open_dt = date(2024, 1, 15)
        lc = LegalCase.create_aggregate(
            company=_TEST_COMPANY_ID,
            case_number="0009999-00.2024.8.26.0100",
            client_name="Maria Souza",
            description="Ação trabalhista",
            status="in_progress",
            open_date=open_dt,
            notes="Urgente",
        )
        assert lc.description == "Ação trabalhista"
        assert lc.status == "in_progress"
        assert lc.open_date == open_dt
        assert lc.notes == "Urgente"

    def test_create_sets_operation_type_insert(self) -> None:
        lc = LegalCase.create_aggregate(
            company=_TEST_COMPANY_ID, case_number="001", client_name="Test"
        )
        lc.create()
        assert lc.operation_type == OperationType.INSERT

    def test_create_emits_legal_case_created_event(self) -> None:
        lc = LegalCase.create_aggregate(
            company=_TEST_COMPANY_ID, case_number="001", client_name="Test"
        )
        lc.create()
        assert len(lc.events) == 1
        assert isinstance(lc.events[0], LegalCaseCreated)
        assert lc.events[0].id == lc.id

    def test_update_changes_fields(self) -> None:
        lc = LegalCase.create_aggregate(
            company=_TEST_COMPANY_ID, case_number="001", client_name="Old"
        )
        lc.update(client_name="New", status="closed")
        assert lc.client_name == "New"
        assert lc.status == "closed"
        assert lc.operation_type == OperationType.UPDATE

    def test_update_emits_event(self) -> None:
        lc = LegalCase.create_aggregate(
            company=_TEST_COMPANY_ID, case_number="001", client_name="Test"
        )
        lc.update(client_name="Updated")
        assert len(lc.events) == 1
        assert isinstance(lc.events[0], LegalCaseUpdated)

    def test_update_does_not_change_none_fields(self) -> None:
        lc = LegalCase.create_aggregate(
            company=_TEST_COMPANY_ID,
            case_number="001",
            client_name="Original",
            status="open",
        )
        lc.update(client_name="Changed")
        assert lc.client_name == "Changed"
        assert lc.status == "open"

    def test_delete_sets_deleted_true(self) -> None:
        lc = LegalCase.create_aggregate(
            company=_TEST_COMPANY_ID, case_number="001", client_name="Test"
        )
        lc.delete()
        assert lc.deleted is True
        assert lc.operation_type == OperationType.DELETE

    def test_delete_emits_event(self) -> None:
        lc = LegalCase.create_aggregate(
            company=_TEST_COMPANY_ID, case_number="001", client_name="Test"
        )
        lc.delete()
        assert len(lc.events) == 1
        assert isinstance(lc.events[0], LegalCaseDeleted)

    def test_hash_by_id(self) -> None:
        lc = LegalCase.create_aggregate(
            company=_TEST_COMPANY_ID, case_number="001", client_name="Test"
        )
        assert hash(lc) == hash(lc.id)


class TestLegalCaseCommands:
    """Testes para os comandos do LegalCase."""

    def test_create_command(self) -> None:
        cmd = CreateLegalCase(
            company=_TEST_COMPANY_ID, case_number="001", client_name="João"
        )
        assert cmd.company == _TEST_COMPANY_ID
        assert cmd.case_number == "001"
        assert cmd.client_name == "João"
        assert cmd.status == "open"

    def test_update_command(self) -> None:
        cmd = UpdateLegalCase(
            company=_TEST_COMPANY_ID, case_number="001", new_status="closed"
        )
        assert cmd.company == _TEST_COMPANY_ID
        assert cmd.case_number == "001"
        assert cmd.new_status == "closed"
        assert cmd.new_client_name is None

    def test_delete_command(self) -> None:
        cmd = DeleteLegalCase(company=_TEST_COMPANY_ID, case_number="001")
        assert cmd.company == _TEST_COMPANY_ID
        assert cmd.case_number == "001"


class TestLegalCaseEvents:
    """Testes para os eventos do LegalCase."""

    def test_created_event(self) -> None:
        event = LegalCaseCreated(id=uuid7.create(), company=_TEST_COMPANY_ID)
        assert event.id is not None
        assert event.company == _TEST_COMPANY_ID

    def test_updated_event(self) -> None:
        event = LegalCaseUpdated(id=uuid7.create(), company=_TEST_COMPANY_ID)
        assert event.id is not None

    def test_deleted_event(self) -> None:
        event = LegalCaseDeleted(id=uuid7.create(), company=_TEST_COMPANY_ID)
        assert event.id is not None


class TestLegalCaseEntity:
    """Testes para a entidade de leitura LegalCase."""

    def test_entity_is_frozen(self) -> None:
        entity = LegalCaseEntity(
            id=uuid7.create(),
            company=_TEST_COMPANY_ID,
            case_number="001",
            client_name="Test",
            deleted=False,
        )
        with pytest.raises(AttributeError):
            entity.client_name = "Changed"  # type: ignore[misc]

    def test_entity_with_optional_fields(self) -> None:
        entity = LegalCaseEntity(
            id=uuid7.create(),
            company=_TEST_COMPANY_ID,
            case_number="001",
            client_name="Test",
            deleted=False,
        )
        assert entity.description is None
        assert entity.open_date is None
        assert entity.notes is None
        assert entity.status == "open"


class TestLegalCaseExceptions:
    """Testes para as exceções do domínio LegalCase."""

    def test_already_registered(self) -> None:
        exc = LegalCaseAlreadyRegistered()
        assert exc.status_code == 409

    def test_not_found(self) -> None:
        exc = LegalCaseNotFound()
        assert exc.status_code == 404
