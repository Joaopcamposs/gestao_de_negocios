"""Módulo principal da aplicação FastAPI do microserviço dentista."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from services.dentist.entrypoints.api.patient import router as patient_router
from shared_core.entrypoints.api.company import router as company_router
from shared_core.entrypoints.api.security import security_router
from shared_core.entrypoints.api.user import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    from infra.database.initializers import create_first_company_and_user

    await create_first_company_and_user(service_type="dentist")
    yield


app = FastAPI(
    title="API Dentist Service",
    description="Microserviço de gestão para dentistas",
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
    return {"message": "Dentist Service is running!"}


# Routers do shared_core
app.include_router(company_router)
app.include_router(user_router)
app.include_router(security_router)

# Routers específicos do dentista
app.include_router(patient_router)
