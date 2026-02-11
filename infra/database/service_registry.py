"""Módulo de registro de serviços e resolução de banco de dados por tipo de serviço."""

import os

from dotenv import load_dotenv

load_dotenv()

# Banco de dados padrão (shared_core / sem serviço específico)
DEFAULT_DB_NAME: str = os.getenv("DB_NAME", "postgres")

# Mapeamento de tipo de serviço → nome do banco de dados.
# Cada microserviço tem seu próprio database no PostgreSQL.
SERVICE_DATABASES: dict[str, dict[str, str]] = {
    "dentist": {"db_name": os.getenv("DB_NAME_DENTIST", "db_dentist")},
    "lawyer": {"db_name": os.getenv("DB_NAME_LAWYER", "db_lawyer")},
}


def get_db_name_for_service(service_type: str | None = None) -> str:
    """
    Resolve o nome do banco de dados a partir do tipo de serviço.

    Args:
        service_type: Identificador do microserviço (ex: 'dentist', 'lawyer').
                      Se None, retorna o banco padrão.

    Returns:
        Nome do banco de dados correspondente.

    Raises:
        ValueError: Se o service_type não estiver registrado.
    """
    if service_type is None:
        return DEFAULT_DB_NAME

    config = SERVICE_DATABASES.get(service_type)
    if config is None:
        raise ValueError(
            f"Serviço '{service_type}' não registrado. "
            f"Serviços disponíveis: {list(SERVICE_DATABASES.keys())}"
        )

    return config["db_name"]
