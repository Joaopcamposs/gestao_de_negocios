"""Módulo do repositório de consulta de LegalCase no contexto advogado."""

from uuid import UUID

from sqlalchemy import select

from messagebus.entities import ViewRepository
from services.lawyer.domain.aggregate.legal_case import LegalCase as LegalCaseAggregate
from services.lawyer.domain.entities.legal_case import LegalCase


class LegalCaseViewRepo(ViewRepository):
    """Repositório de consulta para LegalCase."""

    async def get_by_case_number(
        self, case_number: str, company: UUID, include_deleted: bool = False
    ) -> LegalCase | None:
        """
        Busca um processo pelo número dentro de uma empresa (somente leitura).

        Args:
            case_number: Número do processo.
            company: UUID da empresa.
            include_deleted: Se True, inclui processos deletados.

        Returns:
            Entidade LegalCase ou None se não encontrado.
        """
        async with self.session as session:
            query = select(LegalCaseAggregate).where(
                LegalCaseAggregate.case_number == case_number,
                LegalCaseAggregate.company == company,
            )
            if not include_deleted:
                query = query.where(LegalCaseAggregate.deleted_at.is_(None))

            result = (await session.execute(query)).scalar_one_or_none()
            if not result:
                return None

            return LegalCase(
                id=result.id,
                company=result.company,
                case_number=result.case_number,
                client_name=result.client_name,
                description=result.description,
                status=result.status,
                open_date=result.open_date,
                notes=result.notes,
                deleted_at=result.deleted_at,
            )

    async def get_all(
        self, company: UUID, include_deleted: bool = False
    ) -> list[LegalCase]:
        """
        Busca todos os processos de uma empresa (somente leitura).

        Args:
            company: UUID da empresa.
            include_deleted: Se True, inclui processos deletados.

        Returns:
            Lista de entidades LegalCase.
        """
        async with self.session as session:
            query = select(LegalCaseAggregate).where(
                LegalCaseAggregate.company == company,
            )
            if not include_deleted:
                query = query.where(LegalCaseAggregate.deleted_at.is_(None))

            results = (await session.execute(query)).scalars()
            if not results:
                return []

            return [
                LegalCase(
                    id=r.id,
                    company=r.company,
                    case_number=r.case_number,
                    client_name=r.client_name,
                    description=r.description,
                    status=r.status,
                    open_date=r.open_date,
                    notes=r.notes,
                    deleted_at=r.deleted_at,
                )
                for r in results
            ]
