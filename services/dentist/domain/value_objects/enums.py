"""Módulo de enums para strings hardcoded do contexto dentista.

Este módulo centraliza todas as strings constantes utilizadas no serviço
dentista, garantindo type safety e evitando erros de digitação.
"""

from enum import StrEnum


class EntityType(StrEnum):
    """Tipos de entidades auditáveis do contexto dentista.

    Valores:
        PATIENT: Entidade de paciente
    """

    PATIENT = "Patient"
