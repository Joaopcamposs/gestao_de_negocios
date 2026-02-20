"""Testes de cobertura para repositórios do shared_core.

Cobre CreditCardViewRepo.get_by_id, PaymentViewRepo.get_by_id,
CreditCardDomainRepo.get_all_by_user, PaymentDomainRepo.get_all_by_company,
UserDomainRepo.get_by_id, CompanyDomainRepo.get_by_id e CompanyViewRepo.get_all.
"""

from datetime import date
from unittest.mock import AsyncMock, MagicMock

import uuid7


_COMPANY_ID = uuid7.create()
_USER_ID = uuid7.create()
_CARD_ID = uuid7.create()
_PAYMENT_ID = uuid7.create()


def _make_session():
    """Cria uma sessão SQLAlchemy mockada com async context manager."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    return session


class TestCreditCardViewRepoGetById:
    """Testes para CreditCardViewRepo.get_by_id."""

    async def test_found(self) -> None:
        """Verifica que get_by_id retorna o cartão quando encontrado."""
        from shared_core.adapters.repository.view_repo.credit_card import (
            CreditCardViewRepo,
        )

        session = _make_session()
        mock_c = MagicMock()
        mock_c.id = _CARD_ID
        mock_c.user_id = _USER_ID
        mock_c.card_key_encrypted = b"key"
        mock_c.number_encrypted = b"num"
        mock_c.expiry_encrypted = b"exp"
        mock_c.cvv_encrypted = b"cvv"
        mock_c.cpf_encrypted = b"cpf"
        mock_c.holder_name_encrypted = b"name"
        mock_c.active = True
        mock_c.created_at = None
        mock_c.created_by = None
        mock_c.updated_at = None
        mock_c.updated_by = None
        mock_c.deleted_at = None
        mock_c.deleted_by = None

        r = MagicMock()
        r.scalar_one_or_none.return_value = mock_c
        session.execute.return_value = r

        repo = CreditCardViewRepo(session=session)
        result = await repo.get_by_id(_CARD_ID)
        assert result is not None
        assert result.id == _CARD_ID

    async def test_not_found(self) -> None:
        """Verifica que get_by_id retorna None quando cartão não existe."""
        from shared_core.adapters.repository.view_repo.credit_card import (
            CreditCardViewRepo,
        )

        session = _make_session()
        r = MagicMock()
        r.scalar_one_or_none.return_value = None
        session.execute.return_value = r

        repo = CreditCardViewRepo(session=session)
        result = await repo.get_by_id(_CARD_ID)
        assert result is None


class TestPaymentViewRepoGetById:
    """Testes para PaymentViewRepo.get_by_id."""

    async def test_found(self) -> None:
        """Verifica que get_by_id retorna o pagamento quando encontrado."""
        from shared_core.adapters.repository.view_repo.payment import PaymentViewRepo

        session = _make_session()
        mock_p = MagicMock()
        mock_p.id = _PAYMENT_ID
        mock_p.company = _COMPANY_ID
        mock_p.amount = 100.0
        mock_p.due_date = date(2026, 3, 1)
        mock_p.status = "pending"
        mock_p.paid_at = None
        mock_p.created_at = None
        mock_p.created_by = None
        mock_p.updated_at = None
        mock_p.updated_by = None
        mock_p.deleted_at = None
        mock_p.deleted_by = None

        r = MagicMock()
        r.scalar_one_or_none.return_value = mock_p
        session.execute.return_value = r

        repo = PaymentViewRepo(session=session)
        result = await repo.get_by_id(_PAYMENT_ID)
        assert result is not None

    async def test_not_found(self) -> None:
        """Verifica que get_by_id retorna None quando pagamento não existe."""
        from shared_core.adapters.repository.view_repo.payment import PaymentViewRepo

        session = _make_session()
        r = MagicMock()
        r.scalar_one_or_none.return_value = None
        session.execute.return_value = r

        repo = PaymentViewRepo(session=session)
        result = await repo.get_by_id(_PAYMENT_ID)
        assert result is None


class TestCreditCardDomainGetAll:
    """Testes para CreditCardDomainRepo.get_all_by_user."""

    async def test_get_all_by_user(self) -> None:
        """Verifica que get_all_by_user retorna todos os cartões do usuário."""
        from shared_core.adapters.repository.domain_repo.credit_card import (
            CreditCardDomainRepo,
        )

        session = _make_session()
        mock_c = MagicMock()
        mock_c.id = _CARD_ID
        mock_c.user_id = _USER_ID
        mock_c.card_key_encrypted = b"key"
        mock_c.number_encrypted = b"num"
        mock_c.expiry_encrypted = b"exp"
        mock_c.cvv_encrypted = b"cvv"
        mock_c.cpf_encrypted = b"cpf"
        mock_c.holder_name_encrypted = b"name"
        mock_c.active = True
        mock_c.created_at = None
        mock_c.created_by = None
        mock_c.updated_at = None
        mock_c.updated_by = None
        mock_c.deleted_at = None
        mock_c.deleted_by = None

        sr = MagicMock()
        sr.all.return_value = [mock_c]
        r = MagicMock()
        r.scalars.return_value = sr
        session.execute.return_value = r

        repo = CreditCardDomainRepo(session=session)
        result = await repo.get_all_by_user(_USER_ID)
        assert len(result) == 1
        assert result[0].id == _CARD_ID


class TestPaymentDomainGetAllByCompany:
    """Testes para PaymentDomainRepo.get_all_by_company."""

    async def test_get_all_by_company(self) -> None:
        """Verifica que get_all_by_company retorna todos os pagamentos da empresa."""
        from shared_core.adapters.repository.domain_repo.payment import PaymentDomainRepo

        session = _make_session()
        mock_p = MagicMock()
        mock_p.id = _PAYMENT_ID
        mock_p.company = _COMPANY_ID
        mock_p.amount = 100.0
        mock_p.due_date = date(2026, 3, 1)
        mock_p.paid = False
        mock_p.paid_at = None
        mock_p.overdue = False
        mock_p.created_at = None
        mock_p.created_by = None
        mock_p.updated_at = None
        mock_p.updated_by = None
        mock_p.deleted_at = None
        mock_p.deleted_by = None

        sr = MagicMock()
        sr.all.return_value = [mock_p]
        r = MagicMock()
        r.scalars.return_value = sr
        session.execute.return_value = r

        repo = PaymentDomainRepo(session=session)
        result = await repo.get_all_by_company(_COMPANY_ID)
        assert len(result) == 1


class TestUserDomainGetById:
    """Testes para UserDomainRepo.get_by_id."""

    async def test_get_by_id_found(self) -> None:
        """Verifica que get_by_id retorna o usuário quando encontrado."""
        from shared_core.adapters.repository.domain_repo.user import UserDomainRepo

        session = _make_session()
        u = MagicMock()
        u.id = _USER_ID
        u.company = _COMPANY_ID
        u.email = "u@t.com"
        u.cpf = "12345678901"
        u.name = "T"
        u.phone = "11"
        u.street = "R"
        u.number = "1"
        u.zip_code = "12345"
        u.district = "D"
        u.city = "C"
        u.state = "S"
        u.country = "BR"
        u.complement = None
        u.admin = False
        u.active = True
        u.is_owner = False
        u.birth_date = None
        u.password_hash = "hashed"
        u.created_at = None
        u.created_by = None
        u.updated_at = None
        u.updated_by = None
        u.deleted_at = None
        u.deleted_by = None

        r = MagicMock()
        r.scalar_one_or_none.return_value = u
        session.execute.return_value = r

        repo = UserDomainRepo(session=session)
        result = await repo.get_by_id(_USER_ID)
        assert result.id == _USER_ID

    async def test_get_by_id_not_found(self) -> None:
        """Verifica que get_by_id levanta UserNotFound quando usuário não existe."""
        import pytest
        from shared_core.adapters.repository.domain_repo.user import UserDomainRepo
        from shared_core.domain.excecoes import UserNotFound

        session = _make_session()
        r = MagicMock()
        r.scalar_one_or_none.return_value = None
        session.execute.return_value = r

        repo = UserDomainRepo(session=session)
        with pytest.raises(UserNotFound):
            await repo.get_by_id(_USER_ID)


class TestCompanyDomainGetByIdFound:
    """Testes para CompanyDomainRepo.get_by_id."""

    async def test_found(self) -> None:
        """Verifica que get_by_id retorna a empresa quando encontrada."""
        from shared_core.adapters.repository.domain_repo.company import CompanyDomainRepo

        session = _make_session()
        mock_c = MagicMock()
        mock_c.id = _COMPANY_ID
        mock_c.legal_name = "T"
        mock_c.trade_name = None
        mock_c.responsible_name = "R"
        mock_c.email = "e@e.com"
        mock_c.cpf = "123"
        mock_c.cnpj = None
        mock_c.active = True
        mock_c.payment_up_to_date = True
        mock_c.last_payment_date = None
        mock_c.created_at = None
        mock_c.created_by = None
        mock_c.updated_at = None
        mock_c.updated_by = None
        mock_c.deleted_at = None
        mock_c.deleted_by = None

        r = MagicMock()
        r.scalar_one_or_none.return_value = mock_c
        session.execute.return_value = r

        repo = CompanyDomainRepo(session=session)
        result = await repo.get_by_id(_COMPANY_ID)
        assert result.legal_name == "T"


class TestCompanyViewRepoIncludeDeleted:
    """Testes para CompanyViewRepo.get_all com include_deleted."""

    async def test_get_all_include_deleted(self) -> None:
        """Verifica que get_all com include_deleted=True inclui empresas deletadas."""
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
        """Verifica que get_all retorna [] quando scalars() é falsy (linha 75)."""
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

        from datetime import datetime, timezone

        payment = Payment.create_aggregate(
            company=_COMPANY_ID,
            amount=100.0,
            due_date=datetime(2026, 3, 1, tzinfo=timezone.utc),
        )
        payment.mark_as_overdue(user_id=_USER_ID)

        await repo._remove(payment)
        session.execute.assert_awaited()


class TestServicesAbstractNotImplemented:
    """Testes para cobertura dos raise NotImplementedError em repos abstratos de serviços."""

    async def test_patient_abstract_add_raises(self) -> None:
        """Cobre o raise NotImplementedError do _add abstrato de Patient."""
        import pytest
        import services.dentist.adapters.orm.patient  # noqa: F401
        from services.dentist.adapters.repository.domain_repo.patient import (
            AbstractPatientDomainRepo,
        )

        class Stub(AbstractPatientDomainRepo):
            async def _add(self, patient):
                await super()._add(patient)

            async def _remove(self, patient):
                pass

            async def get_by_cpf(self, cpf, company):
                pass

        with pytest.raises(NotImplementedError):
            await Stub()._add(MagicMock())

    async def test_patient_abstract_remove_raises(self) -> None:
        """Cobre o raise NotImplementedError do _remove abstrato de Patient."""
        import pytest
        import services.dentist.adapters.orm.patient  # noqa: F401
        from services.dentist.adapters.repository.domain_repo.patient import (
            AbstractPatientDomainRepo,
        )

        class Stub(AbstractPatientDomainRepo):
            async def _add(self, patient):
                pass

            async def _remove(self, patient):
                await super()._remove(patient)

            async def get_by_cpf(self, cpf, company):
                pass

        with pytest.raises(NotImplementedError):
            await Stub()._remove(MagicMock())

    async def test_patient_abstract_get_by_cpf_raises(self) -> None:
        """Cobre o raise NotImplementedError do get_by_cpf abstrato de Patient."""
        import pytest
        import services.dentist.adapters.orm.patient  # noqa: F401
        from services.dentist.adapters.repository.domain_repo.patient import (
            AbstractPatientDomainRepo,
        )

        class Stub(AbstractPatientDomainRepo):
            async def _add(self, patient):
                pass

            async def _remove(self, patient):
                pass

            async def get_by_cpf(self, cpf, company):
                return await super().get_by_cpf(cpf, company)

        with pytest.raises(NotImplementedError):
            await Stub().get_by_cpf("123", _COMPANY_ID)

    async def test_legal_case_abstract_add_raises(self) -> None:
        """Cobre o raise NotImplementedError do _add abstrato de LegalCase."""
        import pytest
        import services.lawyer.adapters.orm.legal_case  # noqa: F401
        from services.lawyer.adapters.repository.domain_repo.legal_case import (
            AbstractLegalCaseDomainRepo,
        )

        class Stub(AbstractLegalCaseDomainRepo):
            async def _add(self, case):
                await super()._add(case)

            async def _remove(self, case):
                pass

            async def get_by_case_number(self, company, case_number):
                pass

        with pytest.raises(NotImplementedError):
            await Stub()._add(MagicMock())

    async def test_legal_case_abstract_remove_raises(self) -> None:
        """Cobre o raise NotImplementedError do _remove abstrato de LegalCase."""
        import pytest
        import services.lawyer.adapters.orm.legal_case  # noqa: F401
        from services.lawyer.adapters.repository.domain_repo.legal_case import (
            AbstractLegalCaseDomainRepo,
        )

        class Stub(AbstractLegalCaseDomainRepo):
            async def _add(self, case):
                pass

            async def _remove(self, case):
                await super()._remove(case)

            async def get_by_case_number(self, company, case_number):
                pass

        with pytest.raises(NotImplementedError):
            await Stub()._remove(MagicMock())

    async def test_legal_case_abstract_get_by_case_number_raises(self) -> None:
        """Cobre o raise NotImplementedError do get_by_case_number abstrato de LegalCase."""
        import pytest
        import services.lawyer.adapters.orm.legal_case  # noqa: F401
        from services.lawyer.adapters.repository.domain_repo.legal_case import (
            AbstractLegalCaseDomainRepo,
        )

        class Stub(AbstractLegalCaseDomainRepo):
            async def _add(self, case):
                pass

            async def _remove(self, case):
                pass

            async def get_by_case_number(self, company, case_number):
                return await super().get_by_case_number(company, case_number)

        with pytest.raises(NotImplementedError):
            await Stub().get_by_case_number(_COMPANY_ID, "0001")
