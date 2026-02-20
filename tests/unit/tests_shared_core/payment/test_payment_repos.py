"""Testes unitários para os repositórios concretos de Payment (domain + view)."""

from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest
import uuid7

from shared_core.domain.aggregate.payment import Payment
from shared_core.domain.excecoes import PaymentNotFound


_COMPANY_ID = uuid7.create()
_USER_ID = uuid7.create()
_PAYMENT_ID = uuid7.create()


def _make_session():
    """Cria uma sessão SQLAlchemy mockada com async context manager."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    return session


def _make_mock_payment_row():
    """Cria uma linha de resultado mockada representando um Payment."""
    p = MagicMock()
    p.id = _PAYMENT_ID
    p.company = _COMPANY_ID
    p.amount = 100.0
    p.due_date = date(2026, 3, 1)
    p.paid = False
    p.paid_at = None
    p.overdue = False
    p.created_at = None
    p.created_by = None
    p.updated_at = None
    p.updated_by = None
    p.deleted_at = None
    p.deleted_by = None
    return p


# ─── PaymentDomainRepo ───


class TestPaymentDomainRepoConcrete:
    """Testes para o repositório de domínio concreto de Payment."""

    async def test_create_aggregate(self) -> None:
        """Verifica que create_aggregate cria um pagamento com sucesso."""
        from shared_core.adapters.repository.domain_repo.payment import (
            PaymentDomainRepo,
        )

        session = _make_session()
        repo = PaymentDomainRepo(session=session)

        payment = await repo.create_aggregate(
            company=_COMPANY_ID,
            amount=100.0,
            due_date=date(2026, 3, 1),
        )
        assert payment.company == _COMPANY_ID
        assert payment.amount == 100.0

    async def test_get_by_id_found(self) -> None:
        """Verifica que get_by_id retorna o pagamento quando encontrado."""
        from shared_core.adapters.repository.domain_repo.payment import (
            PaymentDomainRepo,
        )

        session = _make_session()
        mock_p = _make_mock_payment_row()
        r = MagicMock()
        r.scalar_one_or_none.return_value = mock_p
        session.execute.return_value = r

        repo = PaymentDomainRepo(session=session)
        payment = await repo.get_by_id(_PAYMENT_ID)
        assert payment.id == _PAYMENT_ID

    async def test_get_by_id_not_found(self) -> None:
        """Verifica que get_by_id levanta PaymentNotFound quando não encontrado."""
        from shared_core.adapters.repository.domain_repo.payment import (
            PaymentDomainRepo,
        )

        session = _make_session()
        r = MagicMock()
        r.scalar_one_or_none.return_value = None
        session.execute.return_value = r

        repo = PaymentDomainRepo(session=session)
        with pytest.raises(PaymentNotFound):
            await repo.get_by_id(_PAYMENT_ID)

    async def test_get_all_by_company(self) -> None:
        """Verifica que get_all_by_company retorna pagamentos da empresa."""
        from shared_core.adapters.repository.domain_repo.payment import (
            PaymentDomainRepo,
        )

        session = _make_session()
        mock_p = _make_mock_payment_row()
        sr = MagicMock()
        sr.all.return_value = [mock_p]
        r = MagicMock()
        r.scalars.return_value = sr
        session.execute.return_value = r

        repo = PaymentDomainRepo(session=session)
        result = await repo.get_all_by_company(_COMPANY_ID)
        assert len(result) == 1

    async def test_get_overdue_companies(self) -> None:
        """Verifica que get_overdue_companies retorna empresas com pagamentos atrasados."""
        from shared_core.adapters.repository.domain_repo.payment import (
            PaymentDomainRepo,
        )

        session = _make_session()
        mock_row = MagicMock()
        mock_row.company = _COMPANY_ID
        sr = MagicMock()
        sr.all.return_value = [mock_row]
        r = MagicMock()
        r.scalars.return_value = sr
        session.execute.return_value = r

        repo = PaymentDomainRepo(session=session)
        result = await repo.get_overdue_companies()
        assert _COMPANY_ID in result

    async def test_add(self) -> None:
        """Verifica que _add executa operação na sessão."""
        from shared_core.adapters.repository.domain_repo.payment import (
            PaymentDomainRepo,
        )

        session = _make_session()
        repo = PaymentDomainRepo(session=session)

        payment = Payment.create_aggregate(
            company=_COMPANY_ID, amount=50.0, due_date=date(2026, 3, 1)
        )
        payment.create(_USER_ID)
        await repo._add(payment)
        session.execute.assert_awaited()


# ─── PaymentViewRepo ───


class TestPaymentViewRepo:
    """Testes para o repositório de view concreto de Payment."""

    async def test_get_all_by_company(self) -> None:
        """Verifica que get_all_by_company retorna pagamentos da empresa."""
        from shared_core.adapters.repository.view_repo.payment import PaymentViewRepo

        session = _make_session()
        mock_p = _make_mock_payment_row()
        sr = MagicMock()
        sr.all.return_value = [mock_p]
        r = MagicMock()
        r.scalars.return_value = sr
        session.execute.return_value = r

        repo = PaymentViewRepo(session=session)
        result = await repo.get_all_by_company(_COMPANY_ID)
        assert len(result) == 1

    async def test_get_by_id_found(self) -> None:
        """Verifica que get_by_id retorna o pagamento quando encontrado."""
        from shared_core.adapters.repository.view_repo.payment import PaymentViewRepo

        session = _make_session()
        mock_p = _make_mock_payment_row()
        r = MagicMock()
        r.scalar_one_or_none.return_value = mock_p
        session.execute.return_value = r

        repo = PaymentViewRepo(session=session)
        result = await repo.get_by_id(_PAYMENT_ID)
        assert result is not None

    async def test_get_by_id_not_found(self) -> None:
        """Verifica que get_by_id retorna None quando não encontrado."""
        from shared_core.adapters.repository.view_repo.payment import PaymentViewRepo

        session = _make_session()
        r = MagicMock()
        r.scalar_one_or_none.return_value = None
        session.execute.return_value = r

        repo = PaymentViewRepo(session=session)
        result = await repo.get_by_id(_PAYMENT_ID)
        assert result is None
