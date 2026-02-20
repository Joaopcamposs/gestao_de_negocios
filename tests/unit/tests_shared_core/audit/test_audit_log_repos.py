"""Testes unitários para o repositório de view de AuditLog."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import uuid7


_COMPANY_ID = uuid7.create()
_USER_ID = uuid7.create()


def _make_session():
    """Cria uma sessão SQLAlchemy mockada com async context manager."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    return session


class TestAuditLogViewRepo:
    """Testes para o repositório de view de AuditLog."""

    async def test_get_by_entity(self) -> None:
        """Verifica que get_by_entity retorna logs filtrados por entidade."""
        from shared_core.adapters.repository.view_repo.audit_log import (
            AuditLogViewRepo,
        )

        session = _make_session()
        mock_log = MagicMock()
        mock_log.id = uuid7.create()
        mock_log.entity_type = "Company"
        mock_log.entity_id = _COMPANY_ID
        mock_log.operation = "CREATE"
        mock_log.user_id = _USER_ID
        mock_log.old_data = None
        mock_log.new_data = {}
        mock_log.created_at = datetime.now(timezone.utc)

        sr = MagicMock()
        sr.all.return_value = [mock_log]
        r = MagicMock()
        r.scalars.return_value = sr
        session.execute.return_value = r

        repo = AuditLogViewRepo(session=session)
        result = await repo.get_by_entity("Company", _COMPANY_ID)
        assert len(result) == 1

    async def test_get_by_entity_type(self) -> None:
        """Verifica que get_by_entity_type retorna logs filtrados por tipo."""
        from shared_core.adapters.repository.view_repo.audit_log import (
            AuditLogViewRepo,
        )

        session = _make_session()
        sr = MagicMock()
        sr.all.return_value = []
        r = MagicMock()
        r.scalars.return_value = sr
        session.execute.return_value = r

        repo = AuditLogViewRepo(session=session)
        result = await repo.get_by_entity_type("Company")
        assert result == []

    async def test_get_all(self) -> None:
        """Verifica que get_all retorna todos os logs de auditoria."""
        from shared_core.adapters.repository.view_repo.audit_log import (
            AuditLogViewRepo,
        )

        session = _make_session()
        sr = MagicMock()
        sr.all.return_value = []
        r = MagicMock()
        r.scalars.return_value = sr
        session.execute.return_value = r

        repo = AuditLogViewRepo(session=session)
        result = await repo.get_all()
        assert result == []
