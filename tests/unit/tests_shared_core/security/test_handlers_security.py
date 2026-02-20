"""Testes unitários para os handlers de segurança e autenticação no shared_core.

Cobre authenticate_user, get_current_user e get_current_active_user.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import uuid7

from shared_core.domain.commands.security import AuthenticateUser
from shared_core.domain.excecoes import CredentialsException, UserInactiveException
from shared_core.services.handlers.security import (
    authenticate_user,
    get_current_active_user,
    get_current_user,
)
from tests.unit.conftest import FakeUnitOfWork


_COMPANY_ID = uuid7.create()
_USER_ID = uuid7.create()


def _make_mock_user(active=True, email="user@test.com", company=None):
    """Cria um usuário mockado para testes de segurança."""
    user = MagicMock()
    user.id = _USER_ID
    user.active = active
    user.email = email
    user.company = company or _COMPANY_ID
    user.email_encrypted = b"encrypted_email"
    user.verify_password = MagicMock(return_value=True)
    user.generate_token = MagicMock(
        return_value=MagicMock(access_token="test_token", token_type="bearer")
    )
    return user


class TestAuthenticateUser:
    """Testes para o handler authenticate_user."""

    async def test_authenticate_success_no_alert(self) -> None:
        """Verifica autenticação bem-sucedida sem alerta de pagamento."""
        mock_user = _make_mock_user()
        mock_view_repo = AsyncMock()
        mock_view_repo.get_public_user_by_email = AsyncMock(return_value=mock_user)

        mock_company = MagicMock()
        mock_company.id = str(_COMPANY_ID)
        mock_company.payment_up_to_date = True

        mock_company_view_repo = AsyncMock()
        mock_company_view_repo.get_all = AsyncMock(return_value=[mock_company])

        call_count = 0

        class DualUow(FakeUnitOfWork):
            """UoW fake que alterna entre repositórios de usuário e empresa."""

            def __call__(self, domain=None):
                """Alterna o repositório de view conforme a chamada."""
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    self._view_repo = mock_view_repo
                else:
                    self._view_repo = mock_company_view_repo
                return self

        uow = DualUow()
        command = AuthenticateUser(email="user@test.com", password="pass123")

        result = await authenticate_user(command, uow)

        assert result is not None
        assert result.access_token == "test_token"
        assert result.payment_alert is None

    async def test_authenticate_user_not_found(self) -> None:
        """Verifica que autenticação retorna None quando usuário não existe."""
        mock_view_repo = AsyncMock()
        mock_view_repo.get_public_user_by_email = AsyncMock(return_value=None)

        uow = FakeUnitOfWork(view_repo=mock_view_repo)
        command = AuthenticateUser(email="unknown@test.com", password="pass")

        result = await authenticate_user(command, uow)
        assert result is None

    async def test_authenticate_user_inactive(self) -> None:
        """Verifica que usuário inativo levanta UserInactiveException."""
        mock_user = _make_mock_user(active=False)
        mock_view_repo = AsyncMock()
        mock_view_repo.get_public_user_by_email = AsyncMock(return_value=mock_user)

        uow = FakeUnitOfWork(view_repo=mock_view_repo)
        command = AuthenticateUser(email="user@test.com", password="pass")

        with pytest.raises(UserInactiveException):
            await authenticate_user(command, uow)

    async def test_authenticate_wrong_password(self) -> None:
        """Verifica que senha incorreta retorna None."""
        mock_user = _make_mock_user()
        mock_user.verify_password = MagicMock(return_value=False)
        mock_view_repo = AsyncMock()
        mock_view_repo.get_public_user_by_email = AsyncMock(return_value=mock_user)

        uow = FakeUnitOfWork(view_repo=mock_view_repo)
        command = AuthenticateUser(email="user@test.com", password="wrong")

        result = await authenticate_user(command, uow)
        assert result is None

    async def test_authenticate_with_payment_alert(self) -> None:
        """Verifica que autenticação retorna alerta quando pagamento está em atraso."""
        mock_user = _make_mock_user()
        mock_view_repo = AsyncMock()
        mock_view_repo.get_public_user_by_email = AsyncMock(return_value=mock_user)

        mock_company = MagicMock()
        mock_company.id = str(_COMPANY_ID)
        mock_company.payment_up_to_date = False

        mock_company_view_repo = AsyncMock()
        mock_company_view_repo.get_all = AsyncMock(return_value=[mock_company])

        call_count = 0

        class DualUow(FakeUnitOfWork):
            """UoW fake que alterna entre repositórios de usuário e empresa."""

            def __call__(self, domain=None):
                """Alterna o repositório de view conforme a chamada."""
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    self._view_repo = mock_view_repo
                else:
                    self._view_repo = mock_company_view_repo
                return self

        uow = DualUow()
        command = AuthenticateUser(email="user@test.com", password="pass123")

        result = await authenticate_user(command, uow)

        assert result is not None
        assert result.payment_alert is not None
        assert "atraso" in result.payment_alert


class TestGetCurrentUser:
    """Testes para o handler get_current_user."""

    async def test_get_current_user_success(self) -> None:
        """Verifica que get_current_user retorna o usuário com token válido."""
        import jwt

        from shared_core.consts import ALGORITHM, SECRET_KEY

        token = jwt.encode(
            {"email": "user@test.com", "id_empresa": str(_COMPANY_ID)},
            SECRET_KEY,
            algorithm=ALGORITHM,
        )

        mock_user = _make_mock_user()
        mock_view_repo = AsyncMock()
        mock_view_repo.get_by_email = AsyncMock(return_value=mock_user)

        with patch("shared_core.services.handlers.security.UnitOfWork") as MockUoW:
            mock_uow_instance = FakeUnitOfWork(view_repo=mock_view_repo)
            MockUoW.return_value = mock_uow_instance

            result = await get_current_user(token)

        assert result == mock_user

    async def test_get_current_user_invalid_token(self) -> None:
        """Verifica que token inválido levanta CredentialsException."""
        with pytest.raises(CredentialsException):
            await get_current_user("invalid_token")

    async def test_get_current_user_no_email_in_token(self) -> None:
        """Verifica que token sem campo email levanta CredentialsException."""
        import jwt

        from shared_core.consts import ALGORITHM, SECRET_KEY

        token = jwt.encode(
            {"id_empresa": str(_COMPANY_ID)},
            SECRET_KEY,
            algorithm=ALGORITHM,
        )

        with pytest.raises(CredentialsException):
            await get_current_user(token)

    async def test_get_current_user_user_not_found(self) -> None:
        """Verifica que usuário não encontrado levanta CredentialsException."""
        import jwt

        from shared_core.consts import ALGORITHM, SECRET_KEY

        token = jwt.encode(
            {"email": "nobody@test.com", "id_empresa": str(_COMPANY_ID)},
            SECRET_KEY,
            algorithm=ALGORITHM,
        )

        mock_view_repo = AsyncMock()
        mock_view_repo.get_by_email = AsyncMock(return_value=None)

        with patch("shared_core.services.handlers.security.UnitOfWork") as MockUoW:
            mock_uow_instance = FakeUnitOfWork(view_repo=mock_view_repo)
            MockUoW.return_value = mock_uow_instance

            with pytest.raises(CredentialsException):
                await get_current_user(token)


class TestGetCurrentActiveUser:
    """Testes para o handler get_current_active_user."""

    async def test_active_user(self) -> None:
        """Verifica que usuário ativo é retornado corretamente."""
        mock_user = _make_mock_user(active=True)
        result = await get_current_active_user(mock_user)
        assert result == mock_user

    async def test_inactive_user(self) -> None:
        """Verifica que usuário inativo levanta UserInactiveException."""
        mock_user = _make_mock_user(active=False)
        with pytest.raises(UserInactiveException):
            await get_current_active_user(mock_user)
