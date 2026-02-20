"""Testes de integração para o fluxo de Payment."""

from datetime import UTC, datetime, timedelta
from uuid import UUID


from shared_core.bootstrap import bootstrap
from shared_core.domain.commands.company import CreateCompany
from shared_core.domain.commands.payment import (
    CheckAndDeactivateOverdueCompanies,
    CreatePayment,
    MarkPaymentAsOverdue,
    MarkPaymentAsPaid,
)
from shared_core.domain.value_objects.enums import PaymentStatus


async def _create_company(legal_name: str, email: str, cpf: str = "12345678901") -> UUID:
    """Helper para criar empresa."""
    bus = bootstrap(schema="public", raise_event_errors=True)
    return await bus.handle(
        CreateCompany(
            legal_name=legal_name,
            responsible_name="Test User",
            active=True,
            cpf=cpf,
            email=email,
            password="secret123",
            should_create_user=True,
        )
    )


async def _create_payment(
    company_id: UUID,
    amount: float = 150.0,
    days_until_due: int = 30,
) -> UUID:
    """Helper para criar pagamento."""
    bus = bootstrap(schema="public", raise_event_errors=True)
    return await bus.handle(
        CreatePayment(
            company=company_id,
            amount=amount,
            due_date=datetime.now(UTC) + timedelta(days=days_until_due),
        )
    )


class TestCreatePayment:
    """Testes de integração para criação de pagamentos."""

    async def test_create_payment_returns_uuid(self, engine) -> None:
        """Verifica que criar pagamento retorna UUID válido."""
        company_id = await _create_company("Pay Create Corp", "paycreate@test.com")
        payment_id = await _create_payment(company_id)

        assert isinstance(payment_id, UUID)

    async def test_create_payment_has_pending_status(self, engine) -> None:
        """Verifica que pagamento criado tem status PENDING."""
        from shared_core.adapters.repository.domain_repo.payment import PaymentDomainRepo
        from shared_core.domains import Domain

        company_id = await _create_company("Pay Status Corp", "paystatus@test.com")
        payment_id = await _create_payment(company_id)

        bus = bootstrap(schema="public", raise_event_errors=True)
        async with bus.uow(Domain.payment) as uow:
            repo: PaymentDomainRepo = uow.domain_repo
            payment = await repo.get_by_id(payment_id=payment_id)

        assert payment.status == PaymentStatus.PENDING
        assert payment.paid_at is None

    async def test_create_multiple_payments_for_same_company(self, engine) -> None:
        """Verifica que uma empresa pode ter múltiplos pagamentos."""
        company_id = await _create_company("Pay Multi Corp", "paymulti@test.com")

        payment_id_1 = await _create_payment(company_id, amount=100.0)
        payment_id_2 = await _create_payment(company_id, amount=200.0)

        assert payment_id_1 != payment_id_2


class TestMarkPaymentAsPaid:
    """Testes de integração para marcar pagamento como pago."""

    async def test_mark_payment_as_paid_changes_status(self, engine) -> None:
        """Verifica que marcar como pago altera status para PAID."""
        from shared_core.adapters.repository.domain_repo.payment import PaymentDomainRepo
        from shared_core.domains import Domain

        company_id = await _create_company("Pay Paid Corp", "paypaid@test.com")
        payment_id = await _create_payment(company_id)

        bus = bootstrap(schema="public", raise_event_errors=True)
        await bus.handle(MarkPaymentAsPaid(payment_id=payment_id))

        async with bus.uow(Domain.payment) as uow:
            repo: PaymentDomainRepo = uow.domain_repo
            payment = await repo.get_by_id(payment_id=payment_id)

        assert payment.status == PaymentStatus.PAID
        assert payment.paid_at is not None

    async def test_mark_payment_as_paid_updates_company_payment_status(
        self, engine
    ) -> None:
        """Verifica que marcar pagamento como pago atualiza o status de pagamento da empresa."""
        from shared_core.adapters.repository.domain_repo.company import CompanyDomainRepo
        from shared_core.domains import Domain

        company_id = await _create_company("Pay Co Paid Corp", "paycopaid@test.com")
        payment_id = await _create_payment(company_id)

        bus = bootstrap(schema="public", raise_event_errors=True)
        await bus.handle(MarkPaymentAsPaid(payment_id=payment_id))

        async with bus.uow(Domain.company) as uow:
            repo: CompanyDomainRepo = uow.domain_repo
            company = await repo.get_by_id(company_id=company_id)

        assert company.payment_up_to_date is True
        assert company.last_payment_date is not None


class TestMarkPaymentAsOverdue:
    """Testes de integração para marcar pagamento como em atraso."""

    async def test_mark_payment_as_overdue_changes_status(self, engine) -> None:
        """Verifica que marcar como em atraso altera status para OVERDUE."""
        from shared_core.adapters.repository.domain_repo.payment import PaymentDomainRepo
        from shared_core.domains import Domain

        company_id = await _create_company("Pay Overdue Corp", "payoverdue@test.com")
        payment_id = await _create_payment(company_id)

        bus = bootstrap(schema="public", raise_event_errors=True)
        await bus.handle(MarkPaymentAsOverdue(payment_id=payment_id))

        async with bus.uow(Domain.payment) as uow:
            repo: PaymentDomainRepo = uow.domain_repo
            payment = await repo.get_by_id(payment_id=payment_id)

        assert payment.status == PaymentStatus.OVERDUE

    async def test_mark_payment_as_overdue_updates_company_flag(self, engine) -> None:
        """Verifica que marcar pagamento como em atraso atualiza o flag da empresa."""
        from shared_core.adapters.repository.domain_repo.company import CompanyDomainRepo
        from shared_core.domains import Domain

        company_id = await _create_company("Pay Co Overdue Corp", "paycooverdue@test.com")
        payment_id = await _create_payment(company_id)

        bus = bootstrap(schema="public", raise_event_errors=True)
        await bus.handle(MarkPaymentAsOverdue(payment_id=payment_id))

        async with bus.uow(Domain.company) as uow:
            repo: CompanyDomainRepo = uow.domain_repo
            company = await repo.get_by_id(company_id=company_id)

        assert company.payment_up_to_date is False


class TestCheckAndDeactivateOverdueCompanies:
    """Testes de integração para inativação automática de empresas com atraso > 30 dias."""

    async def test_company_with_no_overdue_is_not_deactivated(self, engine) -> None:
        """Verifica que empresa sem atraso não é inativada."""
        from shared_core.adapters.repository.domain_repo.company import CompanyDomainRepo
        from shared_core.domains import Domain

        company_id = await _create_company("No Deact Corp", "nodeact@test.com")

        bus = bootstrap(schema="public", raise_event_errors=True)
        deactivated = await bus.handle(CheckAndDeactivateOverdueCompanies())

        async with bus.uow(Domain.company) as uow:
            repo: CompanyDomainRepo = uow.domain_repo
            company = await repo.get_by_id(company_id=company_id)

        assert company_id not in deactivated
        assert company.active is True

    async def test_check_and_deactivate_returns_list(self, engine) -> None:
        """Verifica que CheckAndDeactivateOverdueCompanies retorna uma lista."""
        bus = bootstrap(schema="public", raise_event_errors=True)
        result = await bus.handle(CheckAndDeactivateOverdueCompanies())

        assert isinstance(result, list)


class TestPaymentAlertOnLogin:
    """Testes de integração para alerta de pagamento em atraso no login."""

    async def test_login_with_payment_up_to_date_has_no_alert(self, engine) -> None:
        """Verifica que login sem atraso não gera alerta no token."""
        from shared_core.domain.commands.security import AuthenticateUser

        await _create_company("Alert OK Corp", "alertok@test.com")

        bus = bootstrap(schema="public", raise_event_errors=True)
        token = await bus.handle(
            AuthenticateUser(email="alertok@test.com", password="secret123")
        )

        assert token is not None
        assert token.payment_alert is None

    async def test_login_with_overdue_payment_has_alert(self, engine) -> None:
        """Verifica que login com pagamento em atraso gera alerta no token."""
        from shared_core.domain.commands.security import AuthenticateUser

        company_id = await _create_company("Alert Overdue Corp", "alertoverdue@test.com")
        payment_id = await _create_payment(company_id)

        bus = bootstrap(schema="public", raise_event_errors=True)
        await bus.handle(MarkPaymentAsOverdue(payment_id=payment_id))

        token = await bus.handle(
            AuthenticateUser(email="alertoverdue@test.com", password="secret123")
        )

        assert token is not None
        assert token.payment_alert is not None
        assert len(token.payment_alert) > 0
