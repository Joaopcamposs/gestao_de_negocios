"""Módulo com schemas base reutilizáveis para leitura de entidades auditáveis."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ReadAuditSchema(BaseModel):
    """Schema base com campos de auditoria para schemas de leitura.

    Todos os schemas de leitura que representam entidades auditáveis
    devem herdar desta classe para evitar repetição de campos.
    """

    active: bool = True
    deleted_at: datetime | None = None
    deleted_by: UUID | None = None
    created_at: datetime | None = None
    created_by: UUID | None = None
    updated_at: datetime | None = None
    updated_by: UUID | None = None
