"""Testes unitários para os handlers de Payment no shared_core.

Cobre create_payment, mark_payment_as_paid, mark_payment_as_overdue,
check_and_deactivate_overdue_companies e handlers de eventos.
"""

from datetime import date
from unittest.mock import AsyncMock, MagicMock

import uuid7

from shared_core.domain.commands.payment import (
    CheckAndDeactivateOverdueCompanies,
    CreatePayment,
    MarkPaymentAsOverdue,
    MarkPaymentAsPaid,
)
from shared_core.domain.events.payment import (
    CompanyAndUsersDeactivated,
    CompanyPaymentOverdue,
    CompanyPaymentPaid,
    PaymentCreated,
    PaymentUpdated,
)
from shared_core.services.handlers.payment import (
    check_and_deactivate_overdue_companies,
    company_and_users_deactivated,
    company_payment_overdue,
    company_payment_paid,
    create_payment,
    mark_payment_as_overdue,
    mark_payment_as_paid,
    payment_created,
    payment_updated,
)
from tests.unit.conftest import FakeUnitOfWork


_COMPANY_ID = uuid7.create()
_PAYMENT_ID = uuid7.create()
_USER_ID = uuid7.create()


class TestCreatePayment:
    """Testes para o handler create_payment."""

    async def test_create_payment(self) -> None:
        """Verifica que create_payment cria o pagamento e retorna o ID."""
        mock_repo = AsyncMock()
        mock_payment = MagicMock()
        mock_payment.id = _PAYMENT_ID
        mock_repo.create_aggregate = AsyncMock(return_value=mock_payment)

        uow = FakeUnitOfWork(domain_repo=mock_repo)

        command = CreatePayment(
            company=_COMPANY_ID,
            amount=100.00,
            due_date=date(2026, 3, 1),
        )

        result = await create_payment(command, uow)

        assert result == _PAYMENT_ID
        mock_repo.create_aggregate.assert_awaited_once()
        mock_payment.create.assert_called_once()
        mock_repo.add.assert_awaited_once()


class TestMarkPaymentAsPaid:
    """Testes para o handler mark_payment_as_paid."""

    async def test_mark_payment_as_paid(self) -> None:
        """Verifica que mark_payment_as_paid marca o pagamento como pago."""
        mock_payment_repo = AsyncMock()
        mock_payment = MagicMock()
        mock_payment.company = _COMPANY_ID
        mock_payment.id = _PAYMENT_ID
        mock_payment_repo.get_by_id = AsyncMock(return_value=mock_payment)

        mock_company_repo = AsyncMock()
        mock_company = MagicMock()
        mock_company.id = _COMPANY_ID
        mock_company_repo.get_by_id = AsyncMock(return_value=mock_company)

        call_count = 0

        class DualDomainUow(FakeUnitOfWork):
            """UoW fake que alterna entre repositórios de pagamento e empresa."""

            def __call__(self, domain=None):
                """Alterna o repositório de domínio conforme a chamada."""
                nonlocal call_count
                call_count += 1
                if call_count <= 1:
                    self._domain_repo = mock_payment_repo
                else:
                    self._domain_repo = mock_company_repo
                return self

        uow = DualDomainUow()

        command = MarkPaymentAsPaid(payment_id=_PAYMENT_ID)
        await mark_payment_as_paid(command, uow)

        mock_payment.mark_as_paid.assert_called_once()
        mock_company.update_payment_status.assert_called_once()
        mock_company.add_event.assert_called_once()


class TestMarkPaymentAsOverdue:
    """Testes para o handler mark_payment_as_overdue."""

    async def test_mark_payment_as_overdue(self) -> None:
        """Verifica que mark_payment_as_overdue marca o pagamento como atrasado."""
        mock_payment_repo = AsyncMock()
        mock_payment = MagicMock()
        mock_payment.company = _COMPANY_ID
        mock_payment_repo.get_by_id = AsyncMock(return_value=mock_payment)

        mock_company_repo = AsyncMock()
        mock_company = MagicMock()
        mock_company.id = _COMPANY_ID
        mock_company_repo.get_by_id = AsyncMock(return_value=mock_company)

        call_count = 0

        class DualDomainUow(FakeUnitOfWork):
            """UoW fake que alterna entre repositórios de pagamento e empresa."""

            def __call__(self, domain=None):
                """Alterna o repositório de domínio conforme a chamada."""
                nonlocal call_count
                call_count += 1
                if call_count <= 1:
                    self._domain_repo = mock_payment_repo
                else:
                    self._domain_repo = mock_company_repo
                return self

        uow = DualDomainUow()

        command = MarkPaymentAsOverdue(payment_id=_PAYMENT_ID)
        await mark_payment_as_overdue(command, uow)

        mock_payment.mark_as_overdue.assert_called_once()
        mock_company.update_payment_status.assert_called_once()


class TestCheckAndDeactivateOverdueCompanies:
    """Testes para o handler check_and_deactivate_overdue_companies."""

    async def test_no_overdue_companies(self) -> None:
        """Verifica que retorna lista vazia quando não há empresas em atraso."""
        mock_repo = AsyncMock()
        mock_repo.get_overdue_companies = AsyncMock(return_value=[])

        uow = FakeUnitOfWork(domain_repo=mock_repo)
        command = CheckAndDeactivateOverdueCompanies()

        result = await check_and_deactivate_overdue_companies(command, uow)
        assert result == []

    async def test_deactivate_active_company_with_users(self) -> None:
        """Verifica que empresa ativa com usuários é desativada corretamente."""
        mock_payment_repo = AsyncMock()
        mock_payment_repo.get_overdue_companies = AsyncMock(return_value=[_COMPANY_ID])

        mock_company = MagicMock()
        mock_company.active = True
        mock_company.id = _COMPANY_ID
        mock_company_repo = AsyncMock()
        mock_company_repo.get_by_id = AsyncMock(return_value=mock_company)

        mock_user = MagicMock()
        mock_user_repo = AsyncMock()
        mock_user_repo.get_all_by_company = AsyncMock(return_value=[mock_user])

        call_count = 0

        class MultiDomainUow(FakeUnitOfWork):
            """UoW fake com múltiplos repositórios de domínio."""

            def __call__(self, domain=None):
                """Alterna entre repositórios conforme a sequência de chamadas."""
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    self._domain_repo = mock_payment_repo
                elif call_count == 2:
                    self._domain_repo = mock_company_repo
                else:
                    self._domain_repo = mock_user_repo
                return self

        uow = MultiDomainUow()
        command = CheckAndDeactivateOverdueCompanies()

        result = await check_and_deactivate_overdue_companies(command, uow)

        assert _COMPANY_ID in result
        mock_company.deactivate.assert_called_once()
        mock_user.deactivate.assert_called_once()

    async def test_skip_inactive_company(self) -> None:
        """Verifica que empresa já inativa é ignorada."""
        mock_payment_repo = AsyncMock()
        mock_payment_repo.get_overdue_companies = AsyncMock(return_value=[_COMPANY_ID])

        mock_company = MagicMock()
        mock_company.active = False
        mock_company_repo = AsyncMock()
        mock_company_repo.get_by_id = AsyncMock(return_value=mock_company)

        call_count = 0

        class MultiDomainUow(FakeUnitOfWork):
            """UoW fake com dois repositórios de domínio."""

            def __call__(self, domain=None):
                """Alterna entre repositórios de pagamento e empresa."""
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    self._domain_repo = mock_payment_repo
                else:
                    self._domain_repo = mock_company_repo
                return self

        uow = MultiDomainUow()
        command = CheckAndDeactivateOverdueCompanies()

        result = await check_and_deactivate_overdue_companies(command, uow)
        assert result == []

    async def test_skip_company_not_found(self) -> None:
        """Verifica que empresa não encontrada é ignorada sem erro."""
        mock_payment_repo = AsyncMock()
        mock_payment_repo.get_overdue_companies = AsyncMock(return_value=[_COMPANY_ID])

        mock_company_repo = AsyncMock()
        mock_company_repo.get_by_id = AsyncMock(side_effect=Exception("Not found"))

        mock_user_repo = AsyncMock()
        mock_user_repo.get_all_by_company = AsyncMock(return_value=[])

        call_count = 0

        class MultiDomainUow(FakeUnitOfWork):
            """UoW fake com múltiplos repositórios de domínio."""

            def __call__(self, domain=None):
                """Alterna entre repositórios conforme a sequência de chamadas."""
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    self._domain_repo = mock_payment_repo
                elif call_count == 2:
                    self._domain_repo = mock_company_repo
                else:
                    self._domain_repo = mock_user_repo
                return self

        uow = MultiDomainUow()
        command = CheckAndDeactivateOverdueCompanies()

        result = await check_and_deactivate_overdue_companies(command, uow)
        assert result == []

    async def test_deactivate_company_no_users(self) -> None:
        """Verifica que empresa ativa sem usuários é desativada corretamente."""
        mock_payment_repo = AsyncMock()
        mock_payment_repo.get_overdue_companies = AsyncMock(return_value=[_COMPANY_ID])

        mock_company = MagicMock()
        mock_company.active = True
        mock_company.id = _COMPANY_ID
        mock_company_repo = AsyncMock()
        mock_company_repo.get_by_id = AsyncMock(return_value=mock_company)

        mock_user_repo = AsyncMock()
        mock_user_repo.get_all_by_company = AsyncMock(return_value=[])

        call_count = 0

        class MultiDomainUow(FakeUnitOfWork):
            """UoW fake com múltiplos repositórios de domínio."""

            def __call__(self, domain=None):
                """Alterna entre repositórios conforme a sequência de chamadas."""
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    self._domain_repo = mock_payment_repo
                elif call_count == 2:
                    self._domain_repo = mock_company_repo
                else:
                    self._domain_repo = mock_user_repo
                return self

        uow = MultiDomainUow()
        command = CheckAndDeactivateOverdueCompanies()

        result = await check_and_deactivate_overdue_companies(command, uow)
        assert _COMPANY_ID in result


class TestPaymentEventHandlers:
    """Testes para os handlers de eventos de Payment."""

    async def test_payment_created(self) -> None:
        """Verifica que payment_created é executado sem erros."""
        event = PaymentCreated(id=_PAYMENT_ID, company=_COMPANY_ID)
        uow = FakeUnitOfWork()
        await payment_created(event, uow)

    async def test_payment_updated(self) -> None:
        """Verifica que payment_updated é executado sem erros."""
        event = PaymentUpdated(id=_PAYMENT_ID, company=_COMPANY_ID)
        uow = FakeUnitOfWork()
        await payment_updated(event, uow)

    async def test_company_payment_paid(self) -> None:
        """Verifica que company_payment_paid é executado sem erros."""
        event = CompanyPaymentPaid(company=_COMPANY_ID, payment_id=_PAYMENT_ID)
        uow = FakeUnitOfWork()
        await company_payment_paid(event, uow)

    async def test_company_payment_overdue(self) -> None:
        """Verifica que company_payment_overdue é executado sem erros."""
        event = CompanyPaymentOverdue(company=_COMPANY_ID)
        uow = FakeUnitOfWork()
        await company_payment_overdue(event, uow)

    async def test_company_and_users_deactivated(self) -> None:
        """Verifica que company_and_users_deactivated é executado sem erros."""
        event = CompanyAndUsersDeactivated(company=_COMPANY_ID)
        uow = FakeUnitOfWork()
        await company_and_users_deactivated(event, uow)
