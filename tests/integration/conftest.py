"""Configuração de fixtures para testes de integração."""

from typing import AsyncGenerator, Any

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine

import infra.database as db_module
from infra.database import get_async_sql_engine, mapper_registry


@pytest_asyncio.fixture(autouse=True)
async def engine() -> AsyncGenerator[AsyncEngine, Any]:
    """Cria a engine de teste e as tabelas do banco a cada teste."""
    import shared_core.adapters.orm  # noqa: F401 - registra os mappers do core
    import services.dentist.adapters.orm.patient  # noqa: F401 - registra os mappers do dentista
    import services.lawyer.adapters.orm.legal_case  # noqa: F401 - registra os mappers do advogado

    db_module._engines.clear()

    _engine = get_async_sql_engine(force_create_engine=True)
    async with _engine.begin() as conn:
        await conn.run_sync(mapper_registry.metadata.create_all)

    yield _engine

    async with _engine.begin() as conn:
        for table in reversed(mapper_registry.metadata.sorted_tables):
            await conn.execute(table.delete())
    await _engine.dispose()
