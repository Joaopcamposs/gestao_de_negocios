"""Módulo da implementação concreta do Unit of Work com SQLAlchemy."""

from __future__ import annotations

from typing import Generic, TypeVar

from messagebus.entities import DomainRepository, UserBase, ViewRepository
from messagebus.unity_of_work import AbstractUnitOfWork

from infra.database import default_async_sql_session_factory
from infra.database.schema_handlers import create_full_schema_within_transaction

WRITE_REPO = TypeVar("WRITE_REPO")
READ_REPO = TypeVar("READ_REPO")


class UnitOfWork(AbstractUnitOfWork, Generic[WRITE_REPO, READ_REPO]):
    """Implementação concreta do Unit of Work com sessões SQLAlchemy."""

    domain_repo: DomainRepository
    view_repo: ViewRepository

    def __init__(
        self,
        user: UserBase | None = None,
        schema: str | None = None,
        create_schema: bool = False,
        read_only: bool = False,
        service_type: str | None = None,
    ) -> None:
        self.read_only = read_only

        super().__init__(
            session_factory=default_async_sql_session_factory,
            user=user,
            schema=schema,
            create_schema=create_schema,
            service_type=service_type,
        )

    async def __aenter__(self) -> UnitOfWork:
        """Entra no contexto, criando sessões de leitura e escrita."""
        self.committed = False

        if self.create_schema:  # type: ignore[has-type]
            self.session = await create_full_schema_within_transaction(
                session_factory=self.sql_session_factory,
                schema_id=self.schema,
                service_type=self.service_type,
            )
            self.create_schema = False
        else:
            self.session = await self.sql_session_factory(
                read_only=False,
                schema=self.schema,
                service_type=self.service_type,
            )
        self.read_session = await self.sql_session_factory(
            read_only=True, schema=self.schema, service_type=self.service_type
        )

        if not self.read_only and self.domain_repo:
            self.domain_repo = self.domain_repo(self.session)  # type: ignore[operator]

        if self.view_repo:
            self.view_repo = self.view_repo(self.read_session)  # type: ignore[operator]

        return await super().__aenter__()  # type: ignore[return-value]

    async def __aexit__(  # type: ignore[override]
        self, *args: tuple[type[Exception], Exception, Exception]
    ) -> None:
        """Sai do contexto, fechando sessões de leitura e escrita."""
        if hasattr(self, "read_session") and self.read_session:
            await self.read_session.close()
            await self.read_session.bind.dispose()
            self.read_session = None

        await super().__aexit__(*args)
