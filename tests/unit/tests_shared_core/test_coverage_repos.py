"""Testes de cobertura de branches para repositórios do shared_core.

Cobre branches não alcançados pelos testes de repositório específicos:
- CompanyViewRepo.get_all com scalars() falsy
- CompanyViewRepo.get_all com include_deleted=True
- PaymentDomainRepo._remove (soft delete)
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import uuid7


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


class TestCompanyViewRepoBranches:
    """Testes para branches de CompanyViewRepo.get_all não cobertas pelos testes de repositório."""

    async def test_get_all_include_deleted(self) -> None:
        """Verifica que get_all com include_deleted=True não filtra deletadas."""
        from shared_core.adapters.repository.view_repo.company import CompanyViewRepo

        session = _make_session()
        sr = MagicMock()
        sr.__iter__ = MagicMock(return_value=iter([]))
        r = MagicMock()
        r.scalars.return_value = sr
        session.execute.return_value = r

        repo = CompanyViewRepo(session=session)
        result = await repo.get_all(include_deleted=True)
        assert result == []

    async def test_get_all_empty_scalars_returns_empty(self) -> None:
        """Verifica que get_all retorna [] quando scalars() é falsy."""
        from shared_core.adapters.repository.view_repo.company import CompanyViewRepo

        session = _make_session()
        r = MagicMock()
        r.scalars.return_value = None
        session.execute.return_value = r

        repo = CompanyViewRepo(session=session)
        result = await repo.get_all()
        assert result == []


class TestPaymentDomainRepoRemove:
    """Testes para PaymentDomainRepo._remove (soft delete)."""

    async def test_remove_executes_soft_delete(self) -> None:
        """Verifica que _remove executa soft delete no banco de dados."""
        import shared_core.adapters.orm  # noqa: F401 — inicializa o mapeamento ORM
        from shared_core.adapters.repository.domain_repo.payment import PaymentDomainRepo
        from shared_core.domain.aggregate.payment import Payment

        session = _make_session()
        repo = PaymentDomainRepo(session=session)


        payment = Payment.create_aggregate(
            company=_COMPANY_ID,
            amount=100.0,
            due_date=datetime(2026, 3, 1, tzinfo=timezone.utc),
        )
        payment.mark_as_overdue(user_id=_USER_ID)

        await repo._remove(payment)
        session.execute.assert_awaited()
