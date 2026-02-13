"""Módulo do repositório de domínio de LegalCase no contexto advogado."""

from abc import abstractmethod
from typing import Any
from uuid import UUID

from sqlalchemy import insert, select, update
from sqlalchemy.sql import Executable

from messagebus.entities import DomainRepository, OperationType
from services.lawyer.domain.aggregate.legal_case import LegalCase
from services.lawyer.domain.exceptions import (
    LegalCaseAlreadyRegistered,
    LegalCaseNotFound,
)


class AbstractLegalCaseDomainRepo(DomainRepository):
    """Repositório abstrato de domínio para LegalCase."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.seen: set[LegalCase] = set()

    async def add(self, legal_case: LegalCase) -> None:
        """
        Adiciona um processo ao repositório e à lista de rastreados.

        Args:
            legal_case: Agregado LegalCase a ser adicionado.
        """
        self.seen.add(legal_case)
        await self._add(legal_case)

    @abstractmethod
    async def _add(self, legal_case: LegalCase) -> None:
        raise NotImplementedError

    async def remove(self, legal_case: LegalCase) -> None:
        """
        Remove um processo do repositório.

        Args:
            legal_case: Agregado LegalCase a ser removido.
        """
        self.seen.add(legal_case)
        await self._remove(legal_case)

    @abstractmethod
    async def _remove(self, legal_case: LegalCase) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_case_number(self, case_number: str, company: UUID) -> LegalCase:
        raise NotImplementedError()


class LegalCaseDomainRepo(AbstractLegalCaseDomainRepo):
    """Implementação concreta do repositório de domínio de LegalCase."""

    async def get_by_case_number(self, case_number: str, company: UUID) -> LegalCase:
        """
        Busca um processo pelo número dentro de uma empresa.

        Raises:
            LegalCaseNotFound: Se o processo não for encontrado.
        """
        async with self.session as session:
            result = (
                await session.execute(
                    select(LegalCase).where(
                        LegalCase.case_number == case_number,
                        LegalCase.company == company,
                        LegalCase.deleted_at.is_(None),
                    )
                )
            ).scalar_one_or_none()
            if not result:
                raise LegalCaseNotFound

            return LegalCase(
                id=result.id,
                company=result.company,
                case_number=result.case_number,
                client_name=result.client_name,
                description=result.description,
                status=result.status,
                open_date=result.open_date,
                notes=result.notes,
                active=result.active,
                created_at=result.created_at,
                created_by=result.created_by,
                updated_at=result.updated_at,
                updated_by=result.updated_by,
                deleted_at=result.deleted_at,
                deleted_by=result.deleted_by,
            )

    async def create_aggregate(
        self,
        company: UUID,
        case_number: str,
        client_name: str,
        description: str | None = None,
        status: str = "open",
        open_date=None,
        notes: str | None = None,
    ) -> LegalCase:
        """
        Cria um novo agregado LegalCase, verificando duplicidade de número.

        Raises:
            LegalCaseAlreadyRegistered: Se já existe processo com o mesmo número na empresa.
        """
        async with self.session as session:
            existing = (
                await session.execute(
                    select(LegalCase).where(
                        LegalCase.case_number == case_number,
                        LegalCase.company == company,
                        LegalCase.deleted_at.is_(None),
                    )
                )
            ).scalar_one_or_none()
            if existing:
                raise LegalCaseAlreadyRegistered

        return LegalCase.create_aggregate(
            company=company,
            case_number=case_number,
            client_name=client_name,
            description=description,
            status=status,
            open_date=open_date,
            notes=notes,
        )

    async def _add(self, legal_case: LegalCase) -> None:
        """Persiste um processo no banco de dados (inserção ou atualização)."""
        data = {
            "id": legal_case.id,
            "company": legal_case.company,
            "case_number": legal_case.case_number,
            "client_name": legal_case.client_name,
            "description": legal_case.description,
            "status": legal_case.status,
            "open_date": legal_case.open_date,
            "notes": legal_case.notes,
            "active": legal_case.active,
            "created_at": legal_case.created_at,
            "created_by": legal_case.created_by,
            "updated_at": legal_case.updated_at,
            "updated_by": legal_case.updated_by,
            "deleted_at": legal_case.deleted_at,
            "deleted_by": legal_case.deleted_by,
        }

        operation: Executable
        match legal_case.operation_type:
            case OperationType.INSERT:
                operation = insert(LegalCase).values(data)
            case OperationType.UPDATE:
                operation = (
                    update(LegalCase).where(LegalCase.id == legal_case.id).values(data)
                )
            case _:
                raise ValueError("Unsupported operation type for domain repository.")

        await self.session.execute(operation)

    async def _remove(self, legal_case: LegalCase) -> None:
        """Marca um processo como deletado no banco de dados (soft delete)."""
        operation = (
            update(LegalCase)
            .where(LegalCase.id == legal_case.id)
            .values(
                {
                    "deleted_at": legal_case.deleted_at,
                    "deleted_by": legal_case.deleted_by,
                }
            )
        )
        await self.session.execute(operation)
