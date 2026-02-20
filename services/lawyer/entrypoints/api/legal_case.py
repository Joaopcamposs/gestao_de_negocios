"""Módulo de endpoints da API para LegalCase no contexto advogado."""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from messagebus.unity_of_work import UnitOfWork
from services.lawyer.adapters.views.legal_case import view_legal_case
from services.lawyer.bootstrap import bootstrap_lawyer
from services.lawyer.domain.commands.legal_case import (
    CreateLegalCase,
    DeleteLegalCase,
    UpdateLegalCase,
)
from services.lawyer.entrypoints.schemas.legal_case import (
    CreateLegalCaseSchema,
    ReadLegalCaseSchema,
    UpdateLegalCaseSchema,
)
from shared_core.services.handlers.security import current_user, get_current_user

router = APIRouter(
    prefix="/v1/lawyer",
    tags=["Lawyer - Legal Cases"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/case", response_model=UUID, status_code=status.HTTP_201_CREATED)
async def post_legal_case(body: CreateLegalCaseSchema) -> UUID:
    """Cria um novo processo jurídico."""
    bus = bootstrap_lawyer(user=current_user.get())

    command = CreateLegalCase(
        company=current_user.get().company,
        case_number=body.case_number,
        client_name=body.client_name,
        description=body.description,
        status=body.status,
        open_date=body.open_date,
        notes=body.notes,
    )
    case_id: UUID = await bus.handle(command)
    return case_id


@router.put("/case", status_code=status.HTTP_200_OK)
async def put_legal_case(body: UpdateLegalCaseSchema) -> None:
    """Atualiza um processo jurídico existente."""
    bus = bootstrap_lawyer(user=current_user.get())

    command = UpdateLegalCase(
        company=current_user.get().company,
        case_number=body.case_number,
        new_client_name=body.new_client_name,
        new_description=body.new_description,
        new_status=body.new_status,
        new_notes=body.new_notes,
    )
    await bus.handle(command)


@router.get("/case", response_model=list[ReadLegalCaseSchema])
async def get_legal_case(
    case_number: str | None = None, include_deleted: bool = False
) -> list[ReadLegalCaseSchema]:
    """Consulta processos jurídicos."""
    user = current_user.get()
    uow = UnitOfWork(user=user, service_type="lawyer")
    cases = await view_legal_case(
        uow,
        company=user.company,
        case_number=case_number,
        include_deleted=include_deleted,
    )
    return cases


@router.delete("/case", status_code=status.HTTP_204_NO_CONTENT)
async def delete_legal_case_endpoint(case_number: str) -> None:
    """Exclui um processo jurídico pelo número."""
    bus = bootstrap_lawyer(user=current_user.get())

    command = DeleteLegalCase(company=current_user.get().company, case_number=case_number)
    await bus.handle(command)
