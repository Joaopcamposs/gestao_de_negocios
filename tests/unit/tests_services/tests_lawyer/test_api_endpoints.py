"""Testes unitários para os endpoints da API do serviço Lawyer."""

from unittest.mock import AsyncMock, MagicMock, patch

import uuid7

_COMPANY_ID = uuid7.create()
_USER_ID = uuid7.create()


def _make_mock_user():
    """Cria um usuário mockado para testes de API."""
    user = MagicMock()
    user.id = _USER_ID
    user.company = _COMPANY_ID
    user.email = "test@test.com"
    user.cpf = "12345678901"
    user.name = "Test"
    user.phone = "11999"
    user.admin = False
    user.active = True
    user.is_owner = False
    return user


class TestLawyerLegalCaseAPI:
    """Testes para os endpoints de LegalCase do serviço Lawyer."""

    @patch("services.lawyer.entrypoints.api.legal_case.bootstrap_lawyer")
    @patch("services.lawyer.entrypoints.api.legal_case.current_user")
    async def test_post_legal_case(self, mock_ctx, mock_bootstrap) -> None:
        """Verifica que POST /legal_case cria um caso jurídico com sucesso."""
        from services.lawyer.entrypoints.api.legal_case import post_legal_case
        from services.lawyer.entrypoints.schemas.legal_case import (
            CreateLegalCaseSchema,
        )

        mock_ctx.get.return_value = _make_mock_user()
        mock_bus = AsyncMock()
        mock_bus.handle = AsyncMock(return_value=uuid7.create())
        mock_bootstrap.return_value = mock_bus

        body = CreateLegalCaseSchema(
            case_number="0001",
            client_name="Client",
        )

        result = await post_legal_case(body)
        assert result is not None

    @patch("services.lawyer.entrypoints.api.legal_case.bootstrap_lawyer")
    @patch("services.lawyer.entrypoints.api.legal_case.current_user")
    async def test_put_legal_case(self, mock_ctx, mock_bootstrap) -> None:
        """Verifica que PUT /legal_case atualiza um caso jurídico com sucesso."""
        from services.lawyer.entrypoints.api.legal_case import put_legal_case
        from services.lawyer.entrypoints.schemas.legal_case import (
            UpdateLegalCaseSchema,
        )

        mock_ctx.get.return_value = _make_mock_user()
        mock_bus = AsyncMock()
        mock_bootstrap.return_value = mock_bus

        body = UpdateLegalCaseSchema(new_client_name="New Client")
        await put_legal_case("0001", body)
        mock_bus.handle.assert_awaited_once()

    @patch(
        "services.lawyer.entrypoints.api.legal_case.view_legal_case",
        new_callable=AsyncMock,
    )
    @patch("services.lawyer.entrypoints.api.legal_case.UnitOfWork")
    @patch("services.lawyer.entrypoints.api.legal_case.current_user")
    async def test_get_legal_case(self, mock_ctx, MockUoW, mock_view) -> None:
        """Verifica que GET /legal_case retorna lista de casos jurídicos."""
        from services.lawyer.entrypoints.api.legal_case import get_legal_case

        mock_ctx.get.return_value = _make_mock_user()
        mock_view.return_value = []

        result = await get_legal_case()
        assert result == []

    @patch("services.lawyer.entrypoints.api.legal_case.bootstrap_lawyer")
    @patch("services.lawyer.entrypoints.api.legal_case.current_user")
    async def test_delete_legal_case(self, mock_ctx, mock_bootstrap) -> None:
        """Verifica que DELETE /legal_case remove um caso jurídico com sucesso."""
        from services.lawyer.entrypoints.api.legal_case import (
            delete_legal_case_endpoint,
        )

        mock_ctx.get.return_value = _make_mock_user()
        mock_bus = AsyncMock()
        mock_bootstrap.return_value = mock_bus

        await delete_legal_case_endpoint("0001")
        mock_bus.handle.assert_awaited_once()
