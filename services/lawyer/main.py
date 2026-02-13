"""Módulo principal da aplicação FastAPI do microserviço advogado."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from services.lawyer.entrypoints.api.legal_case import router as legal_case_router
from shared_core.entrypoints.api.audit_log import router as audit_log_router
from shared_core.entrypoints.api.company import router as company_router
from shared_core.entrypoints.api.security import security_router
from shared_core.entrypoints.api.user import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    from infra.database.initializers import create_first_company_and_user

    await create_first_company_and_user(service_type="lawyer")
    yield


app = FastAPI(
    title="API Lawyer Service",
    description="Microserviço de gestão para advogados",
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
    return {"message": "Lawyer Service is running!"}


# Routers do shared_core
app.include_router(company_router)
app.include_router(user_router)
app.include_router(security_router)
app.include_router(audit_log_router)

# Routers específicos do advogado
app.include_router(legal_case_router)
