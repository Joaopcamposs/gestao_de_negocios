"""Testes unitários para os repositórios concretos de Company (domain + view)."""

from unittest.mock import AsyncMock, MagicMock

import pytest
import uuid7

from shared_core.domain.aggregate.company import Company
from shared_core.domain.excecoes import (
    CompanyAlreadyRegistered,
    CompanyNotFound,
)


_COMPANY_ID = uuid7.create()
_USER_ID = uuid7.create()


def _make_session():
    """Cria uma sessão SQLAlchemy mockada com async context manager."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    return session


# ─── CompanyDomainRepo (métodos concretos) ───


class TestCompanyDomainRepoConcrete:
    """Testes para o repositório de domínio concreto de Company."""

    async def test_validate_company_email_existing_raises(self) -> None:
        """Verifica que validate_company_email levanta erro para email existente."""
        from shared_core.adapters.repository.domain_repo.company import (
            CompanyDomainRepo,
        )

        session = _make_session()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = ("existing_hash",)
        session.execute.return_value = mock_result

        repo = CompanyDomainRepo(session=session)

        with pytest.raises(ValueError, match="já existe"):
            await repo.validate_company_email("test@test.com")

    async def test_validate_company_email_new_ok(self) -> None:
        """Verifica que validate_company_email aceita email novo."""
        from shared_core.adapters.repository.domain_repo.company import (
            CompanyDomainRepo,
        )

        session = _make_session()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        session.execute.return_value = mock_result

        repo = CompanyDomainRepo(session=session)
        await repo.validate_company_email("new@test.com")

    async def test_create_aggregate_existing_raises(self) -> None:
        """Verifica que create_aggregate levanta CompanyAlreadyRegistered para empresa existente."""
        from shared_core.adapters.repository.domain_repo.company import (
            CompanyDomainRepo,
        )

        session = _make_session()

        result1 = MagicMock()
        result1.fetchone.return_value = None

        result2 = MagicMock()
        result2.scalar_one_or_none.return_value = MagicMock()

        session.execute.side_effect = [result1, result2]

        repo = CompanyDomainRepo(session=session)

        with pytest.raises(CompanyAlreadyRegistered):
            await repo.create_aggregate(
                legal_name="Existing",
                trade_name=None,
                responsible_name="R",
                email="e@e.com",
                cpf="12345678901",
                cnpj=None,
                active=True,
            )

    async def test_create_aggregate_success(self) -> None:
        """Verifica que create_aggregate cria uma empresa com sucesso."""
        from shared_core.adapters.repository.domain_repo.company import (
            CompanyDomainRepo,
        )

        session = _make_session()

        result1 = MagicMock()
        result1.fetchone.return_value = None

        result2 = MagicMock()
        result2.scalar_one_or_none.return_value = None

        session.execute.side_effect = [result1, result2]

        repo = CompanyDomainRepo(session=session)

        company = await repo.create_aggregate(
            legal_name="New Company",
            trade_name="NC",
            responsible_name="R",
            email="new@test.com",
            cpf="12345678901",
            cnpj=None,
            active=True,
        )

        assert company.legal_name == "New Company"

    async def test_get_by_legal_name_not_found(self) -> None:
        """Verifica que get_by_legal_name levanta CompanyNotFound quando não encontrado."""
        from shared_core.adapters.repository.domain_repo.company import (
            CompanyDomainRepo,
        )

        session = _make_session()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        session.execute.return_value = mock_result

        repo = CompanyDomainRepo(session=session)

        with pytest.raises(CompanyNotFound):
            await repo.get_by_legal_name("Inexistente")

    async def test_get_by_legal_name_found(self) -> None:
        """Verifica que get_by_legal_name retorna a empresa quando encontrada."""
        from shared_core.adapters.repository.domain_repo.company import (
            CompanyDomainRepo,
        )

        session = _make_session()

        mock_company = MagicMock()
        mock_company.id = _COMPANY_ID
        mock_company.legal_name = "Test"
        mock_company.trade_name = "T"
        mock_company.responsible_name = "R"
        mock_company.email = "e@e.com"
        mock_company.cpf = "12345678901"
        mock_company.cnpj = None
        mock_company.active = True
        mock_company.payment_up_to_date = True
        mock_company.last_payment_date = None
        mock_company.created_at = None
        mock_company.created_by = None
        mock_company.updated_at = None
        mock_company.updated_by = None
        mock_company.deleted_at = None
        mock_company.deleted_by = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_company
        session.execute.return_value = mock_result

        repo = CompanyDomainRepo(session=session)
        result = await repo.get_by_legal_name("Test")
        assert result.legal_name == "Test"

    async def test_get_by_id_not_found(self) -> None:
        """Verifica que get_by_id levanta CompanyNotFound quando não encontrado."""
        from shared_core.adapters.repository.domain_repo.company import (
            CompanyDomainRepo,
        )

        session = _make_session()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        session.execute.return_value = mock_result

        repo = CompanyDomainRepo(session=session)

        with pytest.raises(CompanyNotFound):
            await repo.get_by_id(_COMPANY_ID)

    async def test_get_by_id_found(self) -> None:
        """Verifica que get_by_id retorna a empresa quando encontrada."""
        from shared_core.adapters.repository.domain_repo.company import (
            CompanyDomainRepo,
        )

        session = _make_session()

        mock_company = MagicMock()
        mock_company.id = _COMPANY_ID
        mock_company.legal_name = "ByID"
        mock_company.trade_name = None
        mock_company.responsible_name = "R"
        mock_company.email = "e@e.com"
        mock_company.cpf = "12345678901"
        mock_company.cnpj = None
        mock_company.active = True
        mock_company.payment_up_to_date = True
        mock_company.last_payment_date = None
        mock_company.created_at = None
        mock_company.created_by = None
        mock_company.updated_at = None
        mock_company.updated_by = None
        mock_company.deleted_at = None
        mock_company.deleted_by = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_company
        session.execute.return_value = mock_result

        repo = CompanyDomainRepo(session=session)
        result = await repo.get_by_id(_COMPANY_ID)
        assert result.legal_name == "ByID"

    async def test_get_all_active(self) -> None:
        """Verifica que get_all_active retorna empresas ativas."""
        from shared_core.adapters.repository.domain_repo.company import (
            CompanyDomainRepo,
        )

        session = _make_session()

        mock_c = MagicMock()
        mock_c.id = _COMPANY_ID
        mock_c.legal_name = "Active"
        mock_c.trade_name = None
        mock_c.responsible_name = "R"
        mock_c.email = "e@e.com"
        mock_c.cpf = "12345678901"
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

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_c]
        mock_result.scalars.return_value = mock_scalars
        session.execute.return_value = mock_result

        repo = CompanyDomainRepo(session=session)
        result = await repo.get_all_active()
        assert len(result) == 1
        assert result[0].legal_name == "Active"

    async def test_add_calls_upsert(self) -> None:
        """Verifica que _add executa upsert na sessão."""
        from shared_core.adapters.repository.domain_repo.company import (
            CompanyDomainRepo,
        )

        session = _make_session()
        repo = CompanyDomainRepo(session=session)

        company = Company.create_aggregate(
            legal_name="Test",
            trade_name=None,
            responsible_name="R",
            email="e@e.com",
            cpf="12345678901",
            cnpj=None,
            active=True,
        )
        company.create(_USER_ID)

        await repo._add(company)
        session.execute.assert_awaited_once()

    async def test_remove_calls_soft_delete(self) -> None:
        """Verifica que _remove executa soft delete na sessão."""
        from shared_core.adapters.repository.domain_repo.company import (
            CompanyDomainRepo,
        )

        session = _make_session()
        repo = CompanyDomainRepo(session=session)

        company = Company.create_aggregate(
            legal_name="Test",
            trade_name=None,
            responsible_name="R",
            email="e@e.com",
            cpf="12345678901",
            cnpj=None,
            active=True,
        )
        company.delete(_USER_ID)

        await repo._remove(company)
        session.execute.assert_awaited_once()


# ─── CompanyViewRepo ───


class TestCompanyViewRepoConcrete:
    """Testes para o repositório de view concreto de Company."""

    async def test_get_by_legal_name_found(self) -> None:
        """Verifica que get_by_legal_name retorna a empresa quando encontrada."""
        from shared_core.adapters.repository.view_repo.company import CompanyViewRepo

        session = _make_session()

        mock_c = MagicMock()
        mock_c.id = _COMPANY_ID
        mock_c.legal_name = "Found"
        mock_c.trade_name = None
        mock_c.responsible_name = "R"
        mock_c.email = "e@e.com"
        mock_c.cpf = "123"
        mock_c.cnpj = None
        mock_c.active = True
        mock_c.payment_up_to_date = True
        mock_c.last_payment_date = None
        mock_c.deleted_at = None
        mock_c.deleted_by = None
        mock_c.created_at = None
        mock_c.created_by = None
        mock_c.updated_at = None
        mock_c.updated_by = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_c
        session.execute.return_value = mock_result

        repo = CompanyViewRepo(session=session)
        result = await repo.get_by_legal_name("Found")
        assert result is not None
        assert result.legal_name == "Found"

    async def test_get_by_legal_name_not_found(self) -> None:
        """Verifica que get_by_legal_name retorna None quando não encontrada."""
        from shared_core.adapters.repository.view_repo.company import CompanyViewRepo

        session = _make_session()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        session.execute.return_value = mock_result

        repo = CompanyViewRepo(session=session)
        result = await repo.get_by_legal_name("None")
        assert result is None

    async def test_get_all(self) -> None:
        """Verifica que get_all retorna todas as empresas."""
        from shared_core.adapters.repository.view_repo.company import CompanyViewRepo

        session = _make_session()

        mock_c = MagicMock()
        mock_c.id = _COMPANY_ID
        mock_c.legal_name = "All"
        mock_c.trade_name = None
        mock_c.responsible_name = "R"
        mock_c.email = "e@e.com"
        mock_c.cpf = "123"
        mock_c.cnpj = None
        mock_c.active = True
        mock_c.payment_up_to_date = True
        mock_c.last_payment_date = None
        mock_c.deleted_at = None
        mock_c.deleted_by = None
        mock_c.created_at = None
        mock_c.created_by = None
        mock_c.updated_at = None
        mock_c.updated_by = None

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.__iter__ = MagicMock(return_value=iter([mock_c]))
        mock_result.scalars.return_value = mock_scalars
        session.execute.return_value = mock_result

        repo = CompanyViewRepo(session=session)
        result = await repo.get_all()
        assert len(result) == 1

    async def test_get_all_include_deleted(self) -> None:
        """Verifica que get_all com include_deleted retorna empresas deletadas."""
        from shared_core.adapters.repository.view_repo.company import CompanyViewRepo

        session = _make_session()
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.__iter__ = MagicMock(return_value=iter([]))
        mock_result.scalars.return_value = mock_scalars
        session.execute.return_value = mock_result

        repo = CompanyViewRepo(session=session)
        result = await repo.get_all(include_deleted=True)
        assert result == []
