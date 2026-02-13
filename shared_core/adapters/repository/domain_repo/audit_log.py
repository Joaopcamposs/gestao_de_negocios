"""Módulo do repositório de domínio de AuditLog."""

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

import uuid7
from sqlalchemy import insert

from messagebus.entities import AuditableEvent, DomainRepository
from shared_core.domain.entities.audit_log import AuditLog


class AuditLogDomainRepo(DomainRepository):
    """Repositório de domínio para persistência de registros de auditoria."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.seen: set = set()

    async def add(self, audit_log: AuditLog) -> None:
        """
        Persiste um registro de auditoria no banco de dados.

        Args:
            audit_log: Entidade AuditLog a ser persistida.
        """
        data = {
            "id": audit_log.id,
            "entity_type": audit_log.entity_type,
            "entity_id": audit_log.entity_id,
            "operation": audit_log.operation,
            "old_data": audit_log.old_data,
            "new_data": audit_log.new_data,
            "user_id": audit_log.user_id,
            "created_at": audit_log.created_at,
        }
        await self.session.execute(insert(AuditLog).values(data))

    async def create_from_event(
        self,
        event: AuditableEvent,
        entity_id: UUID,
        operation: str,
        user_id: UUID | None = None,
    ) -> AuditLog:
        """
        Cria e persiste um registro de auditoria a partir de um evento auditável.

        Args:
            event: Evento auditável contendo old_data e new_data.
            entity_id: ID da entidade afetada.
            operation: Tipo de operação (CREATE, UPDATE, DELETE).
            user_id: ID do usuário que realizou a operação (opcional).

        Returns:
            Entidade AuditLog criada e persistida.
        """
        audit_log = AuditLog(
            id=uuid7.create(),
            entity_type=event.entity_type,
            entity_id=entity_id,
            operation=operation,
            old_data=event.old_data,
            new_data=event.new_data,
            user_id=user_id,
            created_at=datetime.now(timezone.utc),
        )
        await self.add(audit_log)
        return audit_log
