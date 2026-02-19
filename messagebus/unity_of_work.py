"""Módulo abstrato do Unit of Work para gerenciamento de transações.

Este módulo faz parte do barramento de mensagens e não deve ter dependências
de infraestrutura (banco de dados, ORM, etc.). A implementação concreta
está em infra/database/unit_of_work.py.
"""

from __future__ import annotations

from abc import ABC
from collections.abc import Callable, Generator
from enum import Enum
from typing import Any
from uuid import UUID

from messagebus.entities import DomainRepository, UserBase, ViewRepository


class UnitOfWorkContextAlreadyOpen(Exception):
    """Exceção lançada ao tentar abrir um contexto de UoW já aberto."""

    pass


class UnitOfWorkWithProblem(Exception):
    """Exceção lançada ao tentar abrir um contexto de UoW com usuario não pertencendo ao schema."""

    pass


class AbstractUnitOfWork(ABC):
    """
    Interface abstrata do Unit of Work.

    Define o contrato para gerenciamento de transações, repositórios e
    coleta de eventos. Implementações concretas devem fornecer a lógica
    de sessão/banco de dados.
    """

    domain_repo: DomainRepository
    view_repo: ViewRepository
    seen: set
    committed: bool
    session: Any
    user: UserBase | None
    schema: str | None
    create_schema: bool = False

    def __init__(
        self,
        session_factory: Callable | None = None,
        user: UserBase | None = None,
        schema: str | None = None,
        create_schema: bool = False,
        service_type: str | None = None,
    ) -> None:
        if (
            (user and user.company)
            and schema
            and str(user.company) != str(schema)
            and not create_schema
        ):
            raise UnitOfWorkWithProblem("The user does not belong to this schema.")

        self.sql_session_factory = session_factory
        self.user = user
        self.schema = schema or (str(self.user.company) if self.user else None)
        self.create_schema = create_schema
        self.service_type = service_type
        self._active_context = False

    def __call__(
        self,
        domain: Enum | None = None,
    ) -> AbstractUnitOfWork:
        """
        Configura os repositórios baseado no domínio.

        Args:
            domain: Enum do domínio contendo classes de repositório.

        Returns:
            A própria instância para permitir encadeamento.
        """
        if domain:
            self.domain_repo = domain.value[0]
            self.view_repo = domain.value[1]
        return self

    async def __aenter__(self) -> AbstractUnitOfWork:
        """Entra no contexto da unidade de trabalho."""
        self.committed = False

        if self._active_context:
            raise UnitOfWorkContextAlreadyOpen()

        self._active_context = True
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Sai do contexto da unidade de trabalho."""
        self._active_context = False

        if not self.committed:
            await self.rollback()

        await self.session.close()
        await self.session.bind.dispose()
        self.session = None

    @property
    def user_id(self) -> UUID | None:
        """Retorna o ID do usuário autenticado ou None se não houver usuário."""
        return self.user.id if self.user else None

    async def commit(self) -> None:
        """Confirma todas as alterações na sessão."""
        await self.session.commit()
        self.committed = True

    async def rollback(self) -> None:
        """Desfaz todas as alterações pendentes."""
        await self.session.rollback()

    def collect_new_events(self) -> Generator[Any, None, None]:
        """
        Coleta eventos pendentes de todos os agregados rastreados.

        Yields:
            Eventos pendentes de processamento.
        """
        if hasattr(self, "domain_repo") and self.domain_repo:
            for aggregate in getattr(self.domain_repo, "seen", set()):
                while getattr(aggregate, "events", []):
                    yield aggregate.events.pop(0)
