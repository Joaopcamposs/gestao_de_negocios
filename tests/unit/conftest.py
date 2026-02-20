"""Fixtures reutilizáveis para testes unitários com UoW mockado."""

from unittest.mock import AsyncMock, MagicMock, PropertyMock
from uuid import UUID

import pytest
import uuid7

from messagebus.entities import UserBase


def make_fake_user(
    company: UUID | None = None,
    user_id: UUID | None = None,
) -> UserBase:
    """Cria um UserBase fake para testes."""
    return UserBase(
        company=company or uuid7.create(),
        id=user_id or uuid7.create(),
        cpf="12345678901",
        email="test@test.com",
    )


class FakeUnitOfWork:
    """
    Mock do UnitOfWork que simula o padrão `async with uow(Domain.X) as uow`.

    Uso:
        uow = FakeUnitOfWork(domain_repo=mock_repo, view_repo=mock_view)
        await handler(command, uow)
    """

    def __init__(
        self,
        domain_repo=None,
        view_repo=None,
        user: UserBase | None = None,
    ):
        self._domain_repo = domain_repo or AsyncMock()
        self._view_repo = view_repo or AsyncMock()
        self.user = user or make_fake_user()
        self.committed = False
        self.rolled_back = False
        self._active_context = False

    def __call__(self, domain=None):
        """Simula uow(Domain.X)."""
        if domain:
            self._domain_repo_class = domain.value[0] if domain else None
            self._view_repo_class = domain.value[1] if domain else None
        return self

    async def __aenter__(self):
        self.committed = False
        self._active_context = True
        return self

    async def __aexit__(self, *args):
        self._active_context = False

    @property
    def domain_repo(self):
        return self._domain_repo

    @domain_repo.setter
    def domain_repo(self, value):
        self._domain_repo = value

    @property
    def view_repo(self):
        return self._view_repo

    @view_repo.setter
    def view_repo(self, value):
        self._view_repo = value

    @property
    def user_id(self) -> UUID | None:
        return self.user.id if self.user else None

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.rolled_back = True

    def collect_new_events(self):
        return iter([])


@pytest.fixture
def fake_user():
    """Fixture que retorna um UserBase fake."""
    return make_fake_user()


@pytest.fixture
def fake_uow():
    """Fixture que retorna um FakeUnitOfWork."""
    return FakeUnitOfWork()
