"""Módulo de entidades base do barramento de mensagens.

Este módulo faz parte do barramento de mensagens e não deve ter dependências
de infraestrutura (banco de dados, ORM, etc.).
"""

from abc import ABC
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any
from uuid import UUID

if TYPE_CHECKING:
    from messagebus.messagebus import Event


@dataclass
class UserBase:
    """Modelo base de usuário com informações mínimas."""

    company: UUID
    id: UUID
    cpf: str | None = None
    email: str | None = None


class DomainRepository(ABC):
    """Repositório abstrato para operações de escrita no domínio."""

    def __init__(
        self,
        session: Any = None,
    ) -> None:
        if session is not None:
            self.session = session


class ViewRepository(ABC):
    """Repositório abstrato para operações de leitura."""

    def __init__(
        self,
        session: Any = None,
    ) -> None:
        if session is not None:
            self.session = session


class OperationType(Enum):
    """Tipos de operação suportados pelo repositório de domínio."""

    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"


@dataclass(kw_only=True)
class Aggregate:
    """Classe base para agregados do domínio."""

    deleted: bool = False

    events: list["Event"] = field(default_factory=list)
    _operation_type: OperationType | None = None

    @property
    def operation_type(self) -> OperationType | None:
        return self._operation_type

    def add_event(self, event: "Event") -> None:
        """Adiciona um evento à lista de eventos do agregado."""
        from messagebus.messagebus import Event

        assert issubclass(type(event), Event)
        self.events.append(event)
