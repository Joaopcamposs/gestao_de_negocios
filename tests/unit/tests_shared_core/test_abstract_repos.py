"""Testes unitários para os repositórios abstratos de domínio do shared_core."""

from unittest.mock import AsyncMock, MagicMock

import uuid7

from shared_core.domain.aggregate.audit_log import AuditLog
from shared_core.domain.aggregate.company import Company
from shared_core.domain.value_objects.enums import AuditOperation


_COMPANY_ID = uuid7.create()
_USER_ID = uuid7.create()


def _make_mock_session():
    """Cria uma sessão SQLAlchemy mockada com async context manager."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    return session


# ─── Abstract Company Repo ───


class TestAbstractCompanyDomainRepo:
    """Testes para o repositório abstrato de Company."""

    async def test_add_tracks_seen(self) -> None:
        """Verifica que add() rastreia o agregado no conjunto seen."""
        from shared_core.adapters.repository.domain_repo.company import (
            AbstractCompanyDomainRepo,
        )

        class ConcreteRepo(AbstractCompanyDomainRepo):
            async def _add(self, company):
                pass

            async def _remove(self, company):
                pass

            async def get_by_legal_name(self, legal_name):
                pass

        repo = ConcreteRepo()
        company = MagicMock(spec=Company)
        company.__hash__ = MagicMock(return_value=1)

        await repo.add(company)
        assert company in repo.seen

    async def test_remove_tracks_seen(self) -> None:
        """Verifica que remove() rastreia o agregado no conjunto seen."""
        from shared_core.adapters.repository.domain_repo.company import (
            AbstractCompanyDomainRepo,
        )

        class ConcreteRepo(AbstractCompanyDomainRepo):
            async def _add(self, company):
                pass

            async def _remove(self, company):
                pass

            async def get_by_legal_name(self, legal_name):
                pass

        repo = ConcreteRepo()
        company = MagicMock(spec=Company)
        company.__hash__ = MagicMock(return_value=1)

        await repo.remove(company)
        assert company in repo.seen


# ─── Abstract AuditLog Repo ───


class TestAbstractAuditLogDomainRepo:
    """Testes para o repositório abstrato de AuditLog."""

    async def test_add_tracks_seen(self) -> None:
        """Verifica que add() rastreia o auditlog no conjunto seen."""
        from shared_core.adapters.repository.domain_repo.audit_log import (
            AbstractAuditLogDomainRepo,
        )

        class ConcreteRepo(AbstractAuditLogDomainRepo):
            async def _add(self, audit_log):
                pass

        repo = ConcreteRepo()
        audit_log = AuditLog.create_aggregate(
            entity_type="Test",
            entity_id=uuid7.create(),
            operation="CREATE",
        )

        await repo.add(audit_log)
        assert audit_log in repo.seen


class TestAuditLogDomainRepo:
    """Testes para o repositório concreto de AuditLog."""

    async def test_create_from_event(self) -> None:
        """Verifica que create_from_event constrói um AuditLog correto a partir de um evento."""
        from messagebus.entities import AuditableEvent
        from messagebus.messagebus import Event

        from shared_core.adapters.repository.domain_repo.audit_log import (
            AuditLogDomainRepo,
        )

        session = _make_mock_session()
        repo = AuditLogDomainRepo(session=session)

        class FakeEvent(Event, AuditableEvent):
            entity_type: str = "TestEntity"
            old_data: dict | None = {"field": "old"}
            new_data: dict | None = {"field": "new"}

        event = FakeEvent()
        entity_id = uuid7.create()

        result = await repo.create_from_event(
            event=event,
            entity_id=entity_id,
            operation=AuditOperation.CREATE,
            user_id=_USER_ID,
        )

        assert result.entity_type == "TestEntity"
        assert result.entity_id == entity_id
        assert result.user_id == _USER_ID

    async def test_add_executes_insert(self) -> None:
        """Verifica que _add() executa INSERT na sessão."""
        from shared_core.adapters.repository.domain_repo.audit_log import (
            AuditLogDomainRepo,
        )

        session = _make_mock_session()
        repo = AuditLogDomainRepo(session=session)

        audit_log = AuditLog.create_aggregate(
            entity_type="Test",
            entity_id=uuid7.create(),
            operation="CREATE",
        )

        await repo._add(audit_log)
        session.execute.assert_awaited_once()


# ─── Abstract User Repo ───


class TestAbstractUserDomainRepo:
    """Testes para o repositório abstrato de User."""

    async def test_add_and_remove_track_seen(self) -> None:
        """Verifica que add() e remove() rastreiam agregados no conjunto seen."""
        from shared_core.adapters.repository.domain_repo.user import (
            AbstractUserDomainRepo,
        )

        class ConcreteRepo(AbstractUserDomainRepo):
            async def _add(self, user):
                pass

            async def _remove(self, user):
                pass

            async def get_by_email(self, email):
                pass

        repo = ConcreteRepo()
        user = MagicMock()
        user.__hash__ = MagicMock(return_value=1)

        await repo.add(user)
        assert user in repo.seen

        user2 = MagicMock()
        user2.__hash__ = MagicMock(return_value=2)
        await repo.remove(user2)
        assert user2 in repo.seen


# ─── Abstract CreditCard Repo ───


class TestAbstractCreditCardDomainRepo:
    """Testes para o repositório abstrato de CreditCard."""

    async def test_add_and_remove_track_seen(self) -> None:
        """Verifica que add() e remove() rastreiam agregados no conjunto seen."""
        from shared_core.adapters.repository.domain_repo.credit_card import (
            AbstractCreditCardDomainRepo,
        )

        class ConcreteRepo(AbstractCreditCardDomainRepo):
            async def _add(self, card):
                pass

            async def _remove(self, card):
                pass

            async def get_by_id(self, card_id):
                pass

        repo = ConcreteRepo()
        card = MagicMock()
        card.__hash__ = MagicMock(return_value=1)

        await repo.add(card)
        assert card in repo.seen

        card2 = MagicMock()
        card2.__hash__ = MagicMock(return_value=2)
        await repo.remove(card2)
        assert card2 in repo.seen


# ─── Abstract Payment Repo ───


class TestAbstractPaymentDomainRepo:
    """Testes para o repositório abstrato de Payment."""

    async def test_add_tracks_seen(self) -> None:
        """Verifica que add() rastreia o agregado no conjunto seen."""
        from shared_core.adapters.repository.domain_repo.payment import (
            AbstractPaymentDomainRepo,
        )

        class ConcreteRepo(AbstractPaymentDomainRepo):
            async def _add(self, payment):
                pass

            async def _remove(self, payment):
                pass

            async def get_by_id(self, payment_id):
                pass

        repo = ConcreteRepo()
        payment = MagicMock()
        payment.__hash__ = MagicMock(return_value=1)

        await repo.add(payment)
        assert payment in repo.seen

    async def test_remove_tracks_seen(self) -> None:
        """Verifica que remove() rastreia o agregado no conjunto seen."""
        from shared_core.adapters.repository.domain_repo.payment import (
            AbstractPaymentDomainRepo,
        )

        class ConcreteRepo(AbstractPaymentDomainRepo):
            async def _add(self, payment):
                pass

            async def _remove(self, payment):
                pass

            async def get_by_id(self, payment_id):
                pass

        repo = ConcreteRepo()
        payment = MagicMock()
        payment.__hash__ = MagicMock(return_value=2)

        await repo.remove(payment)
        assert payment in repo.seen


# ─── NotImplementedError coverage for abstract methods ───


class TestAbstractNotImplemented:
    """Testes para garantir cobertura dos raise NotImplementedError em métodos abstratos."""

    async def test_company_abstract_add_raises(self) -> None:
        """Cobre o raise NotImplementedError do _add abstrato de Company."""
        from shared_core.adapters.repository.domain_repo.company import (
            AbstractCompanyDomainRepo,
        )

        import pytest

        class CallSuperAdd(AbstractCompanyDomainRepo):
            async def _add(self, company):
                await super()._add(company)

            async def _remove(self, company):
                pass

            async def get_by_legal_name(self, legal_name):
                pass

        repo = CallSuperAdd()
        with pytest.raises(NotImplementedError):
            await repo._add(MagicMock())

    async def test_company_abstract_remove_raises(self) -> None:
        """Cobre o raise NotImplementedError do _remove abstrato de Company."""
        from shared_core.adapters.repository.domain_repo.company import (
            AbstractCompanyDomainRepo,
        )

        import pytest

        class CallSuperRemove(AbstractCompanyDomainRepo):
            async def _add(self, company):
                pass

            async def _remove(self, company):
                await super()._remove(company)

            async def get_by_legal_name(self, legal_name):
                pass

        repo = CallSuperRemove()
        with pytest.raises(NotImplementedError):
            await repo._remove(MagicMock())

    async def test_company_abstract_get_by_legal_name_raises(self) -> None:
        """Cobre o raise NotImplementedError do get_by_legal_name abstrato de Company."""
        from shared_core.adapters.repository.domain_repo.company import (
            AbstractCompanyDomainRepo,
        )

        import pytest

        class CallSuperGet(AbstractCompanyDomainRepo):
            async def _add(self, company):
                pass

            async def _remove(self, company):
                pass

            async def get_by_legal_name(self, legal_name):
                return await super().get_by_legal_name(legal_name)

        repo = CallSuperGet()
        with pytest.raises(NotImplementedError):
            await repo.get_by_legal_name("Test")

    async def test_credit_card_abstract_add_raises(self) -> None:
        """Cobre o raise NotImplementedError do _add abstrato de CreditCard."""
        from shared_core.adapters.repository.domain_repo.credit_card import (
            AbstractCreditCardDomainRepo,
        )

        import pytest

        class CallSuperAdd(AbstractCreditCardDomainRepo):
            async def _add(self, card):
                await super()._add(card)

            async def _remove(self, card):
                pass

            async def get_by_id(self, card_id):
                pass

        repo = CallSuperAdd()
        with pytest.raises(NotImplementedError):
            await repo._add(MagicMock())

    async def test_credit_card_abstract_remove_raises(self) -> None:
        """Cobre o raise NotImplementedError do _remove abstrato de CreditCard."""
        from shared_core.adapters.repository.domain_repo.credit_card import (
            AbstractCreditCardDomainRepo,
        )

        import pytest

        class CallSuperRemove(AbstractCreditCardDomainRepo):
            async def _add(self, card):
                pass

            async def _remove(self, card):
                await super()._remove(card)

            async def get_by_id(self, card_id):
                pass

        repo = CallSuperRemove()
        with pytest.raises(NotImplementedError):
            await repo._remove(MagicMock())

    async def test_payment_abstract_add_raises(self) -> None:
        """Cobre o raise NotImplementedError do _add abstrato de Payment."""
        from shared_core.adapters.repository.domain_repo.payment import (
            AbstractPaymentDomainRepo,
        )

        import pytest

        class CallSuperAdd(AbstractPaymentDomainRepo):
            async def _add(self, payment):
                await super()._add(payment)

            async def _remove(self, payment):
                pass

            async def get_by_id(self, payment_id):
                pass

        repo = CallSuperAdd()
        with pytest.raises(NotImplementedError):
            await repo._add(MagicMock())

    async def test_payment_abstract_remove_raises(self) -> None:
        """Cobre o raise NotImplementedError do _remove abstrato de Payment."""
        from shared_core.adapters.repository.domain_repo.payment import (
            AbstractPaymentDomainRepo,
        )

        import pytest

        class CallSuperRemove(AbstractPaymentDomainRepo):
            async def _add(self, payment):
                pass

            async def _remove(self, payment):
                await super()._remove(payment)

            async def get_by_id(self, payment_id):
                pass

        repo = CallSuperRemove()
        with pytest.raises(NotImplementedError):
            await repo._remove(MagicMock())

    async def test_user_abstract_add_raises(self) -> None:
        """Cobre o raise NotImplementedError do _add abstrato de User."""
        from shared_core.adapters.repository.domain_repo.user import (
            AbstractUserDomainRepo,
        )

        import pytest

        class CallSuperAdd(AbstractUserDomainRepo):
            async def _add(self, user):
                await super()._add(user)

            async def _remove(self, user):
                pass

            async def get_by_email(self, email):
                pass

        repo = CallSuperAdd()
        with pytest.raises(NotImplementedError):
            await repo._add(MagicMock())

    async def test_user_abstract_remove_raises(self) -> None:
        """Cobre o raise NotImplementedError do _remove abstrato de User."""
        from shared_core.adapters.repository.domain_repo.user import (
            AbstractUserDomainRepo,
        )

        import pytest

        class CallSuperRemove(AbstractUserDomainRepo):
            async def _add(self, user):
                pass

            async def _remove(self, user):
                await super()._remove(user)

            async def get_by_email(self, email):
                pass

        repo = CallSuperRemove()
        with pytest.raises(NotImplementedError):
            await repo._remove(MagicMock())

    async def test_user_abstract_get_by_email_raises(self) -> None:
        """Cobre o raise NotImplementedError do get_by_email abstrato de User."""
        from shared_core.adapters.repository.domain_repo.user import (
            AbstractUserDomainRepo,
        )

        import pytest

        class CallSuperGet(AbstractUserDomainRepo):
            async def _add(self, user):
                pass

            async def _remove(self, user):
                pass

            async def get_by_email(self, email):
                return await super().get_by_email(email)

        repo = CallSuperGet()
        with pytest.raises(NotImplementedError):
            await repo.get_by_email("test@test.com")

    async def test_audit_log_abstract_add_raises(self) -> None:
        """Cobre o raise NotImplementedError do _add abstrato de AuditLog."""
        from shared_core.adapters.repository.domain_repo.audit_log import (
            AbstractAuditLogDomainRepo,
        )

        import pytest

        class CallSuperAdd(AbstractAuditLogDomainRepo):
            async def _add(self, audit_log):
                await super()._add(audit_log)

        repo = CallSuperAdd()
        with pytest.raises(NotImplementedError):
            await repo._add(MagicMock())
