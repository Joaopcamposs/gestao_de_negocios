"""Módulo de schemas de autenticação e segurança."""

from pydantic import BaseModel


class Token(BaseModel):
    """Schema de resposta contendo o token JWT e alerta de pagamento se houver."""

    access_token: str
    token_type: str
    payment_alert: str | None = None


class TokenData(BaseModel):
    """Schema de dados extraídos do token JWT."""

    username: str | None = None
