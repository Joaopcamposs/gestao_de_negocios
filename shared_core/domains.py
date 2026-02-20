"""Módulo de mapeamento de domínios para seus respectivos repositórios."""

from enum import Enum

from shared_core.adapters.repository.domain_repo.audit_log import (
    AuditLogDomainRepo,
)
from shared_core.adapters.repository.domain_repo.company import (
    CompanyDomainRepo,
)
from shared_core.adapters.repository.domain_repo.credit_card import CreditCardDomainRepo
from shared_core.adapters.repository.domain_repo.payment import PaymentDomainRepo
from shared_core.adapters.repository.domain_repo.user import UserDomainRepo
from shared_core.adapters.repository.view_repo.audit_log import (
    AuditLogViewRepo,
)
from shared_core.adapters.repository.view_repo.company import (
    CompanyViewRepo,
)
from shared_core.adapters.repository.view_repo.credit_card import CreditCardViewRepo
from shared_core.adapters.repository.view_repo.payment import PaymentViewRepo
from shared_core.adapters.repository.view_repo.user import (
    UserViewRepo,
)


class Domain(Enum):
    """Enum que mapeia domínios para seus repositórios (escrita, leitura)."""

    user = (UserDomainRepo, UserViewRepo)
    company = (CompanyDomainRepo, CompanyViewRepo)
    audit_log = (AuditLogDomainRepo, AuditLogViewRepo)
    credit_card = (CreditCardDomainRepo, CreditCardViewRepo)
    payment = (PaymentDomainRepo, PaymentViewRepo)
