"""Módulo de exceções de domínio do contexto dentista."""

from dataclasses import dataclass

from fastapi import HTTPException


@dataclass
class PatientAlreadyRegistered(HTTPException):
    """Exceção lançada quando o CPF do paciente já está cadastrado."""

    status_code: int = 409
    detail: str = "Patient CPF already registered"


@dataclass
class PatientNotFound(HTTPException):
    """Exceção lançada quando o paciente não é encontrado."""

    status_code: int = 404
    detail: str = "Patient not found"
