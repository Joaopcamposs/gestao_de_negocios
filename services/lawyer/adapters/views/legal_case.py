"""Módulo de views de consulta de LegalCase no contexto advogado."""

from typing import cast
from uuid import UUID

from messagebus.unity_of_work import UnitOfWork
from services.lawyer.adapters.repository.view_repo.legal_case import LegalCaseViewRepo
from services.lawyer.domain.entities.legal_case import LegalCase
from services.lawyer.domains import LawyerDomain


async def view_legal_case(
    uow: UnitOfWork,
    company: UUID,
    case_number: str | None = None,
    include_deleted: bool = False,
) -> list[LegalCase]:
    """
    Consulta processos jurídicos. Se o número for informado, filtra pelo número.

    Args:
        uow: Unit of Work para gerenciar a sessão.
        company: UUID da empresa.
        case_number: Número do processo (opcional).
        include_deleted: Se True, inclui processos deletados.

    Returns:
        Lista de entidades LegalCase.
    """
    async with uow(LawyerDomain.legal_case) as uow:
        view_repo: LegalCaseViewRepo = cast(LegalCaseViewRepo, uow.view_repo)
        if case_number:
            lc = await view_repo.get_by_case_number(
                case_number=case_number, company=company, include_deleted=include_deleted
            )
            if not lc:
                return []
            return [lc]

        return await view_repo.get_all(company=company, include_deleted=include_deleted)
