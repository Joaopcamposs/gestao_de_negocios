"""Módulo de endpoints da API para Patient no contexto dentista."""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from messagebus.unity_of_work import UnitOfWork
from services.dentist.adapters.views.patient import view_patient
from services.dentist.bootstrap import bootstrap_dentist
from services.dentist.domain.commands.patient import (
    CreatePatient,
    DeletePatient,
    UpdatePatient,
)
from services.dentist.entrypoints.schemas.patient import (
    CreatePatientSchema,
    ReadPatientSchema,
    UpdatePatientSchema,
)
from shared_core.services.handlers.security import current_user, get_current_user

router = APIRouter(
    prefix="/v1/dentist",
    tags=["Dentist - Patients"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/patient", response_model=UUID, status_code=status.HTTP_201_CREATED)
async def post_patient(body: CreatePatientSchema) -> UUID:
    """Cria um novo paciente."""
    bus = bootstrap_dentist(user=current_user.get())

    command = CreatePatient(
        company=current_user.get().company,
        name=body.name,
        cpf=body.cpf,
        phone=body.phone,
        birth_date=body.birth_date,
        notes=body.notes,
    )
    patient_id: UUID = await bus.handle(command)
    return patient_id


@router.put("/patient", status_code=status.HTTP_200_OK)
async def put_patient(cpf: str, body: UpdatePatientSchema) -> None:
    """Atualiza um paciente existente."""
    bus = bootstrap_dentist(user=current_user.get())

    command = UpdatePatient(
        company=current_user.get().company,
        cpf=cpf,
        new_name=body.new_name,
        new_phone=body.new_phone,
        new_birth_date=body.new_birth_date,
        new_notes=body.new_notes,
    )
    await bus.handle(command)


@router.get("/patient", response_model=list[ReadPatientSchema])
async def get_patient(
    cpf: str | None = None, include_deleted: bool = False
) -> list[ReadPatientSchema]:
    """Consulta pacientes. Se o CPF for informado, filtra pelo CPF."""
    user = current_user.get()
    uow = UnitOfWork(user=user, service_type="dentist")
    patients = await view_patient(
        uow, company=user.company, cpf=cpf, include_deleted=include_deleted
    )
    return patients


@router.delete("/patient", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient_endpoint(cpf: str) -> None:
    """Exclui um paciente pelo CPF."""
    bus = bootstrap_dentist(user=current_user.get())

    command = DeletePatient(company=current_user.get().company, cpf=cpf)
    await bus.handle(command)
