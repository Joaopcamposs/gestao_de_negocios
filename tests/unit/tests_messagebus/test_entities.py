"""Testes unitários para as entidades base do messagebus (Aggregate, AuditReadBase, DomainRepository, ViewRepository)."""

from datetime import datetime, timezone
from unittest.mock import MagicMock

import uuid7

from messagebus.entities import Aggregate, OperationType
from shared_core.domain.aggregate.audit_log import AuditLog


_USER_ID = uuid7.create()


# ─── DomainRepository e ViewRepository base ───


class TestBaseRepositories:
    """Testes para as classes base DomainRepository e ViewRepository."""

    def test_domain_repository_with_session(self) -> None:
        """Verifica que DomainRepository aceita sessão no construtor."""
        from messagebus.entities import DomainRepository

        session = MagicMock()

        class ConcreteRepo(DomainRepository):
            pass

        repo = ConcreteRepo(session=session)
        assert repo.session == session

    def test_domain_repository_without_session(self) -> None:
        """Verifica que DomainRepository funciona sem sessão."""
        from messagebus.entities import DomainRepository

        class ConcreteRepo(DomainRepository):
            pass

        repo = ConcreteRepo()
        assert not hasattr(repo, "session")

    def test_view_repository_with_session(self) -> None:
        """Verifica que ViewRepository aceita sessão no construtor."""
        from messagebus.entities import ViewRepository

        session = MagicMock()

        class ConcreteRepo(ViewRepository):
            pass

        repo = ConcreteRepo(session=session)
        assert repo.session == session

    def test_view_repository_without_session(self) -> None:
        """Verifica que ViewRepository funciona sem sessão."""
        from messagebus.entities import ViewRepository

        class ConcreteRepo(ViewRepository):
            pass

        repo = ConcreteRepo()
        assert not hasattr(repo, "session")


# ─── AuditReadBase ───


class TestAuditReadBase:
    """Testes para a classe AuditReadBase."""

    def test_is_deleted_property(self) -> None:
        """Verifica que is_deleted retorna True quando deleted_at está preenchido."""
        from messagebus.entities import AuditReadBase

        entity = AuditReadBase(deleted_at=datetime.now(timezone.utc))
        assert entity.is_deleted is True

        entity2 = AuditReadBase()
        assert entity2.is_deleted is False


# ─── Aggregate ───


class TestAggregate:
    """Testes para a classe Aggregate e a funcao _track_change."""

    def test_aggregate_track_change_with_value(self) -> None:
        """Verifica que _track_change altera o campo e registra old/new data."""
        agg = Aggregate()
        agg.active = True

        old_data = {}
        new_data = {}

        agg._track_change(
            old_data=old_data,
            new_data=new_data,
            field_name="active",
            new_value=False,
        )

        assert old_data["active"] is True
        assert new_data["active"] is False
        assert agg.active is False

    def test_aggregate_track_change_none_value_ignored(self) -> None:
        """Verifica que _track_change ignora valores None."""
        agg = Aggregate()
        agg.active = True

        old_data = {}
        new_data = {}

        agg._track_change(
            old_data=old_data,
            new_data=new_data,
            field_name="active",
            new_value=None,
        )

        assert "active" not in old_data
        assert "active" not in new_data
        assert agg.active is True

    def test_aggregate_track_change_with_serializer(self) -> None:
        """Verifica que _track_change aplica o serializador nos dados."""
        agg = Aggregate()
        agg.created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)

        old_data = {}
        new_data = {}

        new_dt = datetime(2026, 6, 1, tzinfo=timezone.utc)
        agg._track_change(
            old_data=old_data,
            new_data=new_data,
            field_name="created_at",
            new_value=new_dt,
            serializer=str,
        )

        assert old_data["created_at"] == str(datetime(2026, 1, 1, tzinfo=timezone.utc))
        assert new_data["created_at"] == str(new_dt)


# ─── AuditLog Aggregate ───


class TestAuditLogAggregate:
    """Testes para o agregado AuditLog."""

    def test_create_aggregate(self) -> None:
        """Verifica que create_aggregate cria um AuditLog com campos corretos."""
        entity_id = uuid7.create()
        audit_log = AuditLog.create_aggregate(
            entity_type="Company",
            entity_id=entity_id,
            operation="CREATE",
            user_id=_USER_ID,
            old_data=None,
            new_data={"name": "Test"},
        )

        assert audit_log.entity_type == "Company"
        assert audit_log.entity_id == entity_id
        assert audit_log.operation == "CREATE"
        assert audit_log.user_id == _USER_ID
        assert audit_log.new_data == {"name": "Test"}
        assert audit_log.operation_type == OperationType.INSERT

    def test_hash(self) -> None:
        """Verifica que o hash do AuditLog é baseado no ID."""
        a = AuditLog.create_aggregate(
            entity_type="Test",
            entity_id=uuid7.create(),
            operation="CREATE",
        )
        assert hash(a) == hash(a.id)

    def test_create_sets_timestamp(self) -> None:
        """Verifica que create() define o timestamp de criação."""
        audit_log = AuditLog(
            id=uuid7.create(),
            entity_type="T",
            entity_id=uuid7.create(),
            operation="CREATE",
        )
        audit_log.create()
        assert audit_log.created_at is not None
        assert audit_log.operation_type == OperationType.INSERT
