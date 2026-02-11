"""Módulo de mapeamento de domínios para seus respectivos repositórios no contexto dentista."""

from enum import Enum

from services.dentist.adapters.repository.domain_repo.patient import PatientDomainRepo
from services.dentist.adapters.repository.view_repo.patient import PatientViewRepo


class DentistDomain(Enum):
    """Enum que mapeia domínios do dentista para seus repositórios (escrita, leitura)."""

    patient = (PatientDomainRepo, PatientViewRepo)
