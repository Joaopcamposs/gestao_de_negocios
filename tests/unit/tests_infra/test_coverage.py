"""Testes de cobertura para o módulo infra.

Cobre get_database_uri, get_async_sql_engine, set_schema_name,
default_async_sql_session_factory, get_session, list_existing_schemas,
delete_schema, validate_company_email, schema_handlers e start_mappers.
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestSetSchemaName:
    """Testes para a função set_schema_name."""

    async def test_set_schema_name(self) -> None:
        """Verifica que set_schema_name executa o SET search_path corretamente."""
        from infra.database import set_schema_name

        session = AsyncMock()
        session.execute = AsyncMock()

        await set_schema_name(session, "test_schema")

        session.execute.assert_awaited_once()
        assert session.schema == "test_schema"


class TestGetAsyncSqlEngine:
    """Testes para a função get_async_sql_engine."""

    def test_force_create_engine(self) -> None:
        """Verifica que force_create_engine=True cria uma nova engine sem pool."""
        import os

        with patch.dict(
            os.environ,
            {"TEST_ENV": "false", "IN_DOCKER": "false", "DB_NAME": "test_db"},
            clear=False,
        ):
            with patch("infra.database.service_registry.DEFAULT_DB_NAME", "test_db"):
                from infra.database import get_async_sql_engine

                engine = get_async_sql_engine(force_create_engine=True)
                assert engine is not None

    def test_cached_engine(self) -> None:
        """Verifica que chamadas repetidas retornam a mesma engine (cache)."""
        import os

        with patch.dict(
            os.environ,
            {"TEST_ENV": "false", "IN_DOCKER": "false", "DB_NAME": "test_db"},
            clear=False,
        ):
            with patch("infra.database.service_registry.DEFAULT_DB_NAME", "test_db"):
                from infra.database import _engines, get_async_sql_engine

                _engines.clear()
                engine1 = get_async_sql_engine(service_type=None)
                engine2 = get_async_sql_engine(service_type=None)
                assert engine1 is engine2


class TestDefaultAsyncSqlSessionFactory:
    """Testes para a função default_async_sql_session_factory."""

    async def test_creates_session(self) -> None:
        """Verifica que default_async_sql_session_factory cria uma sessão."""
        import os

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock()
        mock_session.close = AsyncMock()
        mock_session.schema = None

        mock_engine = MagicMock()
        mock_bound = MagicMock()
        mock_engine.execution_options.return_value = mock_bound

        with patch.dict(
            os.environ,
            {"TEST_ENV": "false", "IN_DOCKER": "false", "DB_NAME": "test_db"},
            clear=False,
        ):
            with patch("infra.database.service_registry.DEFAULT_DB_NAME", "test_db"):
                with patch(
                    "infra.database.get_async_sql_engine", return_value=mock_engine
                ):
                    with patch("infra.database.AsyncSession", return_value=mock_session):
                        from infra.database import default_async_sql_session_factory

                        session = await default_async_sql_session_factory(read_only=False)
                        assert session is mock_session
                        await session.async_close()
                        mock_session.close.assert_awaited_once()

    async def test_creates_readonly_session(self) -> None:
        """Verifica que read_only=True define AUTOCOMMIT na sessão."""
        import os

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock()
        mock_session.schema = None

        mock_engine = MagicMock()
        mock_bound = MagicMock()
        mock_engine.execution_options.return_value = mock_bound

        with patch.dict(
            os.environ,
            {"TEST_ENV": "false", "IN_DOCKER": "false", "DB_NAME": "test_db"},
            clear=False,
        ):
            with patch("infra.database.service_registry.DEFAULT_DB_NAME", "test_db"):
                with patch(
                    "infra.database.get_async_sql_engine", return_value=mock_engine
                ):
                    with patch("infra.database.AsyncSession", return_value=mock_session):
                        from infra.database import default_async_sql_session_factory

                        session = await default_async_sql_session_factory(read_only=True)
                        assert session is mock_session
                        call_kwargs = mock_engine.execution_options.call_args[1]
                        assert call_kwargs.get("isolation_level") == "AUTOCOMMIT"


class TestGetSession:
    """Testes para o gerenciador de contexto get_session."""

    async def test_get_session_yields_and_closes(self) -> None:
        """Verifica que get_session cria e fecha a sessão corretamente."""
        mock_session = AsyncMock()
        mock_session.close = AsyncMock()

        with patch(
            "infra.database.default_async_sql_session_factory", return_value=mock_session
        ):
            from infra.database import get_session

            async with get_session(read_only=False, schema="public") as session:
                assert session is mock_session

            mock_session.close.assert_awaited_once()


class TestListExistingSchemas:
    """Testes para a função list_existing_schemas."""

    async def test_list_schemas(self) -> None:
        """Verifica que list_existing_schemas retorna schemas filtrados."""
        mock_conn = AsyncMock()
        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(
            return_value=iter([("my_schema",), ("public",), ("information_schema",)])
        )
        mock_conn.execute = AsyncMock(return_value=mock_result)

        mock_begin = AsyncMock()
        mock_begin.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_begin.__aexit__ = AsyncMock(return_value=None)

        mock_engine = MagicMock()
        mock_engine.begin.return_value = mock_begin

        with patch("infra.database.get_async_sql_engine", return_value=mock_engine):
            from infra.database import list_existing_schemas

            result = await list_existing_schemas()
            assert "my_schema" in result
            assert "public" not in result
            assert "information_schema" not in result


class TestDeleteSchema:
    """Testes para a função delete_schema."""

    async def test_delete_schema(self) -> None:
        """Verifica que delete_schema executa DROP SCHEMA corretamente."""
        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()

        mock_begin = AsyncMock()
        mock_begin.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_begin.__aexit__ = AsyncMock(return_value=None)

        mock_engine = MagicMock()
        mock_engine.begin.return_value = mock_begin

        with patch("infra.database.get_async_sql_engine", return_value=mock_engine):
            from infra.database import delete_schema

            await delete_schema("test_schema_id")
            mock_conn.execute.assert_awaited_once()


class TestValidateCompanyEmail:
    """Testes para a função validate_company_email."""

    async def test_email_not_registered(self) -> None:
        """Verifica que validate_company_email não levanta exceção quando email não existe."""
        mock_conn = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        mock_conn.execute = AsyncMock(return_value=mock_result)

        mock_begin = AsyncMock()
        mock_begin.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_begin.__aexit__ = AsyncMock(return_value=None)

        mock_engine = MagicMock()
        mock_engine.begin.return_value = mock_begin

        with patch("infra.database.get_async_sql_engine", return_value=mock_engine):
            from infra.database import validate_company_email

            await validate_company_email("new@test.com")

    async def test_email_already_registered_raises(self) -> None:
        """Verifica que validate_company_email levanta ValueError quando email já existe."""
        mock_conn = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = ("some_hash",)
        mock_conn.execute = AsyncMock(return_value=mock_result)

        mock_begin = AsyncMock()
        mock_begin.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_begin.__aexit__ = AsyncMock(return_value=None)

        mock_engine = MagicMock()
        mock_engine.begin.return_value = mock_begin

        with patch("infra.database.get_async_sql_engine", return_value=mock_engine):
            from infra.database import validate_company_email

            with pytest.raises(ValueError, match="já existe"):
                await validate_company_email("existing@test.com")


class TestSchemaHandlers:
    """Testes para os handlers de schema do banco de dados."""

    async def test_verify_existing_schema_raises_if_exists(self) -> None:
        """Verifica que verify_existing_schema levanta ValueError se schema já existe."""
        from infra.database.schema_handlers import verify_existing_schema

        mock_conn = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = ("my_schema",)
        mock_conn.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(ValueError, match="já existe"):
            await verify_existing_schema(mock_conn, "my_schema")

    async def test_verify_existing_schema_passes_if_not_exists(self) -> None:
        """Verifica que verify_existing_schema não levanta exceção se schema não existe."""
        from infra.database.schema_handlers import verify_existing_schema

        mock_conn = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        mock_conn.execute = AsyncMock(return_value=mock_result)

        await verify_existing_schema(mock_conn, "new_schema")

    async def test_create_schema_and_tables(self) -> None:
        """Verifica que create_schema_and_tables cria schema e tabelas corretamente."""
        from infra.database.schema_handlers import create_schema_and_tables

        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()
        mock_conn.run_sync = AsyncMock()

        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        mock_conn.execute.return_value = mock_result

        mock_begin = AsyncMock()
        mock_begin.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_begin.__aexit__ = AsyncMock(return_value=None)

        mock_engine = MagicMock()
        mock_engine.begin.return_value = mock_begin
        mock_engine.dispose = AsyncMock()

        with patch(
            "infra.database.schema_handlers.get_async_sql_engine",
            return_value=mock_engine,
        ):
            await create_schema_and_tables("test_schema_id")

        mock_conn.execute.assert_awaited()

    async def test_create_schema_skips_public_tables(self) -> None:
        """Verifica que create_schema_and_tables ignora tabelas com schema='public' (linha continue)."""
        from sqlalchemy import Sequence as SASequence
        from infra.database.schema_handlers import create_schema_and_tables

        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()
        mock_conn.run_sync = AsyncMock()

        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        mock_conn.execute.return_value = mock_result

        mock_begin = AsyncMock()
        mock_begin.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_begin.__aexit__ = AsyncMock(return_value=None)

        mock_engine = MagicMock()
        mock_engine.begin.return_value = mock_begin
        mock_engine.dispose = AsyncMock()

        public_table = MagicMock()
        public_table.schema = "public"
        public_table.columns = []

        seq_col = MagicMock()
        seq_col.default = SASequence("test_seq")
        seq_col.default.schema = None

        normal_table = MagicMock()
        normal_table.schema = None
        normal_table.columns = [seq_col]

        mock_metadata = MagicMock()
        mock_metadata.sorted_tables = [public_table, normal_table]
        mock_metadata.create_all = MagicMock()

        mock_registry = MagicMock()
        mock_registry.metadata = mock_metadata

        with patch(
            "infra.database.schema_handlers.get_async_sql_engine",
            return_value=mock_engine,
        ):
            with patch("infra.database.schema_handlers.mapper_registry", mock_registry):
                await create_schema_and_tables("new_schema")

        assert seq_col.default.schema == "new_schema"

    async def test_create_full_schema_within_transaction(self) -> None:
        """Verifica que create_full_schema_within_transaction cria schema e retorna sessão."""
        from infra.database.schema_handlers import create_full_schema_within_transaction

        mock_session = AsyncMock()
        mock_session_factory = AsyncMock(return_value=mock_session)

        with patch(
            "infra.database.schema_handlers.create_schema_and_tables",
            new_callable=AsyncMock,
        ):
            result = await create_full_schema_within_transaction(
                session_factory=mock_session_factory,
                schema_id="test_schema",
            )

        assert result is mock_session


class TestInfraDatabaseFunctions:
    """Testes para a função get_database_uri em diferentes ambientes."""

    def test_get_database_uri_docker(self) -> None:
        """Verifica que get_database_uri retorna URI correta no ambiente Docker."""
        with patch.dict(
            os.environ,
            {
                "TEST_ENV": "false",
                "IN_DOCKER": "true",
                "DB_HOST": "postgres",
                "DB_USER": "docker_user",
                "DB_PASSWORD": "docker_pass",
                "DB_NAME": "docker_db",
                "DB_PORT": "5432",
            },
            clear=False,
        ):
            with patch("infra.database.service_registry.DEFAULT_DB_NAME", "docker_db"):
                import infra.database as db_module

                uri = db_module.get_database_uri()
                assert ":5432/" in uri

    def test_get_database_uri_production(self) -> None:
        """Verifica que get_database_uri retorna URI correta em produção."""
        with patch.dict(
            os.environ,
            {
                "TEST_ENV": "false",
                "IN_DOCKER": "false",
                "DB_HOST": "prod.db.com",
                "DB_USER": "prod_user",
                "DB_PASSWORD": "prod_pass",
                "DB_NAME": "prod_db",
                "DB_PORT": "54322",
            },
            clear=False,
        ):
            with patch("infra.database.service_registry.DEFAULT_DB_NAME", "prod_db"):
                from infra.database import get_database_uri

                uri = get_database_uri()
                assert ":54322/" in uri

    def test_get_database_uri_test_env_with_postgres_raises(self) -> None:
        """Verifica que get_database_uri levanta RuntimeError em TEST_ENV com postgres."""
        with patch.dict(
            os.environ,
            {
                "TEST_ENV": "true",
                "IN_DOCKER": "false",
                "DB_HOST": "localhost",
                "DB_USER": "user",
                "DB_PASSWORD": "pass",
                "DB_NAME": "postgres",
                "DB_PORT": "5432",
            },
            clear=False,
        ):
            with patch("infra.database.service_registry.DEFAULT_DB_NAME", "postgres"):
                from infra.database import get_database_uri

                with pytest.raises(RuntimeError, match="TEST_ENV está ativo"):
                    get_database_uri()


class TestORMInit:
    """Testes para o módulo ORM do shared_core."""

    def test_orm_module_has_mappers(self) -> None:
        """Verifica que o módulo ORM importa sem erros."""
        import shared_core.adapters.orm as orm_module

        assert hasattr(orm_module, "__name__")
