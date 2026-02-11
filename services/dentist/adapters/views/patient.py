"""Módulo de views de consulta de Patient no contexto dentista."""

from typing import cast
from uuid import UUID

from infra.database.unit_of_work import UnitOfWork
from services.dentist.adapters.repository.view_repo.patient import PatientViewRepo
from services.dentist.domain.entities.patient import Patient
from services.dentist.domains import DentistDomain


async def view_patient(
    uow: UnitOfWork,
    company: UUID,
    cpf: str | None = None,
    include_deleted: bool = False,
) -> list[Patient]:
    """
    Consulta pacientes. Se o CPF for informado, filtra pelo CPF.
    Caso contrário, retorna todos os pacientes da empresa.

    Args:
        uow: Unit of Work para gerenciar a sessão.
        company: UUID da empresa.
        cpf: CPF do paciente (opcional). Se None, retorna todos.
        include_deleted: Se True, inclui pacientes deletados.

    Returns:
        Lista de entidades Patient.
    """
    async with uow(DentistDomain.patient) as uow:
        view_repo: PatientViewRepo = cast(PatientViewRepo, uow.view_repo)
        if cpf:
            patient = await view_repo.get_by_cpf(
                cpf=cpf, company=company, include_deleted=include_deleted
            )
            if not patient:
                return []
            return [patient]

        patients = await view_repo.get_all(
            company=company, include_deleted=include_deleted
        )
        return patients
