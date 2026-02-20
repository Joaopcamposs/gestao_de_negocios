"""Testes unitários para os mixins de repositório (UpsertMixin e PublicUserMixin)."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
import uuid7

from messagebus.entities import OperationType
from shared_core.domain.aggregate.company import Company


_COMPANY_ID = uuid7.create()
_USER_ID = uuid7.create()


def _make_session():
    """Cria uma sessão SQLAlchemy mockada com async context manager."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    return session


# ─── UpsertMixin ───


class TestUpsertMixin:
    """Testes para o mixin UpsertMixin."""

    async def test_execute_upsert_insert(self) -> None:
        """Verifica que _execute_upsert executa INSERT para OperationType.INSERT."""
        from shared_core.adapters.repository.mixins.upsert import UpsertMixin

        class TestRepo(UpsertMixin):
            def __init__(self, session):
                self.session = session

        session = _make_session()
        repo = TestRepo(session)

        agg = MagicMock()
        agg.operation_type = OperationType.INSERT
        agg.id = uuid7.create()

        await repo._execute_upsert(Company, agg, {"id": agg.id, "legal_name": "T"})
        session.execute.assert_awaited_once()

    async def test_execute_upsert_update(self) -> None:
        """Verifica que _execute_upsert executa UPDATE para OperationType.UPDATE."""
        from shared_core.adapters.repository.mixins.upsert import UpsertMixin

        class TestRepo(UpsertMixin):
            def __init__(self, session):
                self.session = session

        session = _make_session()
        repo = TestRepo(session)

        agg = MagicMock()
        agg.operation_type = OperationType.UPDATE
        agg.id = uuid7.create()

        await repo._execute_upsert(Company, agg, {"id": agg.id, "legal_name": "T2"})
        session.execute.assert_awaited_once()

    async def test_execute_upsert_unsupported_raises(self) -> None:
        """Verifica que _execute_upsert levanta ValueError para tipo não suportado."""
        from shared_core.adapters.repository.mixins.upsert import UpsertMixin

        class TestRepo(UpsertMixin):
            def __init__(self, session):
                self.session = session

        session = _make_session()
        repo = TestRepo(session)

        agg = MagicMock()
        agg.operation_type = None
        agg.id = uuid7.create()

        with pytest.raises(ValueError, match="Unsupported"):
            await repo._execute_upsert(Company, agg, {"id": agg.id})

    async def test_execute_soft_delete(self) -> None:
        """Verifica que _execute_soft_delete executa soft delete na sessão."""
        from shared_core.adapters.repository.mixins.upsert import UpsertMixin

        class TestRepo(UpsertMixin):
            def __init__(self, session):
                self.session = session

        session = _make_session()
        repo = TestRepo(session)

        agg = MagicMock()
        agg.id = uuid7.create()
        agg.deleted_at = datetime.now(timezone.utc)
        agg.deleted_by = _USER_ID

        await repo._execute_soft_delete(Company, agg)
        session.execute.assert_awaited_once()


# ─── PublicUserMixin ───


class TestPublicUserMixin:
    """Testes para o mixin PublicUserMixin."""

    async def test_get_public_user_by_id_found(self) -> None:
        """Verifica que get_public_user_by_id retorna o usuário quando encontrado."""
        from shared_core.adapters.repository.mixins.public_user import PublicUserMixin

        class TestRepo(PublicUserMixin):
            def __init__(self, session):
                self.session = session

        session = _make_session()
        mock_result_obj = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_result_obj
        mock_result_obj.id = _USER_ID
        mock_result_obj.company = _COMPANY_ID
        mock_result_obj.active = True
        mock_result_obj.email_encrypted = b"enc"
        mock_result_obj.email_hash = "hash"
        mock_result_obj.password_hash = "hashed"
        session.execute.return_value = mock_result

        repo = TestRepo(session)
        found = await repo.get_public_user_by_id(_USER_ID)
        assert found is not None
        assert found.id == _USER_ID

    async def test_get_public_user_by_id_not_found(self) -> None:
        """Verifica que get_public_user_by_id retorna None quando não encontrado."""
        from shared_core.adapters.repository.mixins.public_user import PublicUserMixin

        class TestRepo(PublicUserMixin):
            def __init__(self, session):
                self.session = session

        session = _make_session()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        session.execute.return_value = mock_result

        repo = TestRepo(session)
        found = await repo.get_public_user_by_id(_USER_ID)
        assert found is None

    async def test_add_public_user_insert(self) -> None:
        """Verifica que add_public_user executa INSERT para novo usuário público."""
        from shared_core.adapters.repository.mixins.public_user import PublicUserMixin

        class TestRepo(PublicUserMixin):
            def __init__(self, session):
                self.session = session

        session = _make_session()
        repo = TestRepo(session)

        public_user = MagicMock()
        public_user.id = _USER_ID
        public_user.company = _COMPANY_ID
        public_user.active = True
        public_user.email_encrypted = b"enc"
        public_user.email_hash = "hash"
        public_user.password_hash = "hashed"
        public_user.created_at = None
        public_user.created_by = None
        public_user.updated_at = None
        public_user.updated_by = None
        public_user.deleted_at = None
        public_user.deleted_by = None
        public_user.operation_type = OperationType.INSERT

        await repo.add_public_user(public_user)
        session.execute.assert_awaited_once()

    async def test_add_public_user_update(self) -> None:
        """Verifica que add_public_user executa UPDATE para usuário público existente."""
        from shared_core.adapters.repository.mixins.public_user import PublicUserMixin

        class TestRepo(PublicUserMixin):
            def __init__(self, session):
                self.session = session

        session = _make_session()
        repo = TestRepo(session)

        public_user = MagicMock()
        public_user.id = _USER_ID
        public_user.company = _COMPANY_ID
        public_user.active = True
        public_user.email_encrypted = b"enc"
        public_user.email_hash = "hash"
        public_user.password_hash = "hashed"
        public_user.created_at = None
        public_user.created_by = None
        public_user.updated_at = None
        public_user.updated_by = None
        public_user.deleted_at = None
        public_user.deleted_by = None
        public_user.operation_type = OperationType.UPDATE

        await repo.add_public_user(public_user)
        session.execute.assert_awaited_once()

    async def test_add_public_user_unsupported_raises(self) -> None:
        """Verifica que add_public_user levanta ValueError para tipo não suportado."""
        from shared_core.adapters.repository.mixins.public_user import PublicUserMixin

        class TestRepo(PublicUserMixin):
            def __init__(self, session):
                self.session = session

        session = _make_session()
        repo = TestRepo(session)

        public_user = MagicMock()
        public_user.id = _USER_ID
        public_user.company = _COMPANY_ID
        public_user.active = True
        public_user.email_encrypted = b"enc"
        public_user.email_hash = "hash"
        public_user.password_hash = "hashed"
        public_user.created_at = None
        public_user.created_by = None
        public_user.updated_at = None
        public_user.updated_by = None
        public_user.deleted_at = None
        public_user.deleted_by = None
        public_user.operation_type = None

        with pytest.raises(ValueError, match="Unsupported"):
            await repo.add_public_user(public_user)

    async def test_remove_public_user(self) -> None:
        """Verifica que remove_public_user executa soft delete."""
        from shared_core.adapters.repository.mixins.public_user import PublicUserMixin

        class TestRepo(PublicUserMixin):
            def __init__(self, session):
                self.session = session

        session = _make_session()
        repo = TestRepo(session)

        public_user = MagicMock()
        public_user.id = _USER_ID
        public_user.deleted_at = datetime.now(timezone.utc)
        public_user.deleted_by = _USER_ID

        await repo.remove_public_user(public_user)
        session.execute.assert_awaited_once()
