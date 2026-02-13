"""Módulo do repositório de consulta de AuditLog."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.sql import desc

from messagebus.entities import ViewRepository
from shared_core.domain.entities.audit_log import AuditLog


class AuditLogViewRepo(ViewRepository):
    """Repositório de consulta para AuditLog."""

    async def get_by_entity(
        self,
        entity_type: str,
        entity_id: UUID,
    ) -> list[AuditLog]:
        """
        Busca registros de auditoria de uma entidade específica.

        Retorna o histórico completo de modificações ordenado do mais
        recente para o mais antigo.

        Args:
            entity_type: Tipo da entidade (ex: Company, User, Patient).
            entity_id: UUID da entidade.

        Returns:
            Lista de registros de auditoria da entidade.
        """
        async with self.session as session:
            query = (
                select(AuditLog)
                .where(
                    AuditLog.entity_type == entity_type,
                    AuditLog.entity_id == entity_id,
                )
                .order_by(desc(AuditLog.created_at))
            )

            results = (await session.execute(query)).scalars().all()
            return [
                AuditLog(
                    id=r.id,
                    entity_type=r.entity_type,
                    entity_id=r.entity_id,
                    operation=r.operation,
                    old_data=r.old_data,
                    new_data=r.new_data,
                    user_id=r.user_id,
                    created_at=r.created_at,
                )
                for r in results
            ]

    async def get_by_entity_type(
        self,
        entity_type: str,
    ) -> list[AuditLog]:
        """
        Busca todos os registros de auditoria de um tipo de entidade.

        Args:
            entity_type: Tipo da entidade (ex: Company, User, Patient).

        Returns:
            Lista de registros de auditoria do tipo informado.
        """
        async with self.session as session:
            query = (
                select(AuditLog)
                .where(AuditLog.entity_type == entity_type)
                .order_by(desc(AuditLog.created_at))
            )

            results = (await session.execute(query)).scalars().all()
            return [
                AuditLog(
                    id=r.id,
                    entity_type=r.entity_type,
                    entity_id=r.entity_id,
                    operation=r.operation,
                    old_data=r.old_data,
                    new_data=r.new_data,
                    user_id=r.user_id,
                    created_at=r.created_at,
                )
                for r in results
            ]

    async def get_all(self) -> list[AuditLog]:
        """
        Busca todos os registros de auditoria do schema.

        Returns:
            Lista completa de registros de auditoria ordenados por data.
        """
        async with self.session as session:
            query = select(AuditLog).order_by(desc(AuditLog.created_at))

            results = (await session.execute(query)).scalars().all()
            return [
                AuditLog(
                    id=r.id,
                    entity_type=r.entity_type,
                    entity_id=r.entity_id,
                    operation=r.operation,
                    old_data=r.old_data,
                    new_data=r.new_data,
                    user_id=r.user_id,
                    created_at=r.created_at,
                )
                for r in results
            ]
