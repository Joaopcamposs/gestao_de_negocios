"""Módulo de exceções de domínio."""

from dataclasses import dataclass

from fastapi import HTTPException


@dataclass
class UserAlreadyRegistered(HTTPException):
    """Exceção lançada quando o email do usuário já está cadastrado."""

    status_code: int = 409
    detail: str = "User email already registered"


@dataclass
class UserNotFound(HTTPException):
    """Exceção lançada quando o usuário não é encontrado."""

    status_code: int = 404
    detail: str = "User not found"


@dataclass
class CompanyAlreadyRegistered(HTTPException):
    """Exceção lançada quando o nome da empresa já está cadastrado."""

    status_code: int = 409
    detail: str = "Company name already registered"


@dataclass
class CompanyNotFound(HTTPException):
    """Exceção lançada quando a empresa não é encontrada."""

    status_code: int = 404
    detail: str = "Company not found"


@dataclass
class CredentialsException(HTTPException):
    """Exceção lançada quando as credenciais do usuário não são validadas."""

    status_code: int = 401
    detail: str = "Could not validate credentials"


@dataclass
class CreditCardNotFound(HTTPException):
    """Exceção lançada quando o cartão de crédito não é encontrado."""

    status_code: int = 404
    detail: str = "Credit card not found"


@dataclass
class PaymentNotFound(HTTPException):
    """Exceção lançada quando o pagamento não é encontrado."""

    status_code: int = 404
    detail: str = "Payment not found"


@dataclass
class CompanyPaymentOverdueException(HTTPException):
    """Exceção lançada quando a empresa está com pagamento em atraso."""

    status_code: int = 402
    detail: str = "Company payment is overdue"
