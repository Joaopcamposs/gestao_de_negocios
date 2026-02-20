"""Testes unitários para os repositórios concretos de User (domain + view)."""

from unittest.mock import AsyncMock, MagicMock

import pytest
import uuid7

from shared_core.domain.aggregate.user import User
from shared_core.domain.excecoes import UserNotFound
from shared_core.domain.value_objects.address import Address


_COMPANY_ID = uuid7.create()
_USER_ID = uuid7.create()


def _make_session():
    """Cria uma sessão SQLAlchemy mockada com async context manager."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    return session


def _make_mock_user_row():
    """Cria uma linha de resultado mockada representando um User."""
    u = MagicMock()
    u.id = _USER_ID
    u.company = _COMPANY_ID
    u.email = "u@t.com"
    u.cpf = "12345678901"
    u.name = "T"
    u.phone = "11"
    u.street = "R"
    u.number = "1"
    u.zip_code = "12345"
    u.district = "D"
    u.city = "C"
    u.state = "S"
    u.country = "BR"
    u.complement = None
    u.admin = False
    u.active = True
    u.is_owner = False
    u.birth_date = None
    u.password_hash = "hashed"
    u.created_at = None
    u.created_by = None
    u.updated_at = None
    u.updated_by = None
    u.deleted_at = None
    u.deleted_by = None
    return u


# ─── UserDomainRepo ───


class TestUserDomainRepoConcrete:
    """Testes para o repositório de domínio concreto de User."""

    async def test_create_aggregate(self) -> None:
        """Verifica que create_aggregate cria um usuário com sucesso."""
        from shared_core.adapters.repository.domain_repo.user import UserDomainRepo

        session = _make_session()
        r = MagicMock()
        r.scalar_one_or_none.return_value = None
        session.execute.return_value = r

        repo = UserDomainRepo(session=session)

        user = await repo.create_aggregate(
            company=_COMPANY_ID,
            email="new@t.com",
            cpf="12345678901",
            password="pass",
            name="New",
            phone="11",
            address=Address(
                street="R",
                number="1",
                zip_code="12345",
                district="D",
                city="C",
                state="S",
                country="BR",
            ),
        )
        assert user.email == "new@t.com"

    async def test_get_by_email_found(self) -> None:
        """Verifica que get_by_email retorna o usuário quando encontrado."""
        from shared_core.adapters.repository.domain_repo.user import UserDomainRepo

        session = _make_session()
        mock_u = _make_mock_user_row()
        r = MagicMock()
        r.scalar_one_or_none.return_value = mock_u
        session.execute.return_value = r

        repo = UserDomainRepo(session=session)
        user = await repo.get_by_email("u@t.com")
        assert user.email == "u@t.com"

    async def test_get_by_email_not_found(self) -> None:
        """Verifica que get_by_email levanta UserNotFound quando não encontrado."""
        from shared_core.adapters.repository.domain_repo.user import UserDomainRepo

        session = _make_session()
        r = MagicMock()
        r.scalar_one_or_none.return_value = None
        session.execute.return_value = r

        repo = UserDomainRepo(session=session)
        with pytest.raises(UserNotFound):
            await repo.get_by_email("nope@t.com")

    async def test_get_all_by_company(self) -> None:
        """Verifica que get_all_by_company retorna usuários da empresa."""
        from shared_core.adapters.repository.domain_repo.user import UserDomainRepo

        session = _make_session()
        mock_u = _make_mock_user_row()
        sr = MagicMock()
        sr.all.return_value = [mock_u]
        r = MagicMock()
        r.scalars.return_value = sr
        session.execute.return_value = r

        repo = UserDomainRepo(session=session)
        result = await repo.get_all_by_company(_COMPANY_ID)
        assert len(result) == 1

    async def test_get_by_id_found(self) -> None:
        """Verifica que get_by_id retorna o usuário quando encontrado."""
        from shared_core.adapters.repository.domain_repo.user import UserDomainRepo

        session = _make_session()
        mock_u = _make_mock_user_row()
        r = MagicMock()
        r.scalar_one_or_none.return_value = mock_u
        session.execute.return_value = r

        repo = UserDomainRepo(session=session)
        result = await repo.get_by_id(_USER_ID)
        assert result.email == "u@t.com"

    async def test_get_by_id_not_found(self) -> None:
        """Verifica que get_by_id levanta UserNotFound quando não encontrado."""
        from shared_core.adapters.repository.domain_repo.user import UserDomainRepo

        session = _make_session()
        r = MagicMock()
        r.scalar_one_or_none.return_value = None
        session.execute.return_value = r

        repo = UserDomainRepo(session=session)
        with pytest.raises(UserNotFound):
            await repo.get_by_id(_USER_ID)

    async def test_add_and_remove(self) -> None:
        """Verifica que _add e _remove executam operações na sessão."""
        from shared_core.adapters.repository.domain_repo.user import UserDomainRepo

        session = _make_session()
        repo = UserDomainRepo(session=session)

        user = User.create_aggregate(
            company=_COMPANY_ID,
            email="t@t.com",
            cpf="12345678901",
            password="p",
            name="T",
            phone="1",
            address=Address(
                street="R",
                number="1",
                zip_code="12345",
                district="D",
                city="C",
                state="S",
                country="BR",
            ),
        )
        user.create(_USER_ID)
        await repo._add(user)
        session.execute.assert_awaited()

        session.reset_mock()
        user.delete(_USER_ID)
        await repo._remove(user)
        session.execute.assert_awaited()


# ─── UserViewRepo ───


class TestUserViewRepo:
    """Testes para o repositório de view concreto de User."""

    async def test_get_by_email_found(self) -> None:
        """Verifica que get_by_email retorna o usuário quando encontrado."""
        from shared_core.adapters.repository.view_repo.user import UserViewRepo

        session = _make_session()
        mock_u = _make_mock_user_row()
        r = MagicMock()
        r.scalar_one_or_none.return_value = mock_u
        session.execute.return_value = r

        repo = UserViewRepo(session=session)
        result = await repo.get_by_email("u@t.com")
        assert result is not None

    async def test_get_by_email_not_found(self) -> None:
        """Verifica que get_by_email retorna None quando não encontrado."""
        from shared_core.adapters.repository.view_repo.user import UserViewRepo

        session = _make_session()
        r = MagicMock()
        r.scalar_one_or_none.return_value = None
        session.execute.return_value = r

        repo = UserViewRepo(session=session)
        result = await repo.get_by_email("nope@t.com")
        assert result is None

    async def test_get_all(self) -> None:
        """Verifica que get_all retorna todos os usuários."""
        from shared_core.adapters.repository.view_repo.user import UserViewRepo

        session = _make_session()
        mock_u = _make_mock_user_row()
        sr = MagicMock()
        sr.all.return_value = [mock_u]
        r = MagicMock()
        r.scalars.return_value = sr
        session.execute.return_value = r

        repo = UserViewRepo(session=session)
        result = await repo.get_all()
        assert len(result) == 1

    async def test_get_by_id_found(self) -> None:
        """Verifica que get_by_id retorna o usuário quando encontrado."""
        from shared_core.adapters.repository.view_repo.user import UserViewRepo

        session = _make_session()
        mock_u = _make_mock_user_row()
        r = MagicMock()
        r.scalar_one_or_none.return_value = mock_u
        session.execute.return_value = r

        repo = UserViewRepo(session=session)
        result = await repo.get_by_id(_USER_ID)
        assert result is not None

    async def test_get_by_id_not_found(self) -> None:
        """Verifica que get_by_id retorna None quando não encontrado."""
        from shared_core.adapters.repository.view_repo.user import UserViewRepo

        session = _make_session()
        r = MagicMock()
        r.scalar_one_or_none.return_value = None
        session.execute.return_value = r

        repo = UserViewRepo(session=session)
        result = await repo.get_by_id(_USER_ID)
        assert result is None

    async def test_get_public_user_by_email_found(self) -> None:
        """Verifica que get_public_user_by_email retorna o usuário público quando encontrado."""
        from shared_core.adapters.repository.view_repo.user import UserViewRepo

        session = _make_session()
        mock_pu = MagicMock()
        mock_pu.id = _USER_ID
        mock_pu.company = _COMPANY_ID
        mock_pu.active = True
        mock_pu.email_encrypted = b"enc"
        mock_pu.email_hash = "hash"
        mock_pu.password_hash = "hashed"
        r = MagicMock()
        r.scalar_one_or_none.return_value = mock_pu
        session.execute.return_value = r

        repo = UserViewRepo(session=session)
        result = await repo.get_public_user_by_email("u@t.com")
        assert result is not None
        assert result.id == _USER_ID

    async def test_get_public_user_by_email_not_found(self) -> None:
        """Verifica que get_public_user_by_email retorna None quando não encontrado."""
        from shared_core.adapters.repository.view_repo.user import UserViewRepo

        session = _make_session()
        r = MagicMock()
        r.scalar_one_or_none.return_value = None
        session.execute.return_value = r

        repo = UserViewRepo(session=session)
        result = await repo.get_public_user_by_email("nope@t.com")
        assert result is None
