"""Módulo de handlers de comandos e eventos do domínio Patient no contexto dentista."""

from typing import cast
from uuid import UUID

from messagebus.messagebus import logger
from messagebus.unity_of_work import UnitOfWork
from services.dentist.adapters.repository.domain_repo.patient import PatientDomainRepo
from services.dentist.domain.commands.patient import (
    CreatePatient,
    DeletePatient,
    UpdatePatient,
)
from services.dentist.domain.events.patient import (
    PatientCreated,
    PatientDeleted,
    PatientUpdated,
)
from services.dentist.domains import DentistDomain


async def create_patient(command: CreatePatient, uow: UnitOfWork) -> UUID:
    """Handler para criação de paciente."""
    async with uow(DentistDomain.patient) as uow:
        domain_repo: PatientDomainRepo = cast(PatientDomainRepo, uow.domain_repo)

        patient = await domain_repo.create_aggregate(
            company=command.company,
            name=command.name,
            cpf=command.cpf,
            phone=command.phone,
            birth_date=command.birth_date,
            notes=command.notes,
        )
        patient.create(user_id=uow.user_id)

        await domain_repo.add(patient)
        await uow.commit()

        return patient.id


async def update_patient(command: UpdatePatient, uow: UnitOfWork) -> None:
    """Handler para atualização de paciente."""
    async with uow(DentistDomain.patient) as uow:
        domain_repo: PatientDomainRepo = cast(PatientDomainRepo, uow.domain_repo)

        patient = await domain_repo.get_by_cpf(cpf=command.cpf, company=command.company)
        patient.update(
            name=command.new_name,
            phone=command.new_phone,
            birth_date=command.new_birth_date,
            notes=command.new_notes,
            user_id=uow.user_id,
        )

        await domain_repo.add(patient)
        await uow.commit()


async def delete_patient(command: DeletePatient, uow: UnitOfWork) -> None:
    """Handler para exclusão (soft delete) de paciente."""
    async with uow(DentistDomain.patient) as uow:
        domain_repo: PatientDomainRepo = cast(PatientDomainRepo, uow.domain_repo)

        patient = await domain_repo.get_by_cpf(cpf=command.cpf, company=command.company)
        patient.delete(user_id=uow.user_id)

        await domain_repo.remove(patient)
        await uow.commit()


async def patient_created(event: PatientCreated, uow: UnitOfWork) -> None:
    """Handler para o evento de paciente criado."""
    logger.info(
        f"Event PatientCreated for patient: {event.id} in company: {event.company}"
    )


async def patient_updated(event: PatientUpdated, uow: UnitOfWork) -> None:
    """Handler para o evento de paciente atualizado."""
    logger.info(
        f"Event PatientUpdated for patient: {event.id} in company: {event.company}"
    )


async def patient_deleted(event: PatientDeleted, uow: UnitOfWork) -> None:
    """Handler para o evento de paciente excluído."""
    logger.info(
        f"Event PatientDeleted for patient: {event.id} in company: {event.company}"
    )
