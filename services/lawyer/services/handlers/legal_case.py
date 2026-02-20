"""Módulo de handlers de comandos e eventos do domínio LegalCase no contexto advogado."""

from typing import cast
from uuid import UUID

from messagebus.unity_of_work import UnitOfWork
from messagebus.messagebus import logger
from services.lawyer.adapters.repository.domain_repo.legal_case import LegalCaseDomainRepo
from services.lawyer.domain.commands.legal_case import (
    CreateLegalCase,
    DeleteLegalCase,
    UpdateLegalCase,
)
from services.lawyer.domain.events.legal_case import (
    LegalCaseCreated,
    LegalCaseDeleted,
    LegalCaseUpdated,
)
from services.lawyer.domains import LawyerDomain


async def create_legal_case(command: CreateLegalCase, uow: UnitOfWork) -> UUID:
    """Handler para criação de processo jurídico."""
    async with uow(LawyerDomain.legal_case) as uow:
        domain_repo: LegalCaseDomainRepo = cast(LegalCaseDomainRepo, uow.domain_repo)

        legal_case = await domain_repo.create_aggregate(
            company=command.company,
            case_number=command.case_number,
            client_name=command.client_name,
            description=command.description,
            status=command.status,
            open_date=command.open_date,
            notes=command.notes,
        )
        legal_case.create(user_id=uow.user_id)

        await domain_repo.add(legal_case)
        await uow.commit()

        return legal_case.id


async def update_legal_case(command: UpdateLegalCase, uow: UnitOfWork) -> None:
    """Handler para atualização de processo jurídico."""
    async with uow(LawyerDomain.legal_case) as uow:
        domain_repo: LegalCaseDomainRepo = cast(LegalCaseDomainRepo, uow.domain_repo)

        legal_case = await domain_repo.get_by_case_number(
            case_number=command.case_number, company=command.company
        )
        legal_case.update(
            client_name=command.new_client_name,
            description=command.new_description,
            status=command.new_status,
            notes=command.new_notes,
            user_id=uow.user_id,
        )

        await domain_repo.add(legal_case)
        await uow.commit()


async def delete_legal_case(command: DeleteLegalCase, uow: UnitOfWork) -> None:
    """Handler para exclusão (soft delete) de processo jurídico."""
    async with uow(LawyerDomain.legal_case) as uow:
        domain_repo: LegalCaseDomainRepo = cast(LegalCaseDomainRepo, uow.domain_repo)

        legal_case = await domain_repo.get_by_case_number(
            case_number=command.case_number, company=command.company
        )
        legal_case.delete(user_id=uow.user_id)

        await domain_repo.remove(legal_case)
        await uow.commit()


async def legal_case_created(event: LegalCaseCreated, uow: UnitOfWork) -> None:
    """Handler para o evento de processo criado."""
    logger.info(
        f"Event LegalCaseCreated for case: {event.id} in company: {event.company}"
    )


async def legal_case_updated(event: LegalCaseUpdated, uow: UnitOfWork) -> None:
    """Handler para o evento de processo atualizado."""
    logger.info(
        f"Event LegalCaseUpdated for case: {event.id} in company: {event.company}"
    )


async def legal_case_deleted(event: LegalCaseDeleted, uow: UnitOfWork) -> None:
    """Handler para o evento de processo excluído."""
    logger.info(
        f"Event LegalCaseDeleted for case: {event.id} in company: {event.company}"
    )
