"""Módulo do repositório de consulta de Patient no contexto dentista."""

from uuid import UUID

from sqlalchemy import select

from messagebus.entities import ViewRepository
from services.dentist.domain.aggregate.patient import Patient as PatientAggregate
from services.dentist.domain.entities.patient import Patient


class PatientViewRepo(ViewRepository):
    """Repositório de consulta para Patient."""

    async def get_by_cpf(
        self, cpf: str, company: UUID, include_deleted: bool = False
    ) -> Patient | None:
        """
        Busca um paciente pelo CPF dentro de uma empresa (somente leitura).

        Args:
            cpf: CPF do paciente.
            company: UUID da empresa.
            include_deleted: Se True, inclui pacientes deletados.

        Returns:
            Entidade Patient ou None se não encontrado.
        """
        async with self.session as session:
            query = select(PatientAggregate).where(
                PatientAggregate.cpf == cpf,
                PatientAggregate.company == company,
            )
            if not include_deleted:
                query = query.where(PatientAggregate.deleted_at.is_(None))

            result = (await session.execute(query)).scalar_one_or_none()
            if not result:
                return None

            return Patient(
                id=result.id,
                company=result.company,
                name=result.name,
                cpf=result.cpf,
                phone=result.phone,
                birth_date=result.birth_date,
                notes=result.notes,
                deleted_at=result.deleted_at,
            )

    async def get_all(
        self, company: UUID, include_deleted: bool = False
    ) -> list[Patient]:
        """
        Busca todos os pacientes de uma empresa (somente leitura).

        Args:
            company: UUID da empresa.
            include_deleted: Se True, inclui pacientes deletados.

        Returns:
            Lista de entidades Patient.
        """
        async with self.session as session:
            query = select(PatientAggregate).where(
                PatientAggregate.company == company,
            )
            if not include_deleted:
                query = query.where(PatientAggregate.deleted_at.is_(None))

            results = (await session.execute(query)).scalars()
            if not results:
                return []

            return [
                Patient(
                    id=r.id,
                    company=r.company,
                    name=r.name,
                    cpf=r.cpf,
                    phone=r.phone,
                    birth_date=r.birth_date,
                    notes=r.notes,
                    deleted_at=r.deleted_at,
                )
                for r in results
            ]
