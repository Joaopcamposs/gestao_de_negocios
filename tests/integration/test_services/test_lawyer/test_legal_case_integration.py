"""Testes de integração para o fluxo de LegalCase no contexto advogado."""

from datetime import date
from uuid import UUID

import pytest
import uuid7

from messagebus.unity_of_work import UnitOfWork
from services.lawyer.adapters.views.legal_case import view_legal_case
from services.lawyer.bootstrap import bootstrap_lawyer
from services.lawyer.domain.commands.legal_case import (
    CreateLegalCase,
    DeleteLegalCase,
    UpdateLegalCase,
)
from services.lawyer.domain.exceptions import (
    LegalCaseAlreadyRegistered,
    LegalCaseNotFound,
)

_TEST_COMPANY_ID = uuid7.create()


def _bootstrap(**kwargs):
    """Bootstrap do lawyer para testes, usando schema public."""
    return bootstrap_lawyer(raise_event_errors=True, **kwargs)


def _create_case_cmd(case_number: str, client_name: str, **overrides) -> CreateLegalCase:
    """Função auxiliar para criar comando CreateLegalCase com valores padrão."""
    defaults = dict(
        company=_TEST_COMPANY_ID, case_number=case_number, client_name=client_name
    )
    defaults.update(overrides)
    return CreateLegalCase(**defaults)


class TestCreateLegalCase:
    """Testes de integração para criação de processo jurídico."""

    async def test_create_returns_uuid(self, engine) -> None:
        bus = _bootstrap()
        result = await bus.handle(_create_case_cmd("001", "João Silva"))
        assert isinstance(result, UUID)

    async def test_create_persists_in_database(self, engine) -> None:
        bus = _bootstrap()
        await bus.handle(_create_case_cmd("002", "Maria Souza"))

        uow = UnitOfWork()
        cases = await view_legal_case(uow, company=_TEST_COMPANY_ID, case_number="002")
        assert len(cases) == 1
        assert cases[0].client_name == "Maria Souza"
        assert cases[0].case_number == "002"
        assert cases[0].deleted_at is None

    async def test_create_with_all_fields(self, engine) -> None:
        bus = _bootstrap()
        open_dt = date(2024, 3, 10)
        await bus.handle(
            _create_case_cmd(
                "003",
                "Carlos Santos",
                description="Ação cível",
                status="in_progress",
                open_date=open_dt,
                notes="Prioridade alta",
            )
        )

        uow = UnitOfWork()
        cases = await view_legal_case(uow, company=_TEST_COMPANY_ID, case_number="003")
        assert len(cases) == 1
        c = cases[0]
        assert c.description == "Ação cível"
        assert c.status == "in_progress"
        assert c.open_date == open_dt
        assert c.notes == "Prioridade alta"

    async def test_create_duplicate_raises_error(self, engine) -> None:
        bus = _bootstrap()
        await bus.handle(_create_case_cmd("004", "Client A"))

        bus2 = _bootstrap()
        with pytest.raises(LegalCaseAlreadyRegistered):
            await bus2.handle(_create_case_cmd("004", "Client B"))


class TestUpdateLegalCase:
    """Testes de integração para atualização de processo jurídico."""

    async def test_update_changes_client_name(self, engine) -> None:
        bus = _bootstrap()
        await bus.handle(_create_case_cmd("010", "Nome Antigo"))

        bus2 = _bootstrap()
        await bus2.handle(
            UpdateLegalCase(
                company=_TEST_COMPANY_ID, case_number="010", new_client_name="Nome Novo"
            )
        )

        uow = UnitOfWork()
        cases = await view_legal_case(uow, company=_TEST_COMPANY_ID, case_number="010")
        assert len(cases) == 1
        assert cases[0].client_name == "Nome Novo"

    async def test_update_changes_status(self, engine) -> None:
        bus = _bootstrap()
        await bus.handle(_create_case_cmd("011", "Client"))

        bus2 = _bootstrap()
        await bus2.handle(
            UpdateLegalCase(
                company=_TEST_COMPANY_ID, case_number="011", new_status="closed"
            )
        )

        uow = UnitOfWork()
        cases = await view_legal_case(uow, company=_TEST_COMPANY_ID, case_number="011")
        assert cases[0].status == "closed"

    async def test_update_nonexistent_raises_error(self, engine) -> None:
        bus = _bootstrap()
        with pytest.raises(LegalCaseNotFound):
            await bus.handle(
                UpdateLegalCase(
                    company=_TEST_COMPANY_ID, case_number="999", new_client_name="Ghost"
                )
            )


class TestDeleteLegalCase:
    """Testes de integração para exclusão (soft delete) de processo jurídico."""

    async def test_delete_soft_deletes(self, engine) -> None:
        bus = _bootstrap()
        await bus.handle(_create_case_cmd("020", "Para Excluir"))

        bus2 = _bootstrap()
        await bus2.handle(DeleteLegalCase(company=_TEST_COMPANY_ID, case_number="020"))

        uow = UnitOfWork()
        cases = await view_legal_case(uow, company=_TEST_COMPANY_ID, case_number="020")
        assert cases == []

    async def test_deleted_visible_with_include_deleted(self, engine) -> None:
        bus = _bootstrap()
        await bus.handle(_create_case_cmd("021", "Soft Deleted"))

        bus2 = _bootstrap()
        await bus2.handle(DeleteLegalCase(company=_TEST_COMPANY_ID, case_number="021"))

        uow = UnitOfWork()
        cases = await view_legal_case(
            uow, company=_TEST_COMPANY_ID, case_number="021", include_deleted=True
        )
        assert len(cases) == 1
        assert cases[0].deleted_at is not None

    async def test_delete_nonexistent_raises_error(self, engine) -> None:
        bus = _bootstrap()
        with pytest.raises(LegalCaseNotFound):
            await bus.handle(DeleteLegalCase(company=_TEST_COMPANY_ID, case_number="999"))


class TestViewLegalCase:
    """Testes de integração para consulta de processos jurídicos."""

    async def test_view_all(self, engine) -> None:
        bus = _bootstrap()
        await bus.handle(_create_case_cmd("030", "Client A"))
        bus2 = _bootstrap()
        await bus2.handle(_create_case_cmd("031", "Client B"))

        uow = UnitOfWork()
        cases = await view_legal_case(uow, company=_TEST_COMPANY_ID)
        assert len(cases) == 2
        numbers = {c.case_number for c in cases}
        assert numbers == {"030", "031"}

    async def test_view_empty(self, engine) -> None:
        uow = UnitOfWork()
        cases = await view_legal_case(uow, company=_TEST_COMPANY_ID)
        assert cases == []

    async def test_view_excludes_deleted(self, engine) -> None:
        bus = _bootstrap()
        await bus.handle(_create_case_cmd("040", "Active"))
        bus2 = _bootstrap()
        await bus2.handle(_create_case_cmd("041", "Deleted"))

        bus3 = _bootstrap()
        await bus3.handle(DeleteLegalCase(company=_TEST_COMPANY_ID, case_number="041"))

        uow = UnitOfWork()
        cases = await view_legal_case(uow, company=_TEST_COMPANY_ID)
        assert len(cases) == 1
        assert cases[0].client_name == "Active"
