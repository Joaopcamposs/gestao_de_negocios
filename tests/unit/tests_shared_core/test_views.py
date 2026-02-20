"""Testes unitários para as views de consulta do shared_core.

Cobre view_company, view_user, view_credit_cards, view_payments e view_audit_log.
"""

from unittest.mock import AsyncMock, MagicMock

import uuid7

from shared_core.adapters.views.audit_log import view_audit_log
from shared_core.adapters.views.company import view_company
from shared_core.adapters.views.credit_card import view_credit_cards
from shared_core.adapters.views.payment import view_payments
from shared_core.adapters.views.user import view_user
from tests.unit.conftest import FakeUnitOfWork


_COMPANY_ID = uuid7.create()
_USER_ID = uuid7.create()


class TestViewCompany:
    """Testes para a view view_company."""

    async def test_view_company_by_legal_name_found(self) -> None:
        """Verifica que view_company retorna empresa quando encontrada por nome."""
        mock_company = MagicMock()
        mock_view = AsyncMock()
        mock_view.get_by_legal_name = AsyncMock(return_value=mock_company)

        uow = FakeUnitOfWork(view_repo=mock_view)

        result = await view_company(uow, legal_name="Empresa X")

        assert result == [mock_company]

    async def test_view_company_by_legal_name_not_found(self) -> None:
        """Verifica que view_company retorna lista vazia quando empresa não existe."""
        mock_view = AsyncMock()
        mock_view.get_by_legal_name = AsyncMock(return_value=None)

        uow = FakeUnitOfWork(view_repo=mock_view)

        result = await view_company(uow, legal_name="Inexistente")

        assert result == []

    async def test_view_company_all(self) -> None:
        """Verifica que view_company retorna todas as empresas."""
        companies = [MagicMock(), MagicMock()]
        mock_view = AsyncMock()
        mock_view.get_all = AsyncMock(return_value=companies)

        uow = FakeUnitOfWork(view_repo=mock_view)

        result = await view_company(uow)

        assert result == companies

    async def test_view_company_include_deleted(self) -> None:
        """Verifica que view_company passa include_deleted corretamente."""
        mock_view = AsyncMock()
        mock_view.get_all = AsyncMock(return_value=[])

        uow = FakeUnitOfWork(view_repo=mock_view)

        await view_company(uow, include_deleted=True)
        mock_view.get_all.assert_awaited_once_with(include_deleted=True)


class TestViewUser:
    """Testes para a view view_user."""

    async def test_view_user_by_email_found(self) -> None:
        """Verifica que view_user retorna usuário quando encontrado por email."""
        mock_user = MagicMock()
        mock_view = AsyncMock()
        mock_view.get_by_email = AsyncMock(return_value=mock_user)

        uow = FakeUnitOfWork(view_repo=mock_view)

        result = await view_user(uow, email="test@test.com")

        assert result == [mock_user]

    async def test_view_user_by_email_not_found(self) -> None:
        """Verifica que view_user retorna lista vazia quando usuário não existe."""
        mock_view = AsyncMock()
        mock_view.get_by_email = AsyncMock(return_value=None)

        uow = FakeUnitOfWork(view_repo=mock_view)

        result = await view_user(uow, email="unknown@test.com")

        assert result == []

    async def test_view_user_all(self) -> None:
        """Verifica que view_user retorna todos os usuários."""
        users = [MagicMock()]
        mock_view = AsyncMock()
        mock_view.get_all = AsyncMock(return_value=users)

        uow = FakeUnitOfWork(view_repo=mock_view)

        result = await view_user(uow)
        assert result == users


class TestViewCreditCards:
    """Testes para a view view_credit_cards."""

    async def test_view_credit_cards_with_cards(self) -> None:
        """Verifica que view_credit_cards retorna cartões descriptografados."""
        mock_card = MagicMock()
        mock_card.id = uuid7.create()
        mock_card.user_id = _USER_ID
        mock_card.card_key_encrypted = b"key"
        mock_card.active = True
        mock_card.created_at = None
        mock_card.created_by = None
        mock_card.updated_at = None
        mock_card.updated_by = None
        mock_card.deleted_at = None
        mock_card.deleted_by = None
        mock_card.decrypt_fields = MagicMock(
            return_value={
                "number": "4111111111111111",
                "expiry": "12/30",
                "cvv": "123",
                "cpf": "12345678901",
                "holder_name": "Test",
            }
        )

        mock_view = AsyncMock()
        mock_view.get_all_by_user = AsyncMock(return_value=[mock_card])

        uow = FakeUnitOfWork(view_repo=mock_view)

        result = await view_credit_cards(uow, user_id=_USER_ID)

        assert len(result) == 1
        assert result[0].number == "4111111111111111"

    async def test_view_credit_cards_empty(self) -> None:
        """Verifica que view_credit_cards retorna lista vazia quando não há cartões."""
        mock_view = AsyncMock()
        mock_view.get_all_by_user = AsyncMock(return_value=[])

        uow = FakeUnitOfWork(view_repo=mock_view)

        result = await view_credit_cards(uow, user_id=_USER_ID)
        assert result == []


class TestViewPayments:
    """Testes para a view view_payments."""

    async def test_view_payments(self) -> None:
        """Verifica que view_payments retorna pagamentos da empresa."""
        payments = [MagicMock()]
        mock_view = AsyncMock()
        mock_view.get_all_by_company = AsyncMock(return_value=payments)

        uow = FakeUnitOfWork(view_repo=mock_view)

        result = await view_payments(uow, company=_COMPANY_ID)
        assert result == payments


class TestViewAuditLog:
    """Testes para a view view_audit_log."""

    async def test_view_audit_log_by_entity(self) -> None:
        """Verifica que view_audit_log retorna logs por tipo e ID de entidade."""
        logs = [MagicMock()]
        mock_view = AsyncMock()
        mock_view.get_by_entity = AsyncMock(return_value=logs)

        uow = FakeUnitOfWork(view_repo=mock_view)

        result = await view_audit_log(uow, entity_type="Company", entity_id=_COMPANY_ID)
        assert result == logs

    async def test_view_audit_log_by_type_only(self) -> None:
        """Verifica que view_audit_log retorna logs apenas por tipo de entidade."""
        logs = [MagicMock()]
        mock_view = AsyncMock()
        mock_view.get_by_entity_type = AsyncMock(return_value=logs)

        uow = FakeUnitOfWork(view_repo=mock_view)

        result = await view_audit_log(uow, entity_type="Company")
        assert result == logs

    async def test_view_audit_log_all(self) -> None:
        """Verifica que view_audit_log retorna todos os logs quando sem filtros."""
        logs = [MagicMock(), MagicMock()]
        mock_view = AsyncMock()
        mock_view.get_all = AsyncMock(return_value=logs)

        uow = FakeUnitOfWork(view_repo=mock_view)

        result = await view_audit_log(uow)
        assert result == logs
