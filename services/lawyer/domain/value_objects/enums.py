"""Módulo de enums para strings hardcoded do contexto advogado.

Este módulo centraliza todas as strings constantes utilizadas no serviço
advogado, garantindo type safety e evitando erros de digitação.
"""

from enum import StrEnum


class EntityType(StrEnum):
    """Tipos de entidades auditáveis do contexto advogado.

    Valores:
        LEGAL_CASE: Entidade de processo jurídico
    """

    LEGAL_CASE = "LegalCase"


class LegalCaseStatus(StrEnum):
    """Status possíveis para um processo jurídico.

    Valores:
        OPEN: Processo em aberto
        CLOSED: Processo encerrado
        PENDING: Processo pendente de ação
    """

    OPEN = "open"
    CLOSED = "closed"
    PENDING = "pending"
