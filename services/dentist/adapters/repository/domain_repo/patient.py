"""Módulo do repositório de domínio de Patient no contexto dentista."""

from abc import abstractmethod
from typing import Any
from uuid import UUID

from sqlalchemy import insert, select, update
from sqlalchemy.sql import Executable

from messagebus.entities import DomainRepository, OperationType
from services.dentist.domain.aggregate.patient import Patient
from services.dentist.domain.exceptions import PatientAlreadyRegistered, PatientNotFound


class AbstractPatientDomainRepo(DomainRepository):
    """Repositório abstrato de domínio para Patient."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.seen: set[Patient] = set()

    async def add(self, patient: Patient) -> None:
        """
        Adiciona um paciente ao repositório e à lista de rastreados.

        Args:
            patient: Agregado Patient a ser adicionado.
        """
        self.seen.add(patient)
        await self._add(patient)

    @abstractmethod
    async def _add(self, patient: Patient) -> None:
        """Implementação interna de adição."""
        raise NotImplementedError

    async def remove(self, patient: Patient) -> None:
        """
        Remove um paciente do repositório.

        Args:
            patient: Agregado Patient a ser removido.
        """
        self.seen.add(patient)
        await self._remove(patient)

    @abstractmethod
    async def _remove(self, patient: Patient) -> None:
        """Implementação interna de remoção."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_cpf(self, cpf: str, company: UUID) -> Patient:
        """
        Busca um paciente pelo CPF dentro de uma empresa.

        Args:
            cpf: CPF do paciente.
            company: UUID da empresa.

        Returns:
            Agregado Patient encontrado.
        """
        raise NotImplementedError()


class PatientDomainRepo(AbstractPatientDomainRepo):
    """Implementação concreta do repositório de domínio de Patient."""

    async def get_by_cpf(self, cpf: str, company: UUID) -> Patient:
        """
        Busca um paciente pelo CPF dentro de uma empresa.

        Raises:
            PatientNotFound: Se o paciente não for encontrado.
        """
        async with self.session as session:
            result = (
                await session.execute(
                    select(Patient).where(
                        Patient.cpf == cpf,
                        Patient.company == company,
                        Patient.deleted == False,  # noqa: E712
                    )
                )
            ).scalar_one_or_none()
            if not result:
                raise PatientNotFound

            return Patient(
                id=result.id,
                company=result.company,
                name=result.name,
                cpf=result.cpf,
                phone=result.phone,
                birth_date=result.birth_date,
                notes=result.notes,
                deleted=result.deleted,
            )

    async def create_aggregate(
        self,
        company: UUID,
        name: str,
        cpf: str,
        phone: str | None = None,
        birth_date=None,
        notes: str | None = None,
    ) -> Patient:
        """
        Cria um novo agregado Patient, verificando duplicidade de CPF na empresa.

        Raises:
            PatientAlreadyRegistered: Se já existe paciente com o mesmo CPF na empresa.
        """
        async with self.session as session:
            existing = (
                await session.execute(
                    select(Patient).where(
                        Patient.cpf == cpf,
                        Patient.company == company,
                        Patient.deleted == False,  # noqa: E712
                    )
                )
            ).scalar_one_or_none()
            if existing:
                raise PatientAlreadyRegistered

        return Patient.create_aggregate(
            company=company,
            name=name,
            cpf=cpf,
            phone=phone,
            birth_date=birth_date,
            notes=notes,
        )

    async def _add(self, patient: Patient) -> None:
        """Persiste um paciente no banco de dados (inserção ou atualização)."""
        data = {
            "id": patient.id,
            "company": patient.company,
            "name": patient.name,
            "cpf": patient.cpf,
            "phone": patient.phone,
            "birth_date": patient.birth_date,
            "notes": patient.notes,
            "deleted": patient.deleted,
        }

        operation: Executable
        match patient.operation_type:
            case OperationType.INSERT:
                operation = insert(Patient).values(data)
            case OperationType.UPDATE:
                operation = update(Patient).where(Patient.id == patient.id).values(data)
            case _:
                raise ValueError("Unsupported operation type for domain repository.")

        await self.session.execute(operation)

    async def _remove(self, patient: Patient) -> None:
        """Marca um paciente como deletado no banco de dados (soft delete)."""
        operation = (
            update(Patient).where(Patient.id == patient.id).values({"deleted": True})
        )
        await self.session.execute(operation)
