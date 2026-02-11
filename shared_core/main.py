"""Módulo principal da aplicação FastAPI."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from shared_core.entrypoints.api.company import router as company_router
from shared_core.entrypoints.api.security import security_router
from shared_core.entrypoints.api.user import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Cria a primeira empresa e usuário do sistema, se ainda não existirem."""
    import shared_core.adapters.orm  # noqa: F401 - registra mappers do core

    from infra.database.initializers import create_first_company_and_user

    await create_first_company_and_user()
    yield


app = FastAPI(
    title="API Barramento de Mensagens",
    description="APIs REST",
    version="0.0.1",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True},
)


@app.get("/")
async def health_check() -> dict[str, str]:
    """Endpoint de health check da API."""
    return {"message": "API is running!"}


app.include_router(company_router)
app.include_router(user_router)
app.include_router(security_router)
