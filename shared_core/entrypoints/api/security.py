"""Módulo de endpoints da API para autenticação e segurança."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from shared_core.domain.commands.security import AuthenticateUser
from shared_core.domain.entities.user import User
from shared_core.entrypoints.schemas.security import Token
from shared_core.entrypoints.schemas.user import ReadUserSchema
from shared_core.services.handlers.security import get_current_user
from shared_core.bootstrap import bootstrap
from shared_core.consts import SERVICE_TYPE

security_router = APIRouter(prefix="/api", tags=["Login"])


@security_router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """Autentica o usuário e retorna um token JWT."""
    bus = bootstrap(service_type=SERVICE_TYPE)

    token = await bus.handle(
        AuthenticateUser(
            email=form_data.username,
            password=form_data.password,
        )
    )
    if not token:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return token


@security_router.get("/user/me/", response_model=ReadUserSchema)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Retorna os dados do usuário autenticado."""
    return current_user
