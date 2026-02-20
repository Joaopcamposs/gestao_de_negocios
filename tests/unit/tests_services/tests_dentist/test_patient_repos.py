"""Testes unitários para os repositórios concretos de Patient (domain + view) do serviço Dentist."""

from unittest.mock import AsyncMock, MagicMock

import uuid7

import services.dentist.adapters.orm.patient  # noqa: F401 — inicializa o mapeamento ORM


_COMPANY_ID = uuid7.create()
_USER_ID = uuid7.create()


def _make_session():
    """Cria uma sessão SQLAlchemy mockada com async context manager."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    return session


# ─── PatientDomainRepo ───


class TestPatientDomainRepo:
    """Testes para o repositório de domínio concreto de Patient."""

    async def test_create_aggregate(self) -> None:
        """Verifica que create_aggregate cria um paciente com sucesso."""
        from services.dentist.adapters.repository.domain_repo.patient import (
            PatientDomainRepo,
        )

        session = _make_session()
        r = MagicMock()
        r.scalar_one_or_none.return_value = None
        session.execute.return_value = r

        repo = PatientDomainRepo(session=session)

        patient = await repo.create_aggregate(
            company=_COMPANY_ID,
            name="Paciente",
            cpf="12345678901",
        )
        assert patient.name == "Paciente"

    async def test_get_by_cpf_found(self) -> None:
        """Verifica que get_by_cpf retorna o paciente quando encontrado."""
        from services.dentist.adapters.repository.domain_repo.patient import (
            PatientDomainRepo,
        )

        session = _make_session()
        mock_p = MagicMock()
        mock_p.id = uuid7.create()
        mock_p.company = _COMPANY_ID
        mock_p.name = "P"
        mock_p.cpf = "12345678901"
        mock_p.phone = "11"
        mock_p.birth_date = None
        mock_p.notes = ""
        mock_p.active = True
        mock_p.created_at = None
        mock_p.created_by = None
        mock_p.updated_at = None
        mock_p.updated_by = None
        mock_p.deleted_at = None
        mock_p.deleted_by = None

        r = MagicMock()
        r.scalar_one_or_none.return_value = mock_p
        session.execute.return_value = r

        repo = PatientDomainRepo(session=session)
        result = await repo.get_by_cpf(_COMPANY_ID, "12345678901")
        assert result.cpf == "12345678901"

    async def test_add_and_remove(self) -> None:
        """Verifica que _add e _remove executam operações na sessão."""
        from services.dentist.adapters.repository.domain_repo.patient import (
            PatientDomainRepo,
        )
        from services.dentist.domain.aggregate.patient import Patient

        session = _make_session()
        repo = PatientDomainRepo(session=session)

        patient = Patient.create_aggregate(
            company=_COMPANY_ID, name="P", cpf="12345678901"
        )
        patient.create(_USER_ID)
        await repo._add(patient)
        session.execute.assert_awaited()

        session.reset_mock()
        patient.delete(_USER_ID)
        await repo._remove(patient)
        session.execute.assert_awaited()


# ─── PatientViewRepo ───


class TestPatientViewRepo:
    """Testes para o repositório de view concreto de Patient."""

    async def test_get_by_cpf_found(self) -> None:
        """Verifica que get_by_cpf retorna o paciente quando encontrado."""
        from services.dentist.adapters.repository.view_repo.patient import (
            PatientViewRepo,
        )

        session = _make_session()
        mock_p = MagicMock()
        mock_p.id = uuid7.create()
        mock_p.company = _COMPANY_ID
        mock_p.name = "P"
        mock_p.cpf = "12345678901"
        mock_p.phone = "11"
        mock_p.birth_date = None
        mock_p.notes = ""
        mock_p.active = True
        mock_p.deleted_at = None
        mock_p.deleted_by = None
        mock_p.created_at = None
        mock_p.created_by = None
        mock_p.updated_at = None
        mock_p.updated_by = None

        r = MagicMock()
        r.scalar_one_or_none.return_value = mock_p
        session.execute.return_value = r

        repo = PatientViewRepo(session=session)
        result = await repo.get_by_cpf(_COMPANY_ID, "12345678901")
        assert result is not None

    async def test_get_by_cpf_not_found(self) -> None:
        """Verifica que get_by_cpf retorna None quando não encontrado."""
        from services.dentist.adapters.repository.view_repo.patient import (
            PatientViewRepo,
        )

        session = _make_session()
        r = MagicMock()
        r.scalar_one_or_none.return_value = None
        session.execute.return_value = r

        repo = PatientViewRepo(session=session)
        result = await repo.get_by_cpf(_COMPANY_ID, "99999999999")
        assert result is None

    async def test_get_all(self) -> None:
        """Verifica que get_all retorna todos os pacientes da empresa."""
        from services.dentist.adapters.repository.view_repo.patient import (
            PatientViewRepo,
        )

        session = _make_session()
        sr = MagicMock()
        sr.all.return_value = []
        r = MagicMock()
        r.scalars.return_value = sr
        session.execute.return_value = r

        repo = PatientViewRepo(session=session)
        result = await repo.get_all(company=_COMPANY_ID)
        assert result == []

    async def test_get_all_empty_scalars_returns_empty(self) -> None:
        """Verifica que get_all retorna [] quando scalars() é falsy (linha 80)."""
        from services.dentist.adapters.repository.view_repo.patient import (
            PatientViewRepo,
        )

        session = _make_session()
        r = MagicMock()
        r.scalars.return_value = None
        session.execute.return_value = r

        repo = PatientViewRepo(session=session)
        result = await repo.get_all(company=_COMPANY_ID)
        assert result == []


class TestPatientDomainRepoAddRemove:
    """Testes para os métodos públicos add() e remove() do PatientDomainRepo."""

    async def test_add_tracks_seen(self) -> None:
        """Verifica que add() rastreia o paciente no conjunto seen."""
        from services.dentist.adapters.repository.domain_repo.patient import (
            PatientDomainRepo,
        )
        from services.dentist.domain.aggregate.patient import Patient

        session = _make_session()
        repo = PatientDomainRepo(session=session)

        patient = Patient.create_aggregate(
            company=_COMPANY_ID, name="P", cpf="12345678901"
        )
        patient.create(_USER_ID)

        r = MagicMock()
        r.scalar_one_or_none.return_value = None
        session.execute.return_value = r

        await repo.add(patient)
        assert patient in repo.seen

    async def test_remove_tracks_seen(self) -> None:
        """Verifica que remove() rastreia o paciente no conjunto seen."""
        from services.dentist.adapters.repository.domain_repo.patient import (
            PatientDomainRepo,
        )
        from services.dentist.domain.aggregate.patient import Patient

        session = _make_session()
        repo = PatientDomainRepo(session=session)

        patient = Patient.create_aggregate(
            company=_COMPANY_ID, name="P", cpf="12345678901"
        )
        patient.delete(_USER_ID)

        await repo.remove(patient)
        assert patient in repo.seen

    async def test_get_by_cpf_not_found_raises(self) -> None:
        """Verifica que get_by_cpf levanta PatientNotFound quando não encontrado."""
        import pytest
        from services.dentist.adapters.repository.domain_repo.patient import (
            PatientDomainRepo,
        )
        from services.dentist.domain.exceptions import PatientNotFound

        session = _make_session()
        r = MagicMock()
        r.scalar_one_or_none.return_value = None
        session.execute.return_value = r

        repo = PatientDomainRepo(session=session)
        with pytest.raises(PatientNotFound):
            await repo.get_by_cpf("99999999999", _COMPANY_ID)
