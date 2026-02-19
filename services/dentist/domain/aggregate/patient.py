"""Módulo do agregado Patient do contexto dentista."""

from dataclasses import dataclass
from datetime import date
from uuid import UUID

import uuid7

from messagebus.entities import Aggregate, OperationType
from services.dentist.domain.value_objects.enums import EntityType
from services.dentist.domain.events.patient import (
    PatientCreated,
    PatientDeleted,
    PatientUpdated,
)


@dataclass(kw_only=True)
class Patient(Aggregate):
    """Agregado que representa um paciente no contexto dentista."""

    id: UUID
    company: UUID
    name: str
    cpf: str
    phone: str | None = None
    birth_date: date | None = None
    notes: str | None = None

    def __hash__(self) -> int:
        return hash(self.id)

    @staticmethod
    def create_aggregate(
        company: UUID,
        name: str,
        cpf: str,
        phone: str | None = None,
        birth_date: date | None = None,
        notes: str | None = None,
    ) -> "Patient":
        """
        Cria uma nova instância do agregado Patient.

        Args:
            company: UUID da empresa proprietária do paciente.
            name: Nome completo do paciente.
            cpf: CPF do paciente.
            phone: Telefone do paciente (opcional).
            birth_date: Data de nascimento (opcional).
            notes: Observações clínicas (opcional).

        Returns:
            Nova instância de Patient com ID gerado.
        """
        return Patient(
            id=uuid7.create(),
            company=company,
            name=name,
            cpf=cpf,
            phone=phone,
            birth_date=birth_date,
            notes=notes,
        )

    def create(self, user_id: UUID | None = None) -> None:
        """Marca o agregado para inserção e emite evento de criação."""
        self._operation_type = OperationType.INSERT
        self._set_create_audit(user_id)

        new_data = {
            "name": self.name,
            "cpf": self.cpf,
            "phone": self.phone,
            "birth_date": str(self.birth_date) if self.birth_date else None,
            "notes": self.notes,
        }

        self.add_event(
            PatientCreated(
                id=self.id,
                company=self.company,
                entity_type=EntityType.PATIENT,
                new_data=new_data,
            )
        )

    def update(
        self,
        name: str | None = None,
        phone: str | None = None,
        birth_date: date | None = None,
        notes: str | None = None,
        user_id: UUID | None = None,
    ) -> None:
        """
        Atualiza os dados do paciente e emite evento de atualização.

        Args:
            name: Novo nome (opcional).
            phone: Novo telefone (opcional).
            birth_date: Nova data de nascimento (opcional).
            notes: Novas observações (opcional).
            user_id: ID do usuário que está realizando a atualização (opcional).
        """
        self._operation_type = OperationType.UPDATE
        self._set_update_audit(user_id)

        old_data: dict = {}
        new_data: dict = {}

        self._track_change(old_data, new_data, "name", name)
        self._track_change(old_data, new_data, "phone", phone)
        self._track_change(old_data, new_data, "birth_date", birth_date, serializer=str)
        self._track_change(old_data, new_data, "notes", notes)

        self.add_event(
            PatientUpdated(
                id=self.id,
                company=self.company,
                entity_type=EntityType.PATIENT,
                old_data=old_data,
                new_data=new_data,
            )
        )

    def delete(self, user_id: UUID | None = None) -> None:
        """Marca o agregado como deletado (soft delete) e emite evento de exclusão."""
        self._operation_type = OperationType.DELETE

        old_data = {
            "name": self.name,
            "cpf": self.cpf,
            "phone": self.phone,
            "birth_date": str(self.birth_date) if self.birth_date else None,
            "notes": self.notes,
        }

        self._set_delete_audit(user_id)

        self.add_event(
            PatientDeleted(
                id=self.id,
                company=self.company,
                entity_type=EntityType.PATIENT,
                old_data=old_data,
            )
        )
