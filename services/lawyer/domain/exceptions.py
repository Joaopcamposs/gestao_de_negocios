"""Módulo de exceções de domínio do contexto advogado."""

from dataclasses import dataclass

from fastapi import HTTPException


@dataclass
class LegalCaseAlreadyRegistered(HTTPException):
    """Exceção lançada quando o número do processo já está cadastrado."""

    status_code: int = 409
    detail: str = "Legal case number already registered"


@dataclass
class LegalCaseNotFound(HTTPException):
    """Exceção lançada quando o processo não é encontrado."""

    status_code: int = 404
    detail: str = "Legal case not found"
