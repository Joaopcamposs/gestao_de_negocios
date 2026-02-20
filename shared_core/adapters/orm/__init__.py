"""Módulo de mapeamento ORM imperativo entre agregados e tabelas."""

from shared_core.adapters.orm.audit_log import audit_log_mapper  # noqa: F401
from shared_core.adapters.orm.company import company_mapper  # noqa: F401
from shared_core.adapters.orm.user import (
    public_user_mapper,  # noqa: F401
    user_mapper,  # noqa: F401
)


def start_mappers() -> None:
    """Inicializa o mapeamento imperativo entre modelos de domínio e tabelas."""
    pass
