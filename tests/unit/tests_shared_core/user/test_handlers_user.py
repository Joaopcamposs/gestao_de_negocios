"""Testes unitários para os handlers de User no shared_core.

Cobre create_user, update_user, delete_user, handlers de eventos e usuários públicos.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
import uuid7

from shared_core.domain.commands.user import CreateUser, DeleteUser, UpdateUser
from shared_core.domain.events.user import (
    TimeToCreateCompanyAdminUser,
    TimeToCreateInitialCompanyUser,
    UserCreated,
    UserDeleted,
    UserUpdated,
)
from shared_core.domain.value_objects.address import Address
from shared_core.services.handlers.user import (
    create_public_user,
    create_user,
    delete_user,
    remove_public_user,
    update_public_user,
    update_user,
    user_created,
    user_deleted,
    user_updated,
)
from tests.unit.conftest import FakeUnitOfWork


_COMPANY_ID = uuid7.create()
_USER_ID = uuid7.create()
_ADDRESS = Address(
    street="Rua A",
    number="100",
    zip_code="12345000",
    district="Centro",
    city="SP",
    state="SP",
    country="BR",
)


class TestCreateUser:
    """Testes para o handler create_user."""

    async def test_create_user_with_command(self) -> None:
        """Verifica que create_user cria o usuário e retorna o ID."""
        mock_repo = AsyncMock()
        mock_user = MagicMock()
        mock_user.id = _USER_ID
        mock_repo.create_aggregate = AsyncMock(return_value=mock_user)

        uow = FakeUnitOfWork(domain_repo=mock_repo)

        command = CreateUser(
            company=_COMPANY_ID,
            email="test@test.com",
            cpf="12345678901",
            password="pass123",
            name="Test User",
            phone="11999999999",
            address=_ADDRESS,
            active=True,
            admin=False,
        )

        result = await create_user(command, uow)

        assert result == _USER_ID
        mock_repo.create_aggregate.assert_awaited_once()
        mock_user.create.assert_called_once()
        mock_repo.add.assert_awaited_once_with(mock_user)

    async def test_create_user_with_initial_company_event(self) -> None:
        """Verifica que create_user aceita evento TimeToCreateInitialCompanyUser."""
        mock_repo = AsyncMock()
        mock_user = MagicMock()
        mock_user.id = _USER_ID
        mock_repo.create_aggregate = AsyncMock(return_value=mock_user)

        uow = FakeUnitOfWork(domain_repo=mock_repo)

        event = TimeToCreateInitialCompanyUser(
            company=_COMPANY_ID,
            email="init@company.com",
            cpf="12345678901",
            password="pass123",
            name="Owner",
            phone="11999999999",
            active=True,
            admin=True,
        )

        result = await create_user(event, uow)
        assert result == _USER_ID

    async def test_create_user_with_admin_event(self) -> None:
        """Verifica que create_user aceita evento TimeToCreateCompanyAdminUser."""
        mock_repo = AsyncMock()
        mock_user = MagicMock()
        mock_user.id = _USER_ID
        mock_repo.create_aggregate = AsyncMock(return_value=mock_user)

        uow = FakeUnitOfWork(domain_repo=mock_repo)

        event = TimeToCreateCompanyAdminUser(
            company=_COMPANY_ID,
            email="admin@company.com",
        )

        result = await create_user(event, uow)
        assert result == _USER_ID


class TestUpdateUser:
    """Testes para o handler update_user."""

    async def test_update_user(self) -> None:
        """Verifica que update_user atualiza o usuário corretamente."""
        mock_repo = AsyncMock()
        mock_user = MagicMock()
        mock_repo.get_by_email = AsyncMock(return_value=mock_user)

        uow = FakeUnitOfWork(domain_repo=mock_repo)

        command = UpdateUser(
            email="old@test.com",
            new_email="new@test.com",
            new_name="New Name",
        )

        await update_user(command, uow)

        mock_repo.get_by_email.assert_awaited_once_with(email="old@test.com")
        mock_user.update.assert_called_once()
        mock_repo.add.assert_awaited_once_with(mock_user)


class TestDeleteUser:
    """Testes para o handler delete_user."""

    async def test_delete_user(self) -> None:
        """Verifica que delete_user remove o usuário corretamente."""
        mock_repo = AsyncMock()
        mock_user = MagicMock()
        mock_repo.get_by_email = AsyncMock(return_value=mock_user)

        uow = FakeUnitOfWork(domain_repo=mock_repo)

        command = DeleteUser(email="test@test.com")

        await delete_user(command, uow)

        mock_repo.get_by_email.assert_awaited_once_with(email="test@test.com")
        mock_user.delete.assert_called_once()
        mock_repo.remove.assert_awaited_once_with(mock_user)


class TestUserEventHandlers:
    """Testes para os handlers de eventos de User."""

    async def test_user_created(self) -> None:
        """Verifica que user_created é executado sem erros."""
        event = UserCreated(id=_USER_ID, company=_COMPANY_ID)
        uow = FakeUnitOfWork()
        await user_created(event, uow)

    async def test_user_updated(self) -> None:
        """Verifica que user_updated é executado sem erros."""
        event = UserUpdated(id=_USER_ID, company=_COMPANY_ID)
        uow = FakeUnitOfWork()
        await user_updated(event, uow)

    async def test_user_deleted(self) -> None:
        """Verifica que user_deleted é executado sem erros."""
        event = UserDeleted(id=_USER_ID, company=_COMPANY_ID)
        uow = FakeUnitOfWork()
        await user_deleted(event, uow)


class TestCreatePublicUser:
    """Testes para o handler create_public_user."""

    async def test_create_public_user(self) -> None:
        """Verifica que create_public_user cria o usuário público corretamente."""
        mock_repo = AsyncMock()
        mock_view = AsyncMock()

        mock_user = MagicMock()
        mock_user.id = _USER_ID
        mock_user.company = _COMPANY_ID
        mock_user.email = "test@test.com"
        mock_user.password_hash = "hashed"
        mock_user.active = True
        mock_view.get_by_id = AsyncMock(return_value=mock_user)

        uow = FakeUnitOfWork(domain_repo=mock_repo, view_repo=mock_view)

        event = UserCreated(id=_USER_ID, company=_COMPANY_ID)

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(
                "shared_core.domain.aggregate.user.PublicUser.encrypt_email",
                staticmethod(lambda e: b"encrypted"),
            )
            mp.setattr(
                "shared_core.domain.aggregate.user.PublicUser.hash_email",
                staticmethod(lambda e: "hashed"),
            )

            result = await create_public_user(event, uow)

        assert result is not None
        mock_repo.add_public_user.assert_awaited_once()


class TestUpdatePublicUser:
    """Testes para o handler update_public_user."""

    async def test_update_public_user(self) -> None:
        """Verifica que update_public_user atualiza o usuário público corretamente."""
        mock_repo = AsyncMock()
        mock_view = AsyncMock()

        mock_private_user = MagicMock()
        mock_private_user.email = "new@test.com"
        mock_private_user.password_hash = "new_hash"
        mock_private_user.active = True
        mock_view.get_by_id = AsyncMock(return_value=mock_private_user)

        mock_public_user = MagicMock()
        mock_repo.get_public_user_by_id = AsyncMock(return_value=mock_public_user)

        uow = FakeUnitOfWork(domain_repo=mock_repo, view_repo=mock_view)

        event = UserUpdated(id=_USER_ID, company=_COMPANY_ID)

        await update_public_user(event, uow)

        mock_public_user.update.assert_called_once_with(
            email="new@test.com",
            password="new_hash",
            active=True,
        )
        mock_repo.add_public_user.assert_awaited_once()


class TestRemovePublicUser:
    """Testes para o handler remove_public_user."""

    async def test_remove_public_user(self) -> None:
        """Verifica que remove_public_user remove o usuário público corretamente."""
        mock_repo = AsyncMock()
        mock_public_user = MagicMock()
        mock_repo.get_public_user_by_id = AsyncMock(return_value=mock_public_user)

        uow = FakeUnitOfWork(domain_repo=mock_repo)

        event = UserDeleted(id=_USER_ID, company=_COMPANY_ID)

        await remove_public_user(event, uow)

        mock_public_user.remove.assert_called_once()
        mock_repo.remove_public_user.assert_awaited_once()
