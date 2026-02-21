"""Módulo de handlers de segurança e autenticação."""

from contextvars import ContextVar
from typing import Annotated, cast

import jwt
from fastapi import Depends, Security
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from shared_core.adapters.repository.view_repo.company import CompanyViewRepo
from shared_core.adapters.repository.view_repo.user import UserViewRepo
from shared_core.consts import ALGORITHM, SECRET_KEY, SERVICE_TYPE, oauth2_scheme
from shared_core.domain.commands.security import AuthenticateUser
from shared_core.domain.entities.user import User
from shared_core.domain.excecoes import CredentialsException, UserInactiveException
from shared_core.entrypoints.schemas.security import Token
from shared_core.domains import Domain
from messagebus.unity_of_work import UnitOfWork

current_user: ContextVar["User"] = ContextVar("current_user")


async def authenticate_user(command: AuthenticateUser, uow: UnitOfWork) -> Token | None:
    """
    Autentica um usuário pelo email e senha via usuário público.
    Inclui alerta de pagamento no token se a empresa estiver com pagamento em atraso.

    Args:
        command: Comando de autenticação com email e senha.
        uow: Unit of Work para gerenciar a sessão.

    Returns:
        Token JWT se autenticado com sucesso, None caso contrário.
    """
    async with uow(Domain.user) as uow:
        view_repo: UserViewRepo = cast(UserViewRepo, uow.view_repo)

        user = await view_repo.get_public_user_by_email(command.email)
        if not user:
            return None
        if not user.active:
            raise UserInactiveException()
        if not user.verify_password(command.password):
            return None

        token = user.generate_token(
            company_id=user.company,
            encrypted_email=user.email_encrypted,
        )

    payment_alert: str | None = None
    async with uow(Domain.company) as uow:
        company_view_repo: CompanyViewRepo = cast(CompanyViewRepo, uow.view_repo)
        companies = await company_view_repo.get_all()
        for company in companies:
            if str(company.id) == str(user.company):
                if not company.payment_up_to_date:
                    payment_alert = (
                        "Atenção: o pagamento da sua empresa está em atraso. "
                        "Regularize para evitar a inativação da conta."
                    )
                break

    return Token(
        access_token=token.access_token,
        token_type=token.token_type,
        payment_alert=payment_alert,
    )


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    """
    Obtém o usuário autenticado a partir do token JWT.

    Args:
        token: Token JWT do cabeçalho Authorization.

    Returns:
        Entidade User do usuário autenticado.

    Raises:
        CredentialsException: Se o token for inválido ou o usuário não for encontrado.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("email")
        company_id: str | None = payload.get("id_empresa")
        if email is None:
            raise CredentialsException()
    except (InvalidTokenError, ValidationError):
        raise CredentialsException()

    uow = UnitOfWork(schema=str(company_id), service_type=SERVICE_TYPE)
    async with uow(Domain.user) as uow:
        view_repo: UserViewRepo = cast(UserViewRepo, uow.view_repo)
        user = await view_repo.get_by_email(email)

    if user is None:
        raise CredentialsException()

    current_user.set(user)

    return user


async def get_current_active_user(
    current_user_ctx: Annotated[User, Security(get_current_user)],
) -> User:
    """
    Verifica se o usuário autenticado está ativo.

    Args:
        current_user_ctx: Usuário autenticado obtido do token JWT.

    Returns:
        Entidade User do usuário autenticado e ativo.

    Raises:
        UserInactiveException: Se o usuário estiver inativo.
    """
    if not current_user_ctx.active:
        raise UserInactiveException()
    return current_user_ctx
