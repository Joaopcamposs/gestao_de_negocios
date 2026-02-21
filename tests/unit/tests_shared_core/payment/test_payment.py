"""Testes unitários para o domínio de Payment no shared_core.

Cobre o agregado Payment, comandos, eventos, entidade de leitura, schemas
e os campos de pagamento no agregado Company.
"""

from datetime import UTC, datetime, timedelta
from uuid import UUID

import uuid7

from messagebus.entities import Aggregate, OperationType
from shared_core.domain.aggregate.company import Company
from shared_core.domain.aggregate.payment import Payment
from shared_core.domain.commands.payment import (
    CheckAndDeactivateOverdueCompanies,
    CreatePayment,
    MarkPaymentAsOverdue,
    MarkPaymentAsPaid,
)
from shared_core.domain.entities.payment import Payment as PaymentEntity
from shared_core.domain.events.company import CompanyPaymentStatusUpdated
from shared_core.domain.events.payment import (
    CompanyAndUsersDeactivated,
    CompanyPaymentOverdue,
    CompanyPaymentPaid,
    PaymentCreated,
    PaymentUpdated,
)
from shared_core.domain.value_objects.enums import EntityType, PaymentStatus
from shared_core.entrypoints.schemas.payment import CreatePaymentSchema, ReadPaymentSchema


_TEST_COMPANY_ID = uuid7.create()


def _make_payment(**overrides) -> Payment:
    """Função auxiliar para criar um agregado Payment com valores padrão."""
    defaults = dict(
        company=_TEST_COMPANY_ID,
        amount=150.0,
        due_date=datetime.now(UTC) + timedelta(days=30),
    )
    defaults.update(overrides)
    return Payment.create_aggregate(**defaults)


class TestPaymentAggregate:
    """Testes para o agregado Payment."""

    def test_create_aggregate_returns_payment_with_uuid(self) -> None:
        """Verifica que create_aggregate retorna um Payment com UUID válido."""
        payment = _make_payment()

        assert isinstance(payment.id, UUID)
        assert payment.company == _TEST_COMPANY_ID
        assert payment.amount == 150.0
        assert payment.status == PaymentStatus.PENDING
        assert payment.paid_at is None

    def test_create_aggregate_generates_unique_ids(self) -> None:
        """Verifica que cada chamada gera um ID diferente."""
        p1 = _make_payment()
        p2 = _make_payment()

        assert p1.id != p2.id

    def test_payment_inherits_from_aggregate(self) -> None:
        """Verifica que Payment herda de Aggregate."""
        payment = _make_payment()

        assert isinstance(payment, Aggregate)

    def test_create_sets_insert_operation_type(self) -> None:
        """Verifica que create() define o tipo de operação como INSERT."""
        payment = _make_payment()
        payment.create()

        assert payment._operation_type == OperationType.INSERT

    def test_create_emits_payment_created_event(self) -> None:
        """Verifica que create() emite o evento PaymentCreated."""
        payment = _make_payment()
        payment.create()

        created_events = [e for e in payment.events if isinstance(e, PaymentCreated)]
        assert len(created_events) == 1
        assert created_events[0].id == payment.id
        assert created_events[0].company == _TEST_COMPANY_ID
        assert created_events[0].entity_type == EntityType.PAYMENT

    def test_mark_as_paid_changes_status(self) -> None:
        """Verifica que mark_as_paid altera o status para PAID."""
        payment = _make_payment()
        payment.mark_as_paid()

        assert payment.status == PaymentStatus.PAID
        assert payment.paid_at is not None

    def test_mark_as_paid_sets_update_operation_type(self) -> None:
        """Verifica que mark_as_paid() define o tipo de operação como UPDATE."""
        payment = _make_payment()
        payment.mark_as_paid()

        assert payment._operation_type == OperationType.UPDATE

    def test_mark_as_paid_emits_payment_updated_event(self) -> None:
        """Verifica que mark_as_paid() emite o evento PaymentUpdated."""
        payment = _make_payment()
        payment.mark_as_paid()

        updated_events = [e for e in payment.events if isinstance(e, PaymentUpdated)]
        assert len(updated_events) == 1
        event = updated_events[0]
        assert event.id == payment.id
        assert event.old_data["status"] == PaymentStatus.PENDING
        assert event.new_data["status"] == PaymentStatus.PAID

    def test_mark_as_overdue_changes_status(self) -> None:
        """Verifica que mark_as_overdue altera o status para OVERDUE."""
        payment = _make_payment()
        payment.mark_as_overdue()

        assert payment.status == PaymentStatus.OVERDUE
        assert payment.paid_at is None

    def test_mark_as_overdue_sets_update_operation_type(self) -> None:
        """Verifica que mark_as_overdue() define o tipo de operação como UPDATE."""
        payment = _make_payment()
        payment.mark_as_overdue()

        assert payment._operation_type == OperationType.UPDATE

    def test_mark_as_overdue_emits_payment_updated_event(self) -> None:
        """Verifica que mark_as_overdue() emite o evento PaymentUpdated."""
        payment = _make_payment()
        payment.mark_as_overdue()

        updated_events = [e for e in payment.events if isinstance(e, PaymentUpdated)]
        assert len(updated_events) == 1
        event = updated_events[0]
        assert event.old_data["status"] == PaymentStatus.PENDING
        assert event.new_data["status"] == PaymentStatus.OVERDUE

    def test_create_sets_audit_fields(self) -> None:
        """Verifica que create() preenche created_at e created_by."""
        actor_id = uuid7.create()
        payment = _make_payment()
        payment.create(user_id=actor_id)

        assert payment.created_at is not None
        assert payment.created_by == actor_id

    def test_mark_as_paid_sets_audit_fields(self) -> None:
        """Verifica que mark_as_paid() preenche updated_at e updated_by."""
        actor_id = uuid7.create()
        payment = _make_payment()
        payment.mark_as_paid(user_id=actor_id)

        assert payment.updated_at is not None
        assert payment.updated_by == actor_id

    def test_hash_is_based_on_id(self) -> None:
        """Verifica que o hash é baseado no ID."""
        payment = _make_payment()

        assert hash(payment) == hash(payment.id)


class TestPaymentCommands:
    """Testes para os comandos de Payment."""

    def test_create_payment_command(self) -> None:
        """Verifica a criação do comando CreatePayment."""
        due = datetime.now(UTC) + timedelta(days=30)
        command = CreatePayment(
            company=_TEST_COMPANY_ID,
            amount=199.99,
            due_date=due,
        )

        assert command.company == _TEST_COMPANY_ID
        assert command.amount == 199.99
        assert command.due_date == due

    def test_mark_payment_as_paid_command(self) -> None:
        """Verifica a criação do comando MarkPaymentAsPaid."""
        payment_id = uuid7.create()
        command = MarkPaymentAsPaid(payment_id=payment_id)

        assert command.payment_id == payment_id

    def test_mark_payment_as_overdue_command(self) -> None:
        """Verifica a criação do comando MarkPaymentAsOverdue."""
        payment_id = uuid7.create()
        command = MarkPaymentAsOverdue(payment_id=payment_id)

        assert command.payment_id == payment_id

    def test_check_and_deactivate_overdue_companies_command(self) -> None:
        """Verifica a criação do comando CheckAndDeactivateOverdueCompanies."""
        command = CheckAndDeactivateOverdueCompanies()

        assert command is not None


class TestPaymentEvents:
    """Testes para os eventos de Payment."""

    def test_payment_created_event(self) -> None:
        """Verifica a criação do evento PaymentCreated."""
        payment_id = uuid7.create()
        company_id = uuid7.create()
        event = PaymentCreated(
            id=payment_id,
            company=company_id,
            entity_type=EntityType.PAYMENT,
        )

        assert event.id == payment_id
        assert event.company == company_id

    def test_payment_updated_event(self) -> None:
        """Verifica a criação do evento PaymentUpdated."""
        payment_id = uuid7.create()
        company_id = uuid7.create()
        event = PaymentUpdated(
            id=payment_id,
            company=company_id,
            entity_type=EntityType.PAYMENT,
            old_data={"status": "pending"},
            new_data={"status": "paid"},
        )

        assert event.id == payment_id
        assert event.old_data["status"] == "pending"
        assert event.new_data["status"] == "paid"

    def test_company_payment_paid_event(self) -> None:
        """Verifica a criação do evento CompanyPaymentPaid."""
        company_id = uuid7.create()
        payment_id = uuid7.create()
        event = CompanyPaymentPaid(company=company_id, payment_id=payment_id)

        assert event.company == company_id
        assert event.payment_id == payment_id

    def test_company_payment_overdue_event(self) -> None:
        """Verifica a criação do evento CompanyPaymentOverdue."""
        company_id = uuid7.create()
        event = CompanyPaymentOverdue(company=company_id)

        assert event.company == company_id

    def test_company_and_users_deactivated_event(self) -> None:
        """Verifica a criação do evento CompanyAndUsersDeactivated."""
        company_id = uuid7.create()
        event = CompanyAndUsersDeactivated(company=company_id)

        assert event.company == company_id


class TestPaymentEntity:
    """Testes para a entidade de leitura Payment."""

    def test_payment_entity_creation(self) -> None:
        """Verifica a criação da entidade Payment com todos os campos."""
        payment_id = uuid7.create()
        company_id = uuid7.create()
        due = datetime.now(UTC) + timedelta(days=30)
        entity = PaymentEntity(
            id=payment_id,
            company=company_id,
            amount=150.0,
            due_date=due,
            status=PaymentStatus.PENDING,
        )

        assert entity.id == payment_id
        assert entity.company == company_id
        assert entity.amount == 150.0
        assert entity.status == PaymentStatus.PENDING
        assert entity.paid_at is None

    def test_payment_entity_with_paid_at(self) -> None:
        """Verifica a entidade Payment com paid_at preenchido."""
        payment_id = uuid7.create()
        paid_at = datetime.now(UTC)
        entity = PaymentEntity(
            id=payment_id,
            company=uuid7.create(),
            amount=150.0,
            due_date=datetime.now(UTC),
            status=PaymentStatus.PAID,
            paid_at=paid_at,
        )

        assert entity.paid_at == paid_at
        assert entity.status == PaymentStatus.PAID


class TestPaymentSchemas:
    """Testes para os schemas de Payment."""

    def test_create_payment_schema(self) -> None:
        """Verifica o schema de criação de pagamento."""
        due = datetime.now(UTC) + timedelta(days=30)
        schema = CreatePaymentSchema(
            company=_TEST_COMPANY_ID,
            amount=199.99,
            due_date=due,
        )

        assert schema.company == _TEST_COMPANY_ID
        assert schema.amount == 199.99
        assert schema.due_date == due

    def test_read_payment_schema(self) -> None:
        """Verifica o schema de leitura de pagamento."""
        payment_id = uuid7.create()
        due = datetime.now(UTC)
        schema = ReadPaymentSchema(
            id=payment_id,
            company=_TEST_COMPANY_ID,
            amount=199.99,
            due_date=due,
            status=PaymentStatus.PENDING,
        )

        assert schema.id == payment_id
        assert schema.status == PaymentStatus.PENDING
        assert schema.paid_at is None


class TestCompanyPaymentFields:
    """Testes para os campos de pagamento no agregado Company."""

    def _make_company(self, **overrides) -> Company:
        """Função auxiliar para criar um agregado Company."""
        defaults = dict(
            legal_name="Acme Corp",
            trade_name="Acme",
            responsible_name="John Doe",
            email="contact@acme.com",
            cpf="12345678901",
            cnpj="12345678000190",
            active=True,
        )
        defaults.update(overrides)
        return Company.create_aggregate(**defaults)

    def test_company_defaults_payment_up_to_date_true(self) -> None:
        """Verifica que payment_up_to_date é True por padrão."""
        company = self._make_company()

        assert company.payment_up_to_date is True

    def test_company_defaults_last_payment_date_none(self) -> None:
        """Verifica que last_payment_date é None por padrão."""
        company = self._make_company()

        assert company.last_payment_date is None

    def test_update_payment_status_to_paid(self) -> None:
        """Verifica que update_payment_status define payment_up_to_date=True e last_payment_date."""
        company = self._make_company()
        now = datetime.now(UTC)
        company.update_payment_status(payment_up_to_date=True, last_payment_date=now)

        assert company.payment_up_to_date is True
        assert company.last_payment_date == now

    def test_update_payment_status_to_overdue(self) -> None:
        """Verifica que update_payment_status define payment_up_to_date=False."""
        company = self._make_company()
        company.update_payment_status(payment_up_to_date=False)

        assert company.payment_up_to_date is False

    def test_update_payment_status_emits_event(self) -> None:
        """Verifica que update_payment_status emite o evento CompanyPaymentStatusUpdated."""
        company = self._make_company()
        company.update_payment_status(payment_up_to_date=False)

        events = [e for e in company.events if isinstance(e, CompanyPaymentStatusUpdated)]
        assert len(events) == 1
        assert events[0].id == company.id
