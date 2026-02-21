"""Testes unitários para os endpoints da API do shared_core."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import uuid7

from shared_core.entrypoints.schemas.security import Token


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
    user.street = "R"
    user.number = "1"
    user.zip_code = "12345"
    user.district = "D"
    user.city = "C"
    user.state = "S"
    user.country = "BR"
    user.admin = False
    user.active = True
    user.is_owner = False
    user.birth_date = None
    user.complement = None
    user.created_at = None
    user.created_by = None
    user.updated_at = None
    user.updated_by = None
    user.deleted_at = None
    user.deleted_by = None
    user._password_hash = "hashed"
    return user


# ─── Company API ───


class TestCompanyAPI:
    """Testes para os endpoints de Company."""

    @patch("shared_core.entrypoints.api.company.bootstrap")
    @patch("shared_core.entrypoints.api.company.current_user")
    async def test_post_company(self, mock_ctx, mock_bootstrap) -> None:
        """Verifica que POST /company cria uma empresa com sucesso."""
        from shared_core.entrypoints.api.company import post_company
        from shared_core.entrypoints.schemas.company import CreateCompanySchema

        mock_ctx.get.return_value = _make_mock_user()
        mock_bus = AsyncMock()
        mock_bus.handle = AsyncMock(return_value=_COMPANY_ID)
        mock_bootstrap.return_value = mock_bus

        body = CreateCompanySchema(
            legal_name="Teste",
            responsible_name="R",
            email="e@e.com",
            cpf="12345678901",
            password="pass",
            active=True,
        )

        result = await post_company(body)
        assert result == _COMPANY_ID

    @patch("shared_core.entrypoints.api.company.bootstrap")
    @patch("shared_core.entrypoints.api.company.current_user")
    async def test_put_company(self, mock_ctx, mock_bootstrap) -> None:
        """Verifica que PUT /company atualiza uma empresa com sucesso."""
        from shared_core.entrypoints.api.company import put_company
        from shared_core.entrypoints.schemas.company import UpdateCompanySchema

        mock_ctx.get.return_value = _make_mock_user()
        mock_bus = AsyncMock()
        mock_bootstrap.return_value = mock_bus

        body = UpdateCompanySchema(new_legal_name="New")
        await put_company("Old", body)
        mock_bus.handle.assert_awaited_once()

    @patch("shared_core.entrypoints.api.company.view_company", new_callable=AsyncMock)
    @patch("shared_core.entrypoints.api.company.UnitOfWork")
    @patch("shared_core.entrypoints.api.company.current_user")
    async def test_get_company(self, mock_ctx, MockUoW, mock_view) -> None:
        """Verifica que GET /company retorna lista de empresas."""
        from shared_core.entrypoints.api.company import get_company

        mock_ctx.get.return_value = _make_mock_user()
        mock_view.return_value = []

        result = await get_company()
        assert result == []

    @patch("shared_core.entrypoints.api.company.bootstrap")
    @patch("shared_core.entrypoints.api.company.current_user")
    async def test_delete_company(self, mock_ctx, mock_bootstrap) -> None:
        """Verifica que DELETE /company remove uma empresa com sucesso."""
        from shared_core.entrypoints.api.company import delete_company

        mock_ctx.get.return_value = _make_mock_user()
        mock_bus = AsyncMock()
        mock_bootstrap.return_value = mock_bus

        await delete_company("Test")
        mock_bus.handle.assert_awaited_once()


# ─── User API ───


class TestUserAPI:
    """Testes para os endpoints de User."""

    @patch("shared_core.entrypoints.api.user.bootstrap")
    @patch("shared_core.entrypoints.api.user.current_user")
    async def test_post_user(self, mock_ctx, mock_bootstrap) -> None:
        """Verifica que POST /user cria um usuário com sucesso."""
        from shared_core.entrypoints.api.user import post_user
        from shared_core.entrypoints.schemas.user import AddressSchema, CreateUserSchema

        mock_ctx.get.return_value = _make_mock_user()
        mock_bus = AsyncMock()
        mock_bus.handle = AsyncMock(return_value=_USER_ID)
        mock_bootstrap.return_value = mock_bus

        body = CreateUserSchema(
            email="new@test.com",
            password="pass",
            cpf="12345678901",
            name="New User",
            phone="11999",
            address=AddressSchema(
                street="R",
                number="1",
                zip_code="12345",
                district="D",
                city="C",
                state="S",
                country="BR",
            ),
        )

        result = await post_user(body)
        assert result == _USER_ID

    @patch("shared_core.entrypoints.api.user.bootstrap")
    @patch("shared_core.entrypoints.api.user.current_user")
    async def test_put_user(self, mock_ctx, mock_bootstrap) -> None:
        """Verifica que PUT /user atualiza um usuário com sucesso."""
        from shared_core.entrypoints.api.user import put_user
        from shared_core.entrypoints.schemas.user import UpdateUserSchema

        mock_ctx.get.return_value = _make_mock_user()
        mock_bus = AsyncMock()
        mock_bootstrap.return_value = mock_bus

        body = UpdateUserSchema(new_name="New Name")
        await put_user("old@test.com", body)
        mock_bus.handle.assert_awaited_once()

    @patch("shared_core.entrypoints.api.user.view_user", new_callable=AsyncMock)
    @patch("shared_core.entrypoints.api.user.UnitOfWork")
    @patch("shared_core.entrypoints.api.user.current_user")
    async def test_get_user(self, mock_ctx, MockUoW, mock_view) -> None:
        """Verifica que GET /user retorna lista de usuários."""
        from shared_core.entrypoints.api.user import get_user

        mock_ctx.get.return_value = _make_mock_user()
        mock_view.return_value = []

        result = await get_user()
        assert result == []

    @patch("shared_core.entrypoints.api.user.bootstrap")
    @patch("shared_core.entrypoints.api.user.current_user")
    async def test_delete_user(self, mock_ctx, mock_bootstrap) -> None:
        """Verifica que DELETE /user remove um usuário com sucesso."""
        from shared_core.entrypoints.api.user import delete_user

        mock_ctx.get.return_value = _make_mock_user()
        mock_bus = AsyncMock()
        mock_bootstrap.return_value = mock_bus

        await delete_user("test@test.com")
        mock_bus.handle.assert_awaited_once()


# ─── CreditCard API ───


class TestCreditCardAPI:
    """Testes para os endpoints de CreditCard."""

    @patch("shared_core.entrypoints.api.credit_card.bootstrap")
    @patch("shared_core.entrypoints.api.credit_card.current_user")
    async def test_post_credit_card(self, mock_ctx, mock_bootstrap) -> None:
        """Verifica que POST /credit_card cria um cartão de crédito com sucesso."""
        from shared_core.entrypoints.api.credit_card import post_credit_card
        from shared_core.entrypoints.schemas.credit_card import CreateCreditCardSchema

        mock_ctx.get.return_value = _make_mock_user()
        mock_bus = AsyncMock()
        mock_bus.handle = AsyncMock(return_value=uuid7.create())
        mock_bootstrap.return_value = mock_bus

        body = CreateCreditCardSchema(
            number="4111111111111111",
            expiry="12/30",
            cvv="123",
            cpf="12345678901",
            holder_name="Test",
        )

        result = await post_credit_card(body)
        assert result is not None

    @patch(
        "shared_core.entrypoints.api.credit_card.view_credit_cards",
        new_callable=AsyncMock,
    )
    @patch("shared_core.entrypoints.api.credit_card.UnitOfWork")
    @patch("shared_core.entrypoints.api.credit_card.current_user")
    async def test_get_credit_cards(self, mock_ctx, MockUoW, mock_view) -> None:
        """Verifica que GET /credit_card retorna lista de cartões."""
        from shared_core.entrypoints.api.credit_card import get_credit_cards

        mock_ctx.get.return_value = _make_mock_user()
        mock_view.return_value = []

        result = await get_credit_cards()
        assert result == []

    @patch("shared_core.entrypoints.api.credit_card.bootstrap")
    @patch("shared_core.entrypoints.api.credit_card.current_user")
    async def test_delete_credit_card(self, mock_ctx, mock_bootstrap) -> None:
        """Verifica que DELETE /credit_card remove um cartão com sucesso."""
        from shared_core.entrypoints.api.credit_card import delete_credit_card

        mock_ctx.get.return_value = _make_mock_user()
        mock_bus = AsyncMock()
        mock_bootstrap.return_value = mock_bus

        await delete_credit_card(uuid7.create())
        mock_bus.handle.assert_awaited_once()


# ─── Payment API ───


class TestPaymentAPI:
    """Testes para os endpoints de Payment."""

    @patch("shared_core.entrypoints.api.payment.bootstrap")
    @patch("shared_core.entrypoints.api.payment.current_user")
    async def test_post_payment(self, mock_ctx, mock_bootstrap) -> None:
        """Verifica que POST /payment cria um pagamento com sucesso."""
        from datetime import date

        from shared_core.entrypoints.api.payment import post_payment
        from shared_core.entrypoints.schemas.payment import CreatePaymentSchema

        mock_ctx.get.return_value = _make_mock_user()
        mock_bus = AsyncMock()
        mock_bus.handle = AsyncMock(return_value=uuid7.create())
        mock_bootstrap.return_value = mock_bus

        body = CreatePaymentSchema(
            company=_COMPANY_ID, amount=100.0, due_date=date(2026, 3, 1)
        )

        result = await post_payment(body)
        assert result is not None

    @patch("shared_core.entrypoints.api.payment.view_payments", new_callable=AsyncMock)
    @patch("shared_core.entrypoints.api.payment.UnitOfWork")
    @patch("shared_core.entrypoints.api.payment.current_user")
    async def test_get_payments(self, mock_ctx, MockUoW, mock_view) -> None:
        """Verifica que GET /payment retorna lista de pagamentos."""
        from shared_core.entrypoints.api.payment import get_payments

        mock_ctx.get.return_value = _make_mock_user()
        mock_view.return_value = []

        result = await get_payments()
        assert result == []

    @patch("shared_core.entrypoints.api.payment.view_payments", new_callable=AsyncMock)
    @patch("shared_core.entrypoints.api.payment.UnitOfWork")
    @patch("shared_core.entrypoints.api.payment.current_user")
    async def test_get_payments_with_company(self, mock_ctx, MockUoW, mock_view) -> None:
        """Verifica que GET /payment com filtro de company funciona."""
        from shared_core.entrypoints.api.payment import get_payments

        mock_ctx.get.return_value = _make_mock_user()
        mock_view.return_value = []

        result = await get_payments(company=_COMPANY_ID)
        assert result == []

    @patch("shared_core.entrypoints.api.payment.bootstrap")
    @patch("shared_core.entrypoints.api.payment.current_user")
    async def test_patch_payment_paid(self, mock_ctx, mock_bootstrap) -> None:
        """Verifica que PATCH /payment/paid marca pagamento como pago."""
        from shared_core.entrypoints.api.payment import patch_payment_paid

        mock_ctx.get.return_value = _make_mock_user()
        mock_bus = AsyncMock()
        mock_bootstrap.return_value = mock_bus

        await patch_payment_paid(uuid7.create())
        mock_bus.handle.assert_awaited_once()

    @patch("shared_core.entrypoints.api.payment.bootstrap")
    @patch("shared_core.entrypoints.api.payment.current_user")
    async def test_patch_payment_overdue(self, mock_ctx, mock_bootstrap) -> None:
        """Verifica que PATCH /payment/overdue marca pagamento como atrasado."""
        from shared_core.entrypoints.api.payment import patch_payment_overdue

        mock_ctx.get.return_value = _make_mock_user()
        mock_bus = AsyncMock()
        mock_bootstrap.return_value = mock_bus

        await patch_payment_overdue(uuid7.create())
        mock_bus.handle.assert_awaited_once()

    @patch("shared_core.entrypoints.api.payment.bootstrap")
    @patch("shared_core.entrypoints.api.payment.current_user")
    async def test_post_check_overdue(self, mock_ctx, mock_bootstrap) -> None:
        """Verifica que POST /payment/check-overdue retorna empresas com atraso."""
        from shared_core.entrypoints.api.payment import post_check_overdue

        mock_ctx.get.return_value = _make_mock_user()
        mock_bus = AsyncMock()
        mock_bus.handle = AsyncMock(return_value=[_COMPANY_ID])
        mock_bootstrap.return_value = mock_bus

        result = await post_check_overdue()
        assert result == [_COMPANY_ID]

    @patch("shared_core.entrypoints.api.payment.bootstrap")
    @patch("shared_core.entrypoints.api.payment.current_user")
    async def test_post_check_overdue_none_result(self, mock_ctx, mock_bootstrap) -> None:
        """Verifica que POST /payment/check-overdue retorna lista vazia se None."""
        from shared_core.entrypoints.api.payment import post_check_overdue

        mock_ctx.get.return_value = _make_mock_user()
        mock_bus = AsyncMock()
        mock_bus.handle = AsyncMock(return_value=None)
        mock_bootstrap.return_value = mock_bus

        result = await post_check_overdue()
        assert result == []


# ─── AuditLog API ───


class TestAuditLogAPI:
    """Testes para os endpoints de AuditLog."""

    @patch(
        "shared_core.entrypoints.api.audit_log.view_audit_log",
        new_callable=AsyncMock,
    )
    @patch("shared_core.entrypoints.api.audit_log.UnitOfWork")
    @patch("shared_core.entrypoints.api.audit_log.current_user")
    async def test_get_audit_logs(self, mock_ctx, MockUoW, mock_view) -> None:
        """Verifica que GET /audit_log retorna lista de logs."""
        from shared_core.entrypoints.api.audit_log import get_audit_logs

        mock_ctx.get.return_value = _make_mock_user()
        mock_view.return_value = []

        result = await get_audit_logs()
        assert result == []

    @patch(
        "shared_core.entrypoints.api.audit_log.view_audit_log",
        new_callable=AsyncMock,
    )
    @patch("shared_core.entrypoints.api.audit_log.UnitOfWork")
    @patch("shared_core.entrypoints.api.audit_log.current_user")
    async def test_get_audit_logs_with_filters(
        self, mock_ctx, MockUoW, mock_view
    ) -> None:
        """Verifica que GET /audit_log com filtros funciona."""
        from shared_core.domain.value_objects.enums import EntityType
        from shared_core.entrypoints.api.audit_log import get_audit_logs

        mock_ctx.get.return_value = _make_mock_user()
        mock_view.return_value = []

        result = await get_audit_logs(
            entity_type=EntityType.COMPANY, entity_id=_COMPANY_ID
        )
        assert result == []


# ─── Security API ───


class TestSecurityAPI:
    """Testes para os endpoints de Security."""

    @patch("shared_core.entrypoints.api.security.bootstrap")
    async def test_login_success(self, mock_bootstrap) -> None:
        """Verifica que POST /token retorna token com credenciais válidas."""
        from fastapi.security import OAuth2PasswordRequestForm

        from shared_core.entrypoints.api.security import login_for_access_token

        mock_bus = AsyncMock()
        mock_bus.handle = AsyncMock(
            return_value=Token(access_token="tok", token_type="bearer")
        )
        mock_bootstrap.return_value = mock_bus

        form = MagicMock(spec=OAuth2PasswordRequestForm)
        form.username = "user@test.com"
        form.password = "pass"

        result = await login_for_access_token(form)
        assert result.access_token == "tok"

    @patch("shared_core.entrypoints.api.security.bootstrap")
    async def test_login_failure(self, mock_bootstrap) -> None:
        """Verifica que POST /token levanta HTTPException com credenciais inválidas."""
        from fastapi import HTTPException
        from fastapi.security import OAuth2PasswordRequestForm

        from shared_core.entrypoints.api.security import login_for_access_token

        mock_bus = AsyncMock()
        mock_bus.handle = AsyncMock(return_value=None)
        mock_bootstrap.return_value = mock_bus

        form = MagicMock(spec=OAuth2PasswordRequestForm)
        form.username = "bad@test.com"
        form.password = "wrong"

        with pytest.raises(HTTPException) as exc_info:
            await login_for_access_token(form)
        assert exc_info.value.status_code == 400

    async def test_read_users_me(self) -> None:
        """Verifica que GET /users/me retorna o usuário atual."""
        from shared_core.entrypoints.api.security import read_users_me

        mock_user = _make_mock_user()
        result = await read_users_me(mock_user)
        assert result == mock_user
