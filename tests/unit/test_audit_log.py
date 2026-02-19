"""Testes unitários para o sistema de auditoria."""

from datetime import datetime, timezone
from uuid import UUID

import pytest
import uuid7

from messagebus.entities import AuditableEvent
from messagebus.messagebus import Event
from shared_core.domain.aggregate.audit_log import AuditLog
from shared_core.domain.entities.audit_log import AuditLog as AuditLogRead


_TEST_COMPANY_ID = uuid7.create()
_TEST_USER_ID = uuid7.create()


class TestAuditableEvent:
    """Testes para o mixin AuditableEvent."""

    def test_auditable_event_default_values(self) -> None:
        """Verifica que os valores padrão do AuditableEvent são corretos."""
        event = AuditableEvent()

        assert event.entity_type == ""
        assert event.old_data is None
        assert event.new_data is None

    def test_auditable_event_with_data(self) -> None:
        """Verifica que o AuditableEvent aceita dados de auditoria."""
        old = {"name": "Old Name"}
        new = {"name": "New Name"}
        event = AuditableEvent(
            entity_type="TestEntity",
            old_data=old,
            new_data=new,
        )

        assert event.entity_type == "TestEntity"
        assert event.old_data == old
        assert event.new_data == new

    def test_auditable_event_with_none_data(self) -> None:
        """Verifica que o AuditableEvent aceita dados nulos explicitamente."""
        event = AuditableEvent(
            entity_type="TestEntity",
            old_data=None,
            new_data={"field": "value"},
        )

        assert event.old_data is None
        assert event.new_data == {"field": "value"}


class TestAuditableEventInheritance:
    """Testes para herança do AuditableEvent com Event."""

    def test_combined_event_has_both_attributes(self) -> None:
        """Verifica que um evento combinado possui atributos de Event e AuditableEvent."""
        from dataclasses import dataclass

        @dataclass(kw_only=True)
        class TestEvent(AuditableEvent, Event):
            id: UUID

        uid = uuid7.create()
        event = TestEvent(
            id=uid,
            entity_type="Test",
            new_data={"key": "value"},
        )

        assert event.id == uid
        assert event.entity_type == "Test"
        assert event.new_data == {"key": "value"}
        assert event.execute_async is False
        assert isinstance(event, Event)
        assert isinstance(event, AuditableEvent)


class TestAuditLogEntity:
    """Testes para a entidade de leitura AuditLog."""

    def test_audit_log_creation_with_all_fields(self) -> None:
        """Verifica a criação do AuditLog com todos os campos."""
        uid = uuid7.create()
        entity_id = uuid7.create()
        now = datetime.now(timezone.utc)
        old_data = {"name": "Old"}
        new_data = {"name": "New"}

        audit = AuditLogRead(
            id=uid,
            entity_type="Company",
            entity_id=entity_id,
            operation="UPDATE",
            old_data=old_data,
            new_data=new_data,
            user_id=_TEST_USER_ID,
            created_at=now,
        )

        assert audit.id == uid
        assert audit.entity_type == "Company"
        assert audit.entity_id == entity_id
        assert audit.operation == "UPDATE"
        assert audit.old_data == old_data
        assert audit.new_data == new_data
        assert audit.user_id == _TEST_USER_ID
        assert audit.created_at == now

    def test_audit_log_creation_without_optional_fields(self) -> None:
        """Verifica a criação do AuditLog sem campos opcionais."""
        uid = uuid7.create()
        entity_id = uuid7.create()
        now = datetime.now(timezone.utc)

        audit = AuditLogRead(
            id=uid,
            entity_type="User",
            entity_id=entity_id,
            operation="CREATE",
            created_at=now,
        )

        assert audit.user_id is None
        assert audit.old_data is None
        assert audit.new_data is None

    def test_audit_log_for_create_operation(self) -> None:
        """Verifica que CREATE tem new_data mas não old_data."""
        audit = AuditLogRead(
            id=uuid7.create(),
            entity_type="Patient",
            entity_id=uuid7.create(),
            operation="CREATE",
            old_data=None,
            new_data={"name": "João", "cpf": "12345678901"},
            created_at=datetime.now(timezone.utc),
        )

        assert audit.operation == "CREATE"
        assert audit.old_data is None
        assert audit.new_data is not None
        assert audit.new_data["name"] == "João"

    def test_audit_log_for_update_operation(self) -> None:
        """Verifica que UPDATE tem old_data e new_data."""
        audit = AuditLogRead(
            id=uuid7.create(),
            entity_type="Company",
            entity_id=uuid7.create(),
            operation="UPDATE",
            old_data={"legal_name": "Old Corp"},
            new_data={"legal_name": "New Corp"},
            created_at=datetime.now(timezone.utc),
        )

        assert audit.operation == "UPDATE"
        assert audit.old_data == {"legal_name": "Old Corp"}
        assert audit.new_data == {"legal_name": "New Corp"}

    def test_audit_log_for_delete_operation(self) -> None:
        """Verifica que DELETE tem old_data mas não new_data."""
        audit = AuditLogRead(
            id=uuid7.create(),
            entity_type="User",
            entity_id=uuid7.create(),
            operation="DELETE",
            old_data={"email": "test@test.com", "active": True},
            new_data=None,
            created_at=datetime.now(timezone.utc),
        )

        assert audit.operation == "DELETE"
        assert audit.old_data is not None
        assert audit.new_data is None

    def test_audit_log_is_frozen(self) -> None:
        """Verifica que a entidade AuditLog é imutável (frozen)."""
        audit = AuditLogRead(
            id=uuid7.create(),
            entity_type="Company",
            entity_id=uuid7.create(),
            operation="CREATE",
            created_at=datetime.now(timezone.utc),
        )

        with pytest.raises(AttributeError):
            setattr(audit, "operation", "UPDATE")


class TestCompanyAuditData:
    """Testes para dados de auditoria emitidos pelo agregado Company."""

    def test_create_emits_audit_data_in_event(self) -> None:
        """Verifica que create() popula entity_type e new_data no evento."""
        from shared_core.domain.aggregate.company import Company
        from shared_core.domain.events.company import CompanyCreated

        company = Company.create_aggregate(
            legal_name="Acme Corp",
            trade_name="Acme",
            responsible_name="John Doe",
            email="contact@acme.com",
            cpf="12345678901",
            cnpj="12345678000190",
            active=True,
        )
        company.create(password="secret123")

        created_events = [e for e in company.events if isinstance(e, CompanyCreated)]
        assert len(created_events) == 1

        event = created_events[0]
        assert event.entity_type == "Company"
        assert event.old_data is None
        assert event.new_data is not None
        assert event.new_data["legal_name"] == "Acme Corp"
        assert event.new_data["trade_name"] == "Acme"
        assert event.new_data["responsible_name"] == "John Doe"
        assert event.new_data["email"] == "contact@acme.com"
        assert event.new_data["cpf"] == "12345678901"
        assert event.new_data["cnpj"] == "12345678000190"
        assert event.new_data["active"] is True

    def test_update_emits_old_and_new_data_in_event(self) -> None:
        """Verifica que update() popula old_data e new_data no evento."""
        from shared_core.domain.aggregate.company import Company
        from shared_core.domain.events.company import CompanyUpdated

        company = Company.create_aggregate(
            legal_name="Acme Corp",
            trade_name="Acme",
            responsible_name="John Doe",
            email="contact@acme.com",
            cpf="12345678901",
            cnpj=None,
            active=True,
        )
        company.update(legal_name="New Acme Corp", active=False)

        updated_events = [e for e in company.events if isinstance(e, CompanyUpdated)]
        assert len(updated_events) == 1

        event = updated_events[0]
        assert event.entity_type == "Company"
        assert event.old_data == {"legal_name": "Acme Corp", "active": True}
        assert event.new_data == {"legal_name": "New Acme Corp", "active": False}

    def test_update_only_includes_changed_fields(self) -> None:
        """Verifica que update() inclui apenas os campos alterados."""
        from shared_core.domain.aggregate.company import Company
        from shared_core.domain.events.company import CompanyUpdated

        company = Company.create_aggregate(
            legal_name="Acme Corp",
            trade_name="Acme",
            responsible_name="John Doe",
            email="contact@acme.com",
            cpf="12345678901",
            cnpj=None,
            active=True,
        )
        company.update(email="new@acme.com")

        event = company.events[0]
        assert isinstance(event, CompanyUpdated)
        assert event.old_data == {"email": "contact@acme.com"}
        assert event.new_data == {"email": "new@acme.com"}

    def test_delete_emits_old_data_in_event(self) -> None:
        """Verifica que delete() popula old_data no evento."""
        from shared_core.domain.aggregate.company import Company
        from shared_core.domain.events.company import CompanyDeleted

        company = Company.create_aggregate(
            legal_name="Acme Corp",
            trade_name="Acme",
            responsible_name="John Doe",
            email="contact@acme.com",
            cpf="12345678901",
            cnpj="12345678000190",
            active=True,
        )
        company.delete()

        deleted_events = [e for e in company.events if isinstance(e, CompanyDeleted)]
        assert len(deleted_events) == 1

        event = deleted_events[0]
        assert event.entity_type == "Company"
        assert event.new_data is None
        assert event.old_data is not None
        assert event.old_data["legal_name"] == "Acme Corp"
        assert event.old_data["email"] == "contact@acme.com"
        assert event.old_data["active"] is True


class TestUserAuditData:
    """Testes para dados de auditoria emitidos pelo agregado User."""

    def test_create_emits_audit_data_in_event(self) -> None:
        """Verifica que create() popula entity_type e new_data no evento."""
        from shared_core.domain.aggregate.user import User
        from shared_core.domain.events.user import UserCreated

        user = User.create_aggregate(
            company=_TEST_COMPANY_ID,
            email="test@example.com",
            cpf="12345678901",
            password="secret123",
            active=True,
            admin=False,
        )
        user.create()

        created_events = [e for e in user.events if isinstance(e, UserCreated)]
        assert len(created_events) == 1

        event = created_events[0]
        assert event.entity_type == "User"
        assert event.old_data is None
        assert event.new_data is not None
        assert event.new_data["email"] == "test@example.com"
        assert event.new_data["cpf"] == "12345678901"
        assert event.new_data["active"] is True
        assert event.new_data["admin"] is False

    def test_update_emits_old_and_new_data_in_event(self) -> None:
        """Verifica que update() popula old_data e new_data no evento."""
        from shared_core.domain.aggregate.user import User
        from shared_core.domain.events.user import UserUpdated

        user = User.create_aggregate(
            company=_TEST_COMPANY_ID,
            email="test@example.com",
            cpf="12345678901",
            password="secret123",
        )
        user.update(email="new@example.com", active=False)

        updated_events = [e for e in user.events if isinstance(e, UserUpdated)]
        assert len(updated_events) == 1

        event = updated_events[0]
        assert event.entity_type == "User"
        assert event.old_data["email"] == "test@example.com"
        assert event.new_data["email"] == "new@example.com"
        assert event.old_data["active"] is True
        assert event.new_data["active"] is False

    def test_update_password_is_redacted(self) -> None:
        """Verifica que a senha é redatada nos dados de auditoria."""
        from shared_core.domain.aggregate.user import User
        from shared_core.domain.events.user import UserUpdated

        user = User.create_aggregate(
            company=_TEST_COMPANY_ID,
            email="test@example.com",
            cpf="12345678901",
            password="secret123",
        )
        user.update(password="newpassword")

        event = user.events[0]
        assert isinstance(event, UserUpdated)
        assert event.new_data["password"] == "[REDACTED]"

    def test_delete_emits_old_data_in_event(self) -> None:
        """Verifica que delete() popula old_data no evento."""
        from shared_core.domain.aggregate.user import User
        from shared_core.domain.events.user import UserDeleted

        user = User.create_aggregate(
            company=_TEST_COMPANY_ID,
            email="test@example.com",
            cpf="12345678901",
            password="secret123",
            admin=True,
        )
        user.delete()

        deleted_events = [e for e in user.events if isinstance(e, UserDeleted)]
        assert len(deleted_events) == 1

        event = deleted_events[0]
        assert event.entity_type == "User"
        assert event.new_data is None
        assert event.old_data is not None
        assert event.old_data["email"] == "test@example.com"
        assert event.old_data["cpf"] == "12345678901"
        assert event.old_data["admin"] is True


class TestPatientAuditData:
    """Testes para dados de auditoria emitidos pelo agregado Patient."""

    def test_create_emits_audit_data_in_event(self) -> None:
        """Verifica que create() popula entity_type e new_data no evento."""
        from datetime import date

        from services.dentist.domain.aggregate.patient import Patient
        from services.dentist.domain.events.patient import PatientCreated

        patient = Patient.create_aggregate(
            company=_TEST_COMPANY_ID,
            name="João Silva",
            cpf="12345678901",
            phone="11999887766",
            birth_date=date(1990, 5, 15),
            notes="Alérgico",
        )
        patient.create()

        created_events = [e for e in patient.events if isinstance(e, PatientCreated)]
        assert len(created_events) == 1

        event = created_events[0]
        assert event.entity_type == "Patient"
        assert event.old_data is None
        assert event.new_data is not None
        assert event.new_data["name"] == "João Silva"
        assert event.new_data["cpf"] == "12345678901"
        assert event.new_data["phone"] == "11999887766"
        assert event.new_data["birth_date"] == "1990-05-15"
        assert event.new_data["notes"] == "Alérgico"

    def test_update_emits_old_and_new_data_in_event(self) -> None:
        """Verifica que update() popula old_data e new_data no evento."""
        from services.dentist.domain.aggregate.patient import Patient
        from services.dentist.domain.events.patient import PatientUpdated

        patient = Patient.create_aggregate(
            company=_TEST_COMPANY_ID,
            name="João Silva",
            cpf="12345678901",
            phone="11999887766",
        )
        patient.update(name="Maria Silva", phone="11888776655")

        updated_events = [e for e in patient.events if isinstance(e, PatientUpdated)]
        assert len(updated_events) == 1

        event = updated_events[0]
        assert event.entity_type == "Patient"
        assert event.old_data["name"] == "João Silva"
        assert event.new_data["name"] == "Maria Silva"
        assert event.old_data["phone"] == "11999887766"
        assert event.new_data["phone"] == "11888776655"

    def test_update_only_includes_changed_fields(self) -> None:
        """Verifica que update() inclui apenas os campos alterados."""
        from services.dentist.domain.aggregate.patient import Patient
        from services.dentist.domain.events.patient import PatientUpdated

        patient = Patient.create_aggregate(
            company=_TEST_COMPANY_ID,
            name="João Silva",
            cpf="12345678901",
            phone="11999887766",
        )
        patient.update(notes="Nova observação")

        event = patient.events[0]
        assert isinstance(event, PatientUpdated)
        assert "name" not in event.old_data
        assert "name" not in event.new_data
        assert event.old_data == {"notes": None}
        assert event.new_data == {"notes": "Nova observação"}

    def test_delete_emits_old_data_in_event(self) -> None:
        """Verifica que delete() popula old_data no evento."""
        from services.dentist.domain.aggregate.patient import Patient
        from services.dentist.domain.events.patient import PatientDeleted

        patient = Patient.create_aggregate(
            company=_TEST_COMPANY_ID,
            name="João Silva",
            cpf="12345678901",
        )
        patient.delete()

        deleted_events = [e for e in patient.events if isinstance(e, PatientDeleted)]
        assert len(deleted_events) == 1

        event = deleted_events[0]
        assert event.entity_type == "Patient"
        assert event.new_data is None
        assert event.old_data is not None
        assert event.old_data["name"] == "João Silva"
        assert event.old_data["cpf"] == "12345678901"


class TestLegalCaseAuditData:
    """Testes para dados de auditoria emitidos pelo agregado LegalCase."""

    def test_create_emits_audit_data_in_event(self) -> None:
        """Verifica que create() popula entity_type e new_data no evento."""
        from datetime import date

        from services.lawyer.domain.aggregate.legal_case import LegalCase
        from services.lawyer.domain.events.legal_case import LegalCaseCreated

        legal_case = LegalCase.create_aggregate(
            company=_TEST_COMPANY_ID,
            case_number="0001234-56.2024.8.26.0100",
            client_name="Maria Souza",
            description="Ação cível",
            status="open",
            open_date=date(2024, 1, 15),
            notes="Urgente",
        )
        legal_case.create()

        created_events = [e for e in legal_case.events if isinstance(e, LegalCaseCreated)]
        assert len(created_events) == 1

        event = created_events[0]
        assert event.entity_type == "LegalCase"
        assert event.old_data is None
        assert event.new_data is not None
        assert event.new_data["case_number"] == "0001234-56.2024.8.26.0100"
        assert event.new_data["client_name"] == "Maria Souza"
        assert event.new_data["description"] == "Ação cível"
        assert event.new_data["status"] == "open"
        assert event.new_data["open_date"] == "2024-01-15"
        assert event.new_data["notes"] == "Urgente"

    def test_update_emits_old_and_new_data_in_event(self) -> None:
        """Verifica que update() popula old_data e new_data no evento."""
        from services.lawyer.domain.aggregate.legal_case import LegalCase
        from services.lawyer.domain.events.legal_case import LegalCaseUpdated

        legal_case = LegalCase.create_aggregate(
            company=_TEST_COMPANY_ID,
            case_number="0001234-56.2024.8.26.0100",
            client_name="Maria Souza",
            status="open",
        )
        legal_case.update(client_name="João Silva", status="closed")

        updated_events = [e for e in legal_case.events if isinstance(e, LegalCaseUpdated)]
        assert len(updated_events) == 1

        event = updated_events[0]
        assert event.entity_type == "LegalCase"
        assert event.old_data == {"client_name": "Maria Souza", "status": "open"}
        assert event.new_data == {"client_name": "João Silva", "status": "closed"}

    def test_update_only_includes_changed_fields(self) -> None:
        """Verifica que update() inclui apenas os campos alterados."""
        from services.lawyer.domain.aggregate.legal_case import LegalCase
        from services.lawyer.domain.events.legal_case import LegalCaseUpdated

        legal_case = LegalCase.create_aggregate(
            company=_TEST_COMPANY_ID,
            case_number="0001234-56.2024.8.26.0100",
            client_name="Maria Souza",
            status="open",
        )
        legal_case.update(status="closed")

        event = legal_case.events[0]
        assert isinstance(event, LegalCaseUpdated)
        assert event.old_data == {"status": "open"}
        assert event.new_data == {"status": "closed"}

    def test_delete_emits_old_data_in_event(self) -> None:
        """Verifica que delete() popula old_data no evento."""
        from services.lawyer.domain.aggregate.legal_case import LegalCase
        from services.lawyer.domain.events.legal_case import LegalCaseDeleted

        legal_case = LegalCase.create_aggregate(
            company=_TEST_COMPANY_ID,
            case_number="0001234-56.2024.8.26.0100",
            client_name="Maria Souza",
            status="open",
        )
        legal_case.delete()

        deleted_events = [e for e in legal_case.events if isinstance(e, LegalCaseDeleted)]
        assert len(deleted_events) == 1

        event = deleted_events[0]
        assert event.entity_type == "LegalCase"
        assert event.new_data is None
        assert event.old_data is not None
        assert event.old_data["case_number"] == "0001234-56.2024.8.26.0100"
        assert event.old_data["client_name"] == "Maria Souza"
        assert event.old_data["status"] == "open"


class TestAuditLogDomainRepo:
    """Testes para o repositório de domínio de AuditLog."""

    def test_create_from_event_builds_correct_audit_log(self) -> None:
        """Verifica que create_from_event constrói um AuditLog com dados corretos."""
        from dataclasses import dataclass

        @dataclass(kw_only=True)
        class FakeAuditEvent(AuditableEvent, Event):
            id: UUID

        entity_id = uuid7.create()
        event = FakeAuditEvent(
            id=entity_id,
            entity_type="TestEntity",
            old_data={"field": "old"},
            new_data={"field": "new"},
        )

        audit = AuditLog(
            id=uuid7.create(),
            entity_type=event.entity_type,
            entity_id=entity_id,
            operation="UPDATE",
            old_data=event.old_data,
            new_data=event.new_data,
            user_id=_TEST_USER_ID,
            created_at=datetime.now(timezone.utc),
        )

        assert audit.entity_type == "TestEntity"
        assert audit.entity_id == entity_id
        assert audit.operation == "UPDATE"
        assert audit.old_data == {"field": "old"}
        assert audit.new_data == {"field": "new"}
        assert audit.user_id == _TEST_USER_ID

    def test_audit_log_without_user(self) -> None:
        """Verifica que AuditLog pode ser criado sem user_id (operação de sistema)."""
        audit = AuditLog(
            id=uuid7.create(),
            entity_type="Company",
            entity_id=uuid7.create(),
            operation="CREATE",
            new_data={"legal_name": "Test Corp"},
            created_at=datetime.now(timezone.utc),
        )

        assert audit.user_id is None


class TestEventsAreAuditable:
    """Testes para garantir que os eventos de domínio são auditáveis."""

    def test_company_created_is_auditable(self) -> None:
        """Verifica que CompanyCreated herda de AuditableEvent."""
        from shared_core.domain.events.company import CompanyCreated

        event = CompanyCreated(id=uuid7.create())
        assert isinstance(event, AuditableEvent)
        assert isinstance(event, Event)

    def test_company_updated_is_auditable(self) -> None:
        """Verifica que CompanyUpdated herda de AuditableEvent."""
        from shared_core.domain.events.company import CompanyUpdated

        event = CompanyUpdated(id=uuid7.create())
        assert isinstance(event, AuditableEvent)

    def test_company_deleted_is_auditable(self) -> None:
        """Verifica que CompanyDeleted herda de AuditableEvent."""
        from shared_core.domain.events.company import CompanyDeleted

        event = CompanyDeleted(id=uuid7.create())
        assert isinstance(event, AuditableEvent)

    def test_user_created_is_auditable(self) -> None:
        """Verifica que UserCreated herda de AuditableEvent."""
        from shared_core.domain.events.user import UserCreated

        event = UserCreated(id=uuid7.create(), company=_TEST_COMPANY_ID)
        assert isinstance(event, AuditableEvent)

    def test_user_updated_is_auditable(self) -> None:
        """Verifica que UserUpdated herda de AuditableEvent."""
        from shared_core.domain.events.user import UserUpdated

        event = UserUpdated(id=uuid7.create(), company=_TEST_COMPANY_ID)
        assert isinstance(event, AuditableEvent)

    def test_user_deleted_is_auditable(self) -> None:
        """Verifica que UserDeleted herda de AuditableEvent."""
        from shared_core.domain.events.user import UserDeleted

        event = UserDeleted(id=uuid7.create(), company=_TEST_COMPANY_ID)
        assert isinstance(event, AuditableEvent)

    def test_patient_created_is_auditable(self) -> None:
        """Verifica que PatientCreated herda de AuditableEvent."""
        from services.dentist.domain.events.patient import PatientCreated

        event = PatientCreated(id=uuid7.create(), company=_TEST_COMPANY_ID)
        assert isinstance(event, AuditableEvent)

    def test_patient_updated_is_auditable(self) -> None:
        """Verifica que PatientUpdated herda de AuditableEvent."""
        from services.dentist.domain.events.patient import PatientUpdated

        event = PatientUpdated(id=uuid7.create(), company=_TEST_COMPANY_ID)
        assert isinstance(event, AuditableEvent)

    def test_patient_deleted_is_auditable(self) -> None:
        """Verifica que PatientDeleted herda de AuditableEvent."""
        from services.dentist.domain.events.patient import PatientDeleted

        event = PatientDeleted(id=uuid7.create(), company=_TEST_COMPANY_ID)
        assert isinstance(event, AuditableEvent)

    def test_legal_case_created_is_auditable(self) -> None:
        """Verifica que LegalCaseCreated herda de AuditableEvent."""
        from services.lawyer.domain.events.legal_case import LegalCaseCreated

        event = LegalCaseCreated(id=uuid7.create(), company=_TEST_COMPANY_ID)
        assert isinstance(event, AuditableEvent)
        assert isinstance(event, Event)

    def test_legal_case_updated_is_auditable(self) -> None:
        """Verifica que LegalCaseUpdated herda de AuditableEvent."""
        from services.lawyer.domain.events.legal_case import LegalCaseUpdated

        event = LegalCaseUpdated(id=uuid7.create(), company=_TEST_COMPANY_ID)
        assert isinstance(event, AuditableEvent)

    def test_legal_case_deleted_is_auditable(self) -> None:
        """Verifica que LegalCaseDeleted herda de AuditableEvent."""
        from services.lawyer.domain.events.legal_case import LegalCaseDeleted

        event = LegalCaseDeleted(id=uuid7.create(), company=_TEST_COMPANY_ID)
        assert isinstance(event, AuditableEvent)


class TestReadAuditLogSchema:
    """Testes para o schema de leitura de AuditLog."""

    def test_schema_with_all_fields(self) -> None:
        """Verifica que o schema aceita todos os campos."""
        from shared_core.entrypoints.schemas.audit_log import ReadAuditLogSchema

        now = datetime.now(timezone.utc)
        schema = ReadAuditLogSchema(
            id=uuid7.create(),
            entity_type="Company",
            entity_id=uuid7.create(),
            operation="CREATE",
            old_data=None,
            new_data={"legal_name": "Acme"},
            user_id=_TEST_USER_ID,
            created_at=now,
        )

        assert schema.entity_type == "Company"
        assert schema.operation == "CREATE"
        assert schema.old_data is None
        assert schema.new_data == {"legal_name": "Acme"}
        assert schema.user_id == _TEST_USER_ID
        assert schema.created_at == now

    def test_schema_with_optional_fields_none(self) -> None:
        """Verifica que campos opcionais do schema são None por padrão."""
        from shared_core.entrypoints.schemas.audit_log import ReadAuditLogSchema

        schema = ReadAuditLogSchema(
            id=uuid7.create(),
            entity_type="User",
            entity_id=uuid7.create(),
            operation="DELETE",
            created_at=datetime.now(timezone.utc),
        )

        assert schema.old_data is None
        assert schema.new_data is None
        assert schema.user_id is None

    def test_schema_serializes_from_entity(self) -> None:
        """Verifica que o schema pode ser criado a partir de uma entidade AuditLog."""
        from shared_core.entrypoints.schemas.audit_log import ReadAuditLogSchema

        entity = AuditLogRead(
            id=uuid7.create(),
            entity_type="Patient",
            entity_id=uuid7.create(),
            operation="UPDATE",
            old_data={"name": "Old"},
            new_data={"name": "New"},
            user_id=_TEST_USER_ID,
            created_at=datetime.now(timezone.utc),
        )

        schema = ReadAuditLogSchema(
            id=entity.id,
            entity_type=entity.entity_type,
            entity_id=entity.entity_id,
            operation=entity.operation,
            old_data=entity.old_data,
            new_data=entity.new_data,
            user_id=entity.user_id,
            created_at=entity.created_at,
        )

        assert schema.id == entity.id
        assert schema.entity_type == entity.entity_type
        assert schema.entity_id == entity.entity_id
        assert schema.operation == entity.operation
        assert schema.old_data == entity.old_data
        assert schema.new_data == entity.new_data

    def test_schema_update_operation_has_both_data(self) -> None:
        """Verifica que o schema de UPDATE contém old_data e new_data."""
        from shared_core.entrypoints.schemas.audit_log import ReadAuditLogSchema

        schema = ReadAuditLogSchema(
            id=uuid7.create(),
            entity_type="Company",
            entity_id=uuid7.create(),
            operation="UPDATE",
            old_data={"legal_name": "Old Corp"},
            new_data={"legal_name": "New Corp"},
            created_at=datetime.now(timezone.utc),
        )

        assert schema.old_data is not None
        assert schema.new_data is not None


class TestAuditLogDomainRegistration:
    """Testes para o registro do domínio audit_log no enum Domain."""

    def test_audit_log_domain_exists(self) -> None:
        """Verifica que audit_log está registrado no enum Domain."""
        from shared_core.domains import Domain

        assert hasattr(Domain, "audit_log")

    def test_audit_log_domain_has_domain_repo(self) -> None:
        """Verifica que audit_log possui repositório de escrita."""
        from shared_core.adapters.repository.domain_repo.audit_log import (
            AuditLogDomainRepo,
        )
        from shared_core.domains import Domain

        domain_repo_class = Domain.audit_log.value[0]
        assert domain_repo_class is AuditLogDomainRepo

    def test_audit_log_domain_has_view_repo(self) -> None:
        """Verifica que audit_log possui repositório de consulta."""
        from shared_core.adapters.repository.view_repo.audit_log import (
            AuditLogViewRepo,
        )
        from shared_core.domains import Domain

        view_repo_class = Domain.audit_log.value[1]
        assert view_repo_class is AuditLogViewRepo


class TestAuditHandlersRegistration:
    """Testes para o registro dos handlers de auditoria nos event handlers."""

    def test_shared_core_company_events_have_audit_handlers(self) -> None:
        """Verifica que eventos de Company possuem handlers de auditoria no shared_core."""
        from shared_core.domain.events.company import (
            CompanyCreated,
            CompanyDeleted,
            CompanyUpdated,
        )
        from shared_core.handlers import EVENT_HANDLERS
        from shared_core.services.handlers.audit_log import (
            audit_entity_created,
            audit_entity_deleted,
            audit_entity_updated,
        )

        assert audit_entity_created in EVENT_HANDLERS[CompanyCreated]
        assert audit_entity_updated in EVENT_HANDLERS[CompanyUpdated]
        assert audit_entity_deleted in EVENT_HANDLERS[CompanyDeleted]

    def test_shared_core_user_events_have_audit_handlers(self) -> None:
        """Verifica que eventos de User possuem handlers de auditoria no shared_core."""
        from shared_core.domain.events.user import (
            UserCreated,
            UserDeleted,
            UserUpdated,
        )
        from shared_core.handlers import EVENT_HANDLERS
        from shared_core.services.handlers.audit_log import (
            audit_entity_created,
            audit_entity_deleted,
            audit_entity_updated,
        )

        assert audit_entity_created in EVENT_HANDLERS[UserCreated]
        assert audit_entity_updated in EVENT_HANDLERS[UserUpdated]
        assert audit_entity_deleted in EVENT_HANDLERS[UserDeleted]

    def test_dentist_patient_events_have_audit_handlers(self) -> None:
        """Verifica que eventos de Patient possuem handlers de auditoria no dentista."""
        from services.dentist.domain.events.patient import (
            PatientCreated,
            PatientDeleted,
            PatientUpdated,
        )
        from services.dentist.handlers import EVENT_HANDLERS
        from shared_core.services.handlers.audit_log import (
            audit_entity_created,
            audit_entity_deleted,
            audit_entity_updated,
        )

        assert audit_entity_created in EVENT_HANDLERS[PatientCreated]
        assert audit_entity_updated in EVENT_HANDLERS[PatientUpdated]
        assert audit_entity_deleted in EVENT_HANDLERS[PatientDeleted]

    def test_lawyer_legal_case_events_have_audit_handlers(self) -> None:
        """Verifica que eventos de LegalCase possuem handlers de auditoria no advogado."""
        from services.lawyer.domain.events.legal_case import (
            LegalCaseCreated,
            LegalCaseDeleted,
            LegalCaseUpdated,
        )
        from services.lawyer.handlers import EVENT_HANDLERS
        from shared_core.services.handlers.audit_log import (
            audit_entity_created,
            audit_entity_deleted,
            audit_entity_updated,
        )

        assert audit_entity_created in EVENT_HANDLERS[LegalCaseCreated]
        assert audit_entity_updated in EVENT_HANDLERS[LegalCaseUpdated]
        assert audit_entity_deleted in EVENT_HANDLERS[LegalCaseDeleted]


class TestAuditBase:
    """Testes para a classe base AuditBase com campos de auditoria."""

    def test_audit_base_default_values(self) -> None:
        """Verifica que os campos de auditoria possuem valores padrão corretos."""
        from messagebus.entities import AuditBase

        audit = AuditBase()

        assert audit.active is True
        assert audit.created_at is None
        assert audit.created_by is None
        assert audit.updated_at is None
        assert audit.updated_by is None
        assert audit.deleted_at is None
        assert audit.deleted_by is None

    def test_audit_base_is_deleted_false_when_no_deleted_at(self) -> None:
        """Verifica que is_deleted retorna False quando deleted_at é None."""
        from messagebus.entities import AuditBase

        audit = AuditBase()

        assert audit.is_deleted is False

    def test_audit_base_is_deleted_true_when_deleted_at_set(self) -> None:
        """Verifica que is_deleted retorna True quando deleted_at possui valor."""
        from messagebus.entities import AuditBase

        audit = AuditBase(deleted_at=datetime.now(timezone.utc))

        assert audit.is_deleted is True

    def test_audit_base_accepts_all_fields(self) -> None:
        """Verifica que o AuditBase aceita todos os campos de auditoria."""
        from messagebus.entities import AuditBase

        now = datetime.now(timezone.utc)
        user_id = uuid7.create()

        audit = AuditBase(
            active=False,
            created_at=now,
            created_by=user_id,
            updated_at=now,
            updated_by=user_id,
            deleted_at=now,
            deleted_by=user_id,
        )

        assert audit.active is False
        assert audit.created_at == now
        assert audit.created_by == user_id
        assert audit.updated_at == now
        assert audit.updated_by == user_id
        assert audit.deleted_at == now
        assert audit.deleted_by == user_id

    def test_audit_base_can_be_used_standalone(self) -> None:
        """Verifica que AuditBase pode ser usada de forma independente (sem Aggregate)."""
        from dataclasses import dataclass

        from messagebus.entities import AuditBase

        @dataclass(kw_only=True)
        class SimpleEntity(AuditBase):
            """Entidade simples que herda campos de auditoria."""

            name: str

        entity = SimpleEntity(name="Test")

        assert entity.name == "Test"
        assert entity.active is True
        assert entity.created_at is None
        assert entity.is_deleted is False


class TestAggregateInheritsAuditBase:
    """Testes para garantir que Aggregate herda de AuditBase."""

    def test_aggregate_is_subclass_of_audit_base(self) -> None:
        """Verifica que Aggregate é subclasse de AuditBase."""
        from messagebus.entities import Aggregate, AuditBase

        assert issubclass(Aggregate, AuditBase)

    def test_aggregate_instance_is_audit_base(self) -> None:
        """Verifica que uma instância de Aggregate também é AuditBase."""
        from messagebus.entities import Aggregate, AuditBase

        agg = Aggregate()

        assert isinstance(agg, AuditBase)

    def test_aggregate_inherits_audit_fields(self) -> None:
        """Verifica que Aggregate herda todos os campos de auditoria."""
        from messagebus.entities import Aggregate

        agg = Aggregate()

        assert agg.active is True
        assert agg.created_at is None
        assert agg.created_by is None
        assert agg.updated_at is None
        assert agg.updated_by is None
        assert agg.deleted_at is None
        assert agg.deleted_by is None

    def test_aggregate_inherits_is_deleted(self) -> None:
        """Verifica que Aggregate herda a propriedade is_deleted."""
        from messagebus.entities import Aggregate

        agg = Aggregate()
        assert agg.is_deleted is False

        agg.deleted_at = datetime.now(timezone.utc)
        assert agg.is_deleted is True

    def test_aggregate_has_own_fields(self) -> None:
        """Verifica que Aggregate mantém seus campos próprios (events, operation_type)."""
        from messagebus.entities import Aggregate

        agg = Aggregate()

        assert agg.events == []
        assert agg.operation_type is None

    def test_company_is_subclass_of_audit_base(self) -> None:
        """Verifica que Company herda AuditBase via Aggregate."""
        from messagebus.entities import AuditBase
        from shared_core.domain.aggregate.company import Company

        assert issubclass(Company, AuditBase)

        company = Company.create_aggregate(
            legal_name="Test Corp",
            trade_name=None,
            responsible_name="John",
            email="a@b.com",
            cpf="12345678901",
            cnpj=None,
            active=True,
        )

        assert isinstance(company, AuditBase)
        assert company.active is True
        assert company.created_at is None
        assert company.is_deleted is False

    def test_company_delete_sets_deleted_at(self) -> None:
        """Verifica que Company.delete() preenche deleted_at."""
        from shared_core.domain.aggregate.company import Company

        company = Company.create_aggregate(
            legal_name="Del Corp",
            trade_name=None,
            responsible_name="John",
            email="a@b.com",
            cpf="12345678901",
            cnpj=None,
            active=True,
        )
        company.delete()

        assert company.is_deleted is True
        assert company.deleted_at is not None
        assert isinstance(company.deleted_at, datetime)

    def test_user_is_subclass_of_audit_base(self) -> None:
        """Verifica que User herda AuditBase via Aggregate."""
        from messagebus.entities import AuditBase
        from shared_core.domain.aggregate.user import User

        assert issubclass(User, AuditBase)

        user = User.create_aggregate(
            company=uuid7.create(),
            email="test@example.com",
            cpf="12345678901",
            password="secret",
        )

        assert isinstance(user, AuditBase)
        assert user.active is True
        assert user.is_deleted is False

    def test_user_delete_sets_deleted_at(self) -> None:
        """Verifica que User.delete() preenche deleted_at."""
        from shared_core.domain.aggregate.user import User

        user = User.create_aggregate(
            company=uuid7.create(),
            email="test@example.com",
            cpf="12345678901",
            password="secret",
        )
        user.delete()

        assert user.is_deleted is True
        assert user.deleted_at is not None

    def test_public_user_is_subclass_of_audit_base(self) -> None:
        """Verifica que PublicUser herda AuditBase via Aggregate."""
        from messagebus.entities import AuditBase
        from shared_core.domain.aggregate.user import PublicUser, User

        assert issubclass(PublicUser, AuditBase)

        user = User.create_aggregate(
            company=uuid7.create(),
            email="test@example.com",
            cpf="12345678901",
            password="secret",
        )
        public = PublicUser.create_registration_aggregate(user=user)

        assert isinstance(public, AuditBase)
        assert public.active is True
        assert public.is_deleted is False

    def test_public_user_remove_sets_deleted_at(self) -> None:
        """Verifica que PublicUser.remove() preenche deleted_at."""
        from shared_core.domain.aggregate.user import PublicUser, User

        user = User.create_aggregate(
            company=uuid7.create(),
            email="test@example.com",
            cpf="12345678901",
            password="secret",
        )
        public = PublicUser.create_registration_aggregate(user=user)
        public.remove()

        assert public.is_deleted is True
        assert public.deleted_at is not None

    def test_patient_is_subclass_of_audit_base(self) -> None:
        """Verifica que Patient herda AuditBase via Aggregate."""
        from messagebus.entities import AuditBase
        from services.dentist.domain.aggregate.patient import Patient

        assert issubclass(Patient, AuditBase)

        patient = Patient.create_aggregate(
            company=uuid7.create(),
            name="Test",
            cpf="12345678901",
        )

        assert isinstance(patient, AuditBase)
        assert patient.active is True
        assert patient.is_deleted is False

    def test_patient_delete_sets_deleted_at(self) -> None:
        """Verifica que Patient.delete() preenche deleted_at."""
        from services.dentist.domain.aggregate.patient import Patient

        patient = Patient.create_aggregate(
            company=uuid7.create(),
            name="Test",
            cpf="12345678901",
        )
        patient.delete()

        assert patient.is_deleted is True
        assert patient.deleted_at is not None

    def test_legal_case_is_subclass_of_audit_base(self) -> None:
        """Verifica que LegalCase herda AuditBase via Aggregate."""
        from messagebus.entities import AuditBase
        from services.lawyer.domain.aggregate.legal_case import LegalCase

        assert issubclass(LegalCase, AuditBase)

        lc = LegalCase.create_aggregate(
            company=uuid7.create(),
            case_number="001",
            client_name="Test",
        )

        assert isinstance(lc, AuditBase)
        assert lc.active is True
        assert lc.is_deleted is False

    def test_legal_case_delete_sets_deleted_at(self) -> None:
        """Verifica que LegalCase.delete() preenche deleted_at."""
        from services.lawyer.domain.aggregate.legal_case import LegalCase

        lc = LegalCase.create_aggregate(
            company=uuid7.create(),
            case_number="001",
            client_name="Test",
        )
        lc.delete()

        assert lc.is_deleted is True
        assert lc.deleted_at is not None

    def test_audit_fields_in_orm_company_table(self) -> None:
        """Verifica que a tabela company possui colunas de auditoria no ORM."""
        from shared_core.adapters.orm.company import company

        column_names = [c.name for c in company.columns]
        assert "created_at" in column_names
        assert "created_by" in column_names
        assert "updated_at" in column_names
        assert "updated_by" in column_names
        assert "deleted_at" in column_names
        assert "deleted_by" in column_names
        assert "active" in column_names
        assert "deleted" not in column_names

    def test_audit_fields_in_orm_user_table(self) -> None:
        """Verifica que a tabela user possui colunas de auditoria no ORM."""
        from shared_core.adapters.orm.user import user

        column_names = [c.name for c in user.columns]
        assert "created_at" in column_names
        assert "created_by" in column_names
        assert "updated_at" in column_names
        assert "updated_by" in column_names
        assert "deleted_at" in column_names
        assert "deleted_by" in column_names
        assert "active" in column_names
        assert "deleted" not in column_names

    def test_audit_fields_in_orm_public_user_table(self) -> None:
        """Verifica que a tabela public_user possui colunas de auditoria no ORM."""
        from shared_core.adapters.orm.user import public_user

        column_names = [c.name for c in public_user.columns]
        assert "created_at" in column_names
        assert "created_by" in column_names
        assert "deleted_at" in column_names
        assert "deleted_by" in column_names
        assert "deleted" not in column_names

    def test_audit_fields_in_orm_patient_table(self) -> None:
        """Verifica que a tabela patient possui colunas de auditoria no ORM."""
        from services.dentist.adapters.orm.patient import patient

        column_names = [c.name for c in patient.columns]
        assert "created_at" in column_names
        assert "created_by" in column_names
        assert "updated_at" in column_names
        assert "updated_by" in column_names
        assert "deleted_at" in column_names
        assert "deleted_by" in column_names
        assert "active" in column_names
        assert "deleted" not in column_names

    def test_audit_fields_in_orm_legal_case_table(self) -> None:
        """Verifica que a tabela legal_case possui colunas de auditoria no ORM."""
        from services.lawyer.adapters.orm.legal_case import legal_case

        column_names = [c.name for c in legal_case.columns]
        assert "created_at" in column_names
        assert "created_by" in column_names
        assert "updated_at" in column_names
        assert "updated_by" in column_names
        assert "deleted_at" in column_names
        assert "deleted_by" in column_names
        assert "active" in column_names
        assert "deleted" not in column_names

    def test_read_entity_company_uses_deleted_at(self) -> None:
        """Verifica que a entidade de leitura Company usa deleted_at."""
        from shared_core.domain.entities.company import Company

        entity = Company(
            id=uuid7.create(),
            legal_name="Test",
            responsible_name="John",
            email="a@b.com",
            cpf="12345678901",
            active=True,
        )
        assert entity.deleted_at is None

        now = datetime.now(timezone.utc)
        entity_deleted = Company(
            id=uuid7.create(),
            legal_name="Test",
            responsible_name="John",
            email="a@b.com",
            cpf="12345678901",
            active=True,
            deleted_at=now,
        )
        assert entity_deleted.deleted_at == now

    def test_read_entity_user_uses_deleted_at(self) -> None:
        """Verifica que a entidade de leitura User usa deleted_at."""
        from shared_core.domain.entities.user import User

        entity = User(
            id=uuid7.create(),
            company=uuid7.create(),
            email="a@b.com",
            cpf="12345678901",
            active=True,
            admin=False,
        )
        assert entity.deleted_at is None

    def test_read_schema_company_uses_deleted_at(self) -> None:
        """Verifica que o schema ReadCompanySchema usa deleted_at."""
        from shared_core.entrypoints.schemas.company import ReadCompanySchema

        schema = ReadCompanySchema(
            id=uuid7.create(),
            legal_name="Test",
            responsible_name="John",
            email="a@b.com",
            cpf="12345678901",
            active=True,
        )
        assert schema.deleted_at is None

        now = datetime.now(timezone.utc)
        schema_deleted = ReadCompanySchema(
            id=uuid7.create(),
            legal_name="Test",
            responsible_name="John",
            email="a@b.com",
            cpf="12345678901",
            active=True,
            deleted_at=now,
        )
        assert schema_deleted.deleted_at == now

    def test_read_schema_user_uses_deleted_at(self) -> None:
        """Verifica que o schema ReadUserSchema usa deleted_at."""
        from shared_core.entrypoints.schemas.user import ReadUserSchema

        schema = ReadUserSchema(
            id=uuid7.create(),
            company=uuid7.create(),
            email="a@b.com",
            cpf="12345678901",
            active=True,
            admin=False,
        )
        assert schema.deleted_at is None

    def test_read_schema_patient_uses_deleted_at(self) -> None:
        """Verifica que o schema ReadPatientSchema usa deleted_at."""
        from services.dentist.entrypoints.schemas.patient import ReadPatientSchema

        schema = ReadPatientSchema(
            id=uuid7.create(),
            company=uuid7.create(),
            name="Test",
            cpf="12345678901",
        )
        assert schema.deleted_at is None

    def test_read_schema_legal_case_uses_deleted_at(self) -> None:
        """Verifica que o schema ReadLegalCaseSchema usa deleted_at."""
        from services.lawyer.entrypoints.schemas.legal_case import ReadLegalCaseSchema

        schema = ReadLegalCaseSchema(
            id=uuid7.create(),
            company=uuid7.create(),
            case_number="001",
            client_name="Test",
        )
        assert schema.deleted_at is None


class TestAuditLogApiRouterRegistration:
    """Testes para o registro do router de auditoria nas aplicações."""

    def test_dentist_app_has_audit_log_router(self) -> None:
        """Verifica que a aplicação dentista inclui o router de auditoria."""
        from services.dentist.main import app

        audit_routes = [
            route.path
            for route in app.routes
            if hasattr(route, "path") and "audit" in route.path
        ]
        assert any("/v1/audit-log" in route for route in audit_routes)

    def test_lawyer_app_has_audit_log_router(self) -> None:
        """Verifica que a aplicação advogado inclui o router de auditoria."""
        from services.lawyer.main import app

        audit_routes = [
            route.path
            for route in app.routes
            if hasattr(route, "path") and "audit" in route.path
        ]
        assert any("/v1/audit-log" in route for route in audit_routes)
