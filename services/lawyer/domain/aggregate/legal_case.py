"""Módulo do agregado LegalCase do contexto advogado."""

from dataclasses import dataclass
from datetime import date
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
        self.add_event(LegalCaseCreated(id=self.id, company=self.company))

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

        if client_name is not None:
            self.client_name = client_name
        if description is not None:
            self.description = description
        if status is not None:
            self.status = status
        if notes is not None:
            self.notes = notes

        self.add_event(LegalCaseUpdated(id=self.id, company=self.company))

    def delete(self) -> None:
        """Marca o agregado como deletado (soft delete) e emite evento de exclusão."""
        self._operation_type = OperationType.DELETE
        self.deleted = True
        self.add_event(LegalCaseDeleted(id=self.id, company=self.company))
