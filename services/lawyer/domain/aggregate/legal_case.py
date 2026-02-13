"""Módulo do agregado LegalCase do contexto advogado."""

from dataclasses import dataclass
from datetime import date, datetime, timezone
from uuid import UUID

import uuid7

from messagebus.entities import Aggregate, OperationType
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
    status: str = "open"
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
        status: str = "open",
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
            status: Status do processo (padrão: 'open').
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

    def create(self) -> None:
        """Marca o agregado para inserção e emite evento de criação."""
        self._operation_type = OperationType.INSERT

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
                entity_type="LegalCase",
                new_data=new_data,
            )
        )

    def update(
        self,
        client_name: str | None = None,
        description: str | None = None,
        status: str | None = None,
        notes: str | None = None,
    ) -> None:
        """
        Atualiza os dados do processo e emite evento de atualização.

        Args:
            client_name: Novo nome do cliente (opcional).
            description: Nova descrição (opcional).
            status: Novo status (opcional).
            notes: Novas observações (opcional).
        """
        self._operation_type = OperationType.UPDATE

        old_data: dict = {}
        new_data: dict = {}

        if client_name is not None:
            old_data["client_name"] = self.client_name
            new_data["client_name"] = client_name
            self.client_name = client_name
        if description is not None:
            old_data["description"] = self.description
            new_data["description"] = description
            self.description = description
        if status is not None:
            old_data["status"] = self.status
            new_data["status"] = status
            self.status = status
        if notes is not None:
            old_data["notes"] = self.notes
            new_data["notes"] = notes
            self.notes = notes

        self.add_event(
            LegalCaseUpdated(
                id=self.id,
                company=self.company,
                entity_type="LegalCase",
                old_data=old_data,
                new_data=new_data,
            )
        )

    def delete(self) -> None:
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

        self.deleted_at = datetime.now(timezone.utc)

        self.add_event(
            LegalCaseDeleted(
                id=self.id,
                company=self.company,
                entity_type="LegalCase",
                old_data=old_data,
            )
        )
