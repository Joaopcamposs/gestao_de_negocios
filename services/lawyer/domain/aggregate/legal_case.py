"""Módulo do agregado LegalCase do contexto advogado."""

from dataclasses import dataclass
from datetime import date
from uuid import UUID

import uuid7

from messagebus.entities import Aggregate, OperationType
from services.lawyer.domain.value_objects.enums import EntityType, LegalCaseStatus
from services.lawyer.domain.events.legal_case import (
    LegalCaseCreated,
    LegalCaseDeleted,
    LegalCaseUpdated,
)


@dataclass(kw_only=True)
class LegalCase(Aggregate):
    """Agregado que representa um processo jurídico no contexto advogado."""

    id: UUID
    company: UUID
    case_number: str
    client_name: str
    description: str | None = None
    status: LegalCaseStatus = LegalCaseStatus.OPEN
    open_date: date | None = None
    notes: str | None = None

    def __hash__(self) -> int:
        return hash(self.id)

    @staticmethod
    def create_aggregate(
        company: UUID,
        case_number: str,
        client_name: str,
        description: str | None = None,
        status: LegalCaseStatus = LegalCaseStatus.OPEN,
        open_date: date | None = None,
        notes: str | None = None,
    ) -> "LegalCase":
        """
        Cria uma nova instância do agregado LegalCase.

        Args:
            company: UUID da empresa proprietária do processo.
            case_number: Número do processo.
            client_name: Nome do cliente.
            description: Descrição do processo (opcional).
            status: Status do processo (padrão: LegalCaseStatus.OPEN).
            open_date: Data de abertura (opcional).
            notes: Observações (opcional).

        Returns:
            Nova instância de LegalCase com ID gerado.
        """
        return LegalCase(
            id=uuid7.create(),
            company=company,
            case_number=case_number,
            client_name=client_name,
            description=description,
            status=status,
            open_date=open_date,
            notes=notes,
        )

    def create(self, user_id: UUID | None = None) -> None:
        """Marca o agregado para inserção e emite evento de criação."""
        self._operation_type = OperationType.INSERT
        self._set_create_audit(user_id)

        new_data = {
            "case_number": self.case_number,
            "client_name": self.client_name,
            "description": self.description,
            "status": self.status,
            "open_date": str(self.open_date) if self.open_date else None,
            "notes": self.notes,
        }

        self.add_event(
            LegalCaseCreated(
                id=self.id,
                company=self.company,
                entity_type=EntityType.LEGAL_CASE,
                new_data=new_data,
            )
        )

    def update(
        self,
        client_name: str | None = None,
        description: str | None = None,
        status: str | None = None,
        notes: str | None = None,
        user_id: UUID | None = None,
    ) -> None:
        """
        Atualiza os dados do processo e emite evento de atualização.

        Args:
            client_name: Novo nome do cliente (opcional).
            description: Nova descrição (opcional).
            status: Novo status (opcional).
            notes: Novas observações (opcional).
            user_id: ID do usuário que está realizando a atualização (opcional).
        """
        self._operation_type = OperationType.UPDATE
        self._set_update_audit(user_id)

        old_data: dict = {}
        new_data: dict = {}

        self._track_change(old_data, new_data, "client_name", client_name)
        self._track_change(old_data, new_data, "description", description)
        self._track_change(old_data, new_data, "status", status)
        self._track_change(old_data, new_data, "notes", notes)

        self.add_event(
            LegalCaseUpdated(
                id=self.id,
                company=self.company,
                entity_type=EntityType.LEGAL_CASE,
                old_data=old_data,
                new_data=new_data,
            )
        )

    def delete(self, user_id: UUID | None = None) -> None:
        """Marca o agregado como deletado (soft delete) e emite evento de exclusão."""
        self._operation_type = OperationType.DELETE

        old_data = {
            "case_number": self.case_number,
            "client_name": self.client_name,
            "description": self.description,
            "status": self.status,
            "open_date": str(self.open_date) if self.open_date else None,
            "notes": self.notes,
        }

        self._set_delete_audit(user_id)

        self.add_event(
            LegalCaseDeleted(
                id=self.id,
                company=self.company,
                entity_type=EntityType.LEGAL_CASE,
                old_data=old_data,
            )
        )
