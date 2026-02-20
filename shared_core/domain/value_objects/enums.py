"""Módulo de enums para strings hardcoded do sistema de auditoria e entidades.

Este módulo centraliza todas as strings constantes utilizadas no sistema,
garantindo type safety e evitando erros de digitação.
"""

from enum import StrEnum


class AuditOperation(StrEnum):
    """Tipos de operações de auditoria suportadas.

    Valores:
        CREATE: Operação de criação de entidade
        UPDATE: Operação de atualização de entidade
        DELETE: Operação de exclusão de entidade
    """

    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class EntityType(StrEnum):
    """Tipos de entidades auditáveis do sistema.

    Valores:
        COMPANY: Entidade de empresa
        USER: Entidade de usuário
        PATIENT: Entidade de paciente (contexto dentista)
        LEGAL_CASE: Entidade de processo jurídico (contexto advogado)
        AUDIT_LOG: Entidade de log de auditoria
        CREDIT_CARD: Entidade de cartão de crédito
        PAYMENT: Entidade de pagamento
    """

    COMPANY = "Company"
    USER = "User"
    PATIENT = "Patient"
    LEGAL_CASE = "LegalCase"
    AUDIT_LOG = "AuditLog"
    CREDIT_CARD = "CreditCard"
    PAYMENT = "Payment"


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


class PaymentStatus(StrEnum):
    """Status possíveis para um pagamento.

    Valores:
        PENDING: Pagamento pendente
        PAID: Pagamento realizado
        OVERDUE: Pagamento em atraso
    """

    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"


class AuditConstant:
    """Constantes utilizadas no sistema de auditoria.

    Esta classe contém valores fixos que não são enums mas são
    utilizados consistentemente no sistema de auditoria.
    """

    REDACTED_PASSWORD = "[REDACTED]"
