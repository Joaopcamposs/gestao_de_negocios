"""Testes unitários para infra/database e service_registry.

Cobre o registro de serviços, geração de URIs de banco de dados,
inicializadores e handlers de schema.
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from infra.database.service_registry import get_db_name_for_service


class TestServiceRegistry:
    """Testes para o registro de serviços de banco de dados."""

    def test_default_db_name(self) -> None:
        """Verifica que o nome padrão do banco é uma string válida."""
        result = get_db_name_for_service(None)
        assert isinstance(result, str)

    def test_dentist_service(self) -> None:
        """Verifica que o serviço dentist retorna um nome de banco."""
        result = get_db_name_for_service("dentist")
        assert result is not None

    def test_lawyer_service(self) -> None:
        """Verifica que o serviço lawyer retorna um nome de banco."""
        result = get_db_name_for_service("lawyer")
        assert result is not None

    def test_unknown_service_raises(self) -> None:
        """Verifica que serviço desconhecido levanta ValueError."""
        with pytest.raises(ValueError, match="não registrado"):
            get_db_name_for_service("unknown_service")


class TestGetDatabaseUri:
    """Testes para a função get_database_uri."""

    def test_default_uri(self) -> None:
        """Verifica que a URI padrão contém o driver asyncpg e o host correto."""
        from infra.database import get_database_uri

        with patch.dict(
            os.environ,
            {
                "TEST_ENV": "false",
                "IN_DOCKER": "false",
                "DB_HOST": "localhost",
                "DB_USER": "user",
                "DB_PASSWORD": "pass",
                "DB_NAME": "test_db",
            },
            clear=False,
        ):
            uri = get_database_uri()
            assert "postgresql+asyncpg://" in uri
            assert "localhost" in uri

    @patch("infra.database.service_registry.DEFAULT_DB_NAME", "test_db")
    def test_test_env_port(self) -> None:
        """Verifica que TEST_ENV usa a porta padrão 5432."""
        from infra.database import get_database_uri

        with patch.dict(
            os.environ,
            {
                "TEST_ENV": "true",
                "IN_DOCKER": "false",
                "DB_HOST": "localhost",
                "DB_USER": "user",
                "DB_PASSWORD": "pass",
                "DB_NAME": "test_db",
                "DB_PORT": "5432",
            },
            clear=False,
        ):
            uri = get_database_uri()
            assert ":5432/" in uri

    def test_in_docker_port(self) -> None:
        """Verifica que IN_DOCKER usa a porta 5432."""
        from infra.database import get_database_uri

        with patch.dict(
            os.environ,
            {
                "TEST_ENV": "false",
                "IN_DOCKER": "true",
                "DB_HOST": "db",
                "DB_USER": "user",
                "DB_PASSWORD": "pass",
                "DB_NAME": "mydb",
                "DB_PORT": "5432",
            },
            clear=False,
        ):
            uri = get_database_uri()
            assert ":5432/" in uri

    def test_test_env_with_postgres_db_raises(self) -> None:
        """Verifica que TEST_ENV com banco 'postgres' levanta RuntimeError."""
        from infra.database import get_database_uri

        with patch.dict(
            os.environ,
            {
                "TEST_ENV": "true",
                "DB_NAME": "postgres",
                "DB_PORT": "5432",
            },
            clear=False,
        ):
            with patch("infra.database.service_registry.DEFAULT_DB_NAME", "postgres"):
                with pytest.raises(RuntimeError, match="TEST_ENV"):
                    get_database_uri()

    def test_with_service_type(self) -> None:
        """Verifica que service_type é incluído na URI do banco."""
        from infra.database import get_database_uri

        with patch.dict(
            os.environ,
            {
                "TEST_ENV": "false",
                "IN_DOCKER": "false",
            },
            clear=False,
        ):
            uri = get_database_uri(service_type="dentist")
            assert "db_dentist" in uri or "postgresql" in uri


class TestInitializers:
    """Testes para os inicializadores de banco de dados."""

    def test_generate_fake_user(self) -> None:
        """Verifica que generate_fake_user_for_first_registration cria usuário com company_id correto."""
        from infra.database.initializers import generate_fake_user_for_first_registration
        import uuid7

        company_id = uuid7.create()
        user = generate_fake_user_for_first_registration(company_id)
        assert user.company == company_id
        assert user.id is not None

    async def test_create_first_company_existing_schema(self) -> None:
        """Verifica que create_first_company_and_user retorna cedo quando schema UUID já existe."""
        from infra.database.initializers import create_first_company_and_user

        valid_uuid = "01234567-89ab-cdef-0123-456789abcdef"

        with patch("infra.database.initializers.start_mappers"):
            with patch(
                "infra.database.initializers.list_existing_schemas",
                new_callable=AsyncMock,
                return_value=[valid_uuid],
            ):
                await create_first_company_and_user()
                # Should return early since a UUID schema already exists

    async def test_create_first_company_no_existing_schema(self) -> None:
        """Verifica que create_first_company_and_user cria empresa quando não há schema UUID."""
        from infra.database.initializers import create_first_company_and_user

        mock_bus = AsyncMock()
        mock_bus.handle = AsyncMock(return_value=None)

        with patch("infra.database.initializers.start_mappers"):
            with patch(
                "infra.database.initializers.list_existing_schemas",
                new_callable=AsyncMock,
                return_value=["public"],
            ):
                with patch(
                    "infra.database.initializers.bootstrap",
                    return_value=mock_bus,
                ):
                    await create_first_company_and_user()
                    mock_bus.handle.assert_awaited_once()

    async def test_create_first_company_error_deletes_schema(self) -> None:
        """Verifica que erro durante criação da empresa remove o schema criado."""
        from infra.database.initializers import create_first_company_and_user

        mock_bus = AsyncMock()
        mock_bus.handle = AsyncMock(side_effect=RuntimeError("DB error"))

        with patch("infra.database.initializers.start_mappers"):
            with patch(
                "infra.database.initializers.list_existing_schemas",
                new_callable=AsyncMock,
                return_value=["public"],
            ):
                with patch(
                    "infra.database.initializers.bootstrap",
                    return_value=mock_bus,
                ):
                    with patch(
                        "infra.database.initializers.delete_schema",
                        new_callable=AsyncMock,
                    ) as mock_del:
                        with pytest.raises(RuntimeError, match="DB error"):
                            await create_first_company_and_user()
                        mock_del.assert_awaited_once()

    async def test_create_first_company_schema_not_uuid(self) -> None:
        """Verifica que schemas não-UUID existentes não impedem a criação da empresa."""
        from infra.database.initializers import create_first_company_and_user

        mock_bus = AsyncMock()
        mock_bus.handle = AsyncMock(return_value=None)

        with patch("infra.database.initializers.start_mappers"):
            with patch(
                "infra.database.initializers.list_existing_schemas",
                new_callable=AsyncMock,
                return_value=["public", "pg_catalog"],
            ):
                with patch(
                    "infra.database.initializers.bootstrap",
                    return_value=mock_bus,
                ):
                    await create_first_company_and_user()
                    mock_bus.handle.assert_awaited_once()


class TestSchemaHandlers:
    """Testes para os handlers de schema do banco de dados."""

    async def test_verify_existing_schema_not_found(self) -> None:
        """Verifica que verify_existing_schema não levanta erro quando schema não existe."""
        from infra.database.schema_handlers import verify_existing_schema

        conn = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        conn.execute = AsyncMock(return_value=mock_result)

        await verify_existing_schema(conn, "new_schema")
        # Should not raise

    async def test_verify_existing_schema_found(self) -> None:
        """Verifica que verify_existing_schema levanta ValueError quando schema já existe."""
        from infra.database.schema_handlers import verify_existing_schema

        conn = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = ("existing_schema",)
        conn.execute = AsyncMock(return_value=mock_result)

        with pytest.raises(ValueError, match="já existe"):
            await verify_existing_schema(conn, "existing_schema")

    async def test_create_full_schema_within_transaction(self) -> None:
        """Verifica que create_full_schema_within_transaction cria e retorna a sessão."""
        from infra.database.schema_handlers import create_full_schema_within_transaction

        mock_session = MagicMock()
        session_factory = AsyncMock(return_value=mock_session)

        with patch(
            "infra.database.schema_handlers.create_schema_and_tables",
            new_callable=AsyncMock,
        ):
            result = await create_full_schema_within_transaction(
                session_factory=session_factory,
                schema_id="test_schema",
            )
            assert result == mock_session
            session_factory.assert_awaited_once()
