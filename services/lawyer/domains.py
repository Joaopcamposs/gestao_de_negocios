"""Módulo de mapeamento de domínios para seus respectivos repositórios no contexto advogado."""

from enum import Enum

from services.lawyer.adapters.repository.domain_repo.legal_case import LegalCaseDomainRepo
from services.lawyer.adapters.repository.view_repo.legal_case import LegalCaseViewRepo


class LawyerDomain(Enum):
    """Enum que mapeia domínios do advogado para seus repositórios (escrita, leitura)."""

    legal_case = (LegalCaseDomainRepo, LegalCaseViewRepo)
