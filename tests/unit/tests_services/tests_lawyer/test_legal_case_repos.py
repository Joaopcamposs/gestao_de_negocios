"""Testes unitários para os repositórios concretos de LegalCase (domain + view) do serviço Lawyer."""

from unittest.mock import AsyncMock, MagicMock

import uuid7

import services.lawyer.adapters.orm.legal_case  # noqa: F401 — inicializa o mapeamento ORM


_COMPANY_ID = uuid7.create()
_USER_ID = uuid7.create()


def _make_session():
    """Cria uma sessão SQLAlchemy mockada com async context manager."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    return session


# ─── LegalCaseDomainRepo ───


class TestLegalCaseDomainRepo:
    """Testes para o repositório de domínio concreto de LegalCase."""

    async def test_create_aggregate(self) -> None:
        """Verifica que create_aggregate cria um caso jurídico com sucesso."""
        from services.lawyer.adapters.repository.domain_repo.legal_case import (
            LegalCaseDomainRepo,
        )

        session = _make_session()
        r = MagicMock()
        r.scalar_one_or_none.return_value = None
        session.execute.return_value = r

        repo = LegalCaseDomainRepo(session=session)

        case = await repo.create_aggregate(
            company=_COMPANY_ID,
            case_number="0001",
            client_name="Client A",
        )
        assert case.case_number == "0001"

    async def test_get_by_case_number_found(self) -> None:
        """Verifica que get_by_case_number retorna o caso quando encontrado."""
        from services.lawyer.adapters.repository.domain_repo.legal_case import (
            LegalCaseDomainRepo,
        )

        session = _make_session()
        mock_lc = MagicMock()
        mock_lc.id = uuid7.create()
        mock_lc.company = _COMPANY_ID
        mock_lc.case_number = "0001"
        mock_lc.client_name = "A"
        mock_lc.description = None
        mock_lc.status = "Open"
        mock_lc.open_date = None
        mock_lc.close_date = None
        mock_lc.notes = ""
        mock_lc.active = True
        mock_lc.created_at = None
        mock_lc.created_by = None
        mock_lc.updated_at = None
        mock_lc.updated_by = None
        mock_lc.deleted_at = None
        mock_lc.deleted_by = None

        r = MagicMock()
        r.scalar_one_or_none.return_value = mock_lc
        session.execute.return_value = r

        repo = LegalCaseDomainRepo(session=session)
        result = await repo.get_by_case_number(_COMPANY_ID, "0001")
        assert result.case_number == "0001"

    async def test_add_and_remove(self) -> None:
        """Verifica que _add e _remove executam operações na sessão."""
        from services.lawyer.adapters.repository.domain_repo.legal_case import (
            LegalCaseDomainRepo,
        )
        from services.lawyer.domain.aggregate.legal_case import LegalCase

        session = _make_session()
        repo = LegalCaseDomainRepo(session=session)

        case = LegalCase.create_aggregate(
            company=_COMPANY_ID, case_number="0001", client_name="A"
        )
        case.create(_USER_ID)
        await repo._add(case)
        session.execute.assert_awaited()

        session.reset_mock()
        case.delete(_USER_ID)
        await repo._remove(case)
        session.execute.assert_awaited()


# ─── LegalCaseViewRepo ───


class TestLegalCaseViewRepo:
    """Testes para o repositório de view concreto de LegalCase."""

    async def test_get_by_case_number_found(self) -> None:
        """Verifica que get_by_case_number retorna o caso quando encontrado."""
        from services.lawyer.adapters.repository.view_repo.legal_case import (
            LegalCaseViewRepo,
        )

        session = _make_session()
        mock_lc = MagicMock()
        mock_lc.id = uuid7.create()
        mock_lc.company = _COMPANY_ID
        mock_lc.case_number = "0001"
        mock_lc.client_name = "A"
        mock_lc.description = None
        mock_lc.status = "Open"
        mock_lc.open_date = None
        mock_lc.close_date = None
        mock_lc.notes = ""
        mock_lc.active = True
        mock_lc.deleted_at = None
        mock_lc.deleted_by = None
        mock_lc.created_at = None
        mock_lc.created_by = None
        mock_lc.updated_at = None
        mock_lc.updated_by = None

        r = MagicMock()
        r.scalar_one_or_none.return_value = mock_lc
        session.execute.return_value = r

        repo = LegalCaseViewRepo(session=session)
        result = await repo.get_by_case_number(_COMPANY_ID, "0001")
        assert result is not None

    async def test_get_by_case_number_not_found(self) -> None:
        """Verifica que get_by_case_number retorna None quando não encontrado."""
        from services.lawyer.adapters.repository.view_repo.legal_case import (
            LegalCaseViewRepo,
        )

        session = _make_session()
        r = MagicMock()
        r.scalar_one_or_none.return_value = None
        session.execute.return_value = r

        repo = LegalCaseViewRepo(session=session)
        result = await repo.get_by_case_number(_COMPANY_ID, "9999")
        assert result is None

    async def test_get_all(self) -> None:
        """Verifica que get_all retorna todos os casos da empresa."""
        from services.lawyer.adapters.repository.view_repo.legal_case import (
            LegalCaseViewRepo,
        )

        session = _make_session()
        sr = MagicMock()
        sr.all.return_value = []
        r = MagicMock()
        r.scalars.return_value = sr
        session.execute.return_value = r

        repo = LegalCaseViewRepo(session=session)
        result = await repo.get_all(company=_COMPANY_ID)
        assert result == []

    async def test_get_all_empty_scalars_returns_empty(self) -> None:
        """Verifica que get_all retorna [] quando scalars() é falsy (linha 81)."""
        from services.lawyer.adapters.repository.view_repo.legal_case import (
            LegalCaseViewRepo,
        )

        session = _make_session()
        r = MagicMock()
        r.scalars.return_value = None
        session.execute.return_value = r

        repo = LegalCaseViewRepo(session=session)
        result = await repo.get_all(company=_COMPANY_ID)
        assert result == []


class TestLegalCaseDomainRepoAddRemove:
    """Testes para os métodos públicos add() e remove() do LegalCaseDomainRepo."""

    async def test_add_tracks_seen(self) -> None:
        """Verifica que add() rastreia o caso no conjunto seen."""
        from services.lawyer.adapters.repository.domain_repo.legal_case import (
            LegalCaseDomainRepo,
        )
        from services.lawyer.domain.aggregate.legal_case import LegalCase

        session = _make_session()
        repo = LegalCaseDomainRepo(session=session)

        case = LegalCase.create_aggregate(
            company=_COMPANY_ID, case_number="0001", client_name="A"
        )
        case.create(_USER_ID)

        r = MagicMock()
        r.scalar_one_or_none.return_value = None
        session.execute.return_value = r

        await repo.add(case)
        assert case in repo.seen

    async def test_remove_tracks_seen(self) -> None:
        """Verifica que remove() rastreia o caso no conjunto seen."""
        from services.lawyer.adapters.repository.domain_repo.legal_case import (
            LegalCaseDomainRepo,
        )
        from services.lawyer.domain.aggregate.legal_case import LegalCase

        session = _make_session()
        repo = LegalCaseDomainRepo(session=session)

        case = LegalCase.create_aggregate(
            company=_COMPANY_ID, case_number="0001", client_name="A"
        )
        case.delete(_USER_ID)

        await repo.remove(case)
        assert case in repo.seen

    async def test_get_by_case_number_not_found_raises(self) -> None:
        """Verifica que get_by_case_number levanta LegalCaseNotFound quando não encontrado."""
        import pytest
        from services.lawyer.adapters.repository.domain_repo.legal_case import (
            LegalCaseDomainRepo,
        )
        from services.lawyer.domain.exceptions import LegalCaseNotFound

        session = _make_session()
        r = MagicMock()
        r.scalar_one_or_none.return_value = None
        session.execute.return_value = r

        repo = LegalCaseDomainRepo(session=session)
        with pytest.raises(LegalCaseNotFound):
            await repo.get_by_case_number("9999", _COMPANY_ID)
