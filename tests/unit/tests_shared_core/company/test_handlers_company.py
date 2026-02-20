"""Testes unitários para os handlers de Company no shared_core.

Cobre create_company, update_company, delete_company e handlers de eventos.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import uuid7

from shared_core.domain.commands.company import (
    CreateCompany,
    DeleteCompany,
    UpdateCompany,
)
from shared_core.domain.events.company import (
    CompanyCreated,
    CompanyDeleted,
    CompanyUpdated,
)
from shared_core.services.handlers.company import (
    company_created,
    company_deleted,
    company_updated,
    create_company,
    delete_company,
    update_company,
)
from tests.unit.conftest import FakeUnitOfWork


_COMPANY_ID = uuid7.create()


class TestCreateCompany:
    """Testes para o handler create_company."""

    async def test_create_company_success(self) -> None:
        """Verifica que create_company cria a empresa e retorna o ID."""
        mock_repo = AsyncMock()
        mock_company = MagicMock()
        mock_company.id = _COMPANY_ID
        mock_repo.create_aggregate = AsyncMock(return_value=mock_company)

        uow = FakeUnitOfWork(domain_repo=mock_repo)

        command = CreateCompany(
            legal_name="Empresa X",
            trade_name="X",
            responsible_name="João",
            email="joao@empresa.com",
            cpf="12345678901",
            cnpj="12345678000100",
            password="senha123",
            active=True,
        )

        result = await create_company(command, uow)

        assert result == _COMPANY_ID
        mock_repo.create_aggregate.assert_awaited_once()
        mock_company.create.assert_called_once()
        mock_repo.add.assert_awaited_once_with(mock_company)

    async def test_create_company_error_deletes_schema(self) -> None:
        """Verifica que erro durante criação remove o schema."""
        mock_repo = AsyncMock()
        mock_repo.create_aggregate = AsyncMock(side_effect=RuntimeError("DB error"))

        uow = FakeUnitOfWork(domain_repo=mock_repo)

        command = CreateCompany(
            legal_name="Empresa Falha",
            trade_name=None,
            responsible_name="Maria",
            email="maria@test.com",
            cpf="98765432100",
            password="senha123",
            active=True,
        )

        with patch(
            "shared_core.services.handlers.company.delete_schema", new_callable=AsyncMock
        ) as mock_del:
            with pytest.raises(RuntimeError, match="DB error"):
                await create_company(command, uow)
            mock_del.assert_awaited_once_with("Empresa Falha")


class TestUpdateCompany:
    """Testes para o handler update_company."""

    async def test_update_company(self) -> None:
        """Verifica que update_company atualiza a empresa corretamente."""
        mock_repo = AsyncMock()
        mock_company = MagicMock()
        mock_repo.get_by_legal_name = AsyncMock(return_value=mock_company)

        uow = FakeUnitOfWork(domain_repo=mock_repo)

        command = UpdateCompany(
            legal_name="Empresa X",
            new_legal_name="Empresa Y",
            new_trade_name="Y",
            new_responsible_name="Carlos",
            new_email="carlos@test.com",
            new_active=True,
        )

        await update_company(command, uow)

        mock_repo.get_by_legal_name.assert_awaited_once_with(legal_name="Empresa X")
        mock_company.update.assert_called_once()
        mock_repo.add.assert_awaited_once_with(mock_company)


class TestDeleteCompany:
    """Testes para o handler delete_company."""

    async def test_delete_company(self) -> None:
        """Verifica que delete_company remove a empresa corretamente."""
        mock_repo = AsyncMock()
        mock_company = MagicMock()
        mock_repo.get_by_legal_name = AsyncMock(return_value=mock_company)

        uow = FakeUnitOfWork(domain_repo=mock_repo)

        command = DeleteCompany(legal_name="Empresa X")

        await delete_company(command, uow)

        mock_repo.get_by_legal_name.assert_awaited_once_with(legal_name="Empresa X")
        mock_company.delete.assert_called_once()
        mock_repo.remove.assert_awaited_once_with(mock_company)


class TestCompanyEventHandlers:
    """Testes para os handlers de eventos de Company."""

    async def test_company_created(self) -> None:
        """Verifica que company_created é executado sem erros."""
        event = CompanyCreated(id=_COMPANY_ID)
        uow = FakeUnitOfWork()
        await company_created(event, uow)

    async def test_company_updated(self) -> None:
        """Verifica que company_updated é executado sem erros."""
        event = CompanyUpdated(id=_COMPANY_ID)
        uow = FakeUnitOfWork()
        await company_updated(event, uow)

    async def test_company_deleted(self) -> None:
        """Verifica que company_deleted é executado sem erros."""
        event = CompanyDeleted(id=_COMPANY_ID)
        uow = FakeUnitOfWork()
        await company_deleted(event, uow)
