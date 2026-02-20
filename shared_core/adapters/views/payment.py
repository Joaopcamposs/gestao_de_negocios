"""Módulo de views de consulta de Payment."""

from typing import cast
from uuid import UUID

from shared_core.adapters.repository.view_repo.payment import PaymentViewRepo
from shared_core.domain.entities.payment import Payment
from shared_core.domains import Domain
from messagebus.unity_of_work import UnitOfWork


async def view_payments(
    uow: UnitOfWork,
    company: UUID,
) -> list[Payment]:
    """
    Consulta os pagamentos de uma empresa.

    Args:
        uow: Unit of Work para gerenciar a sessão.
        company: UUID da empresa cujos pagamentos serão listados.

    Returns:
        Lista de entidades Payment da empresa.
    """
    async with uow(Domain.payment) as uow:
        view_repo: PaymentViewRepo = cast(PaymentViewRepo, uow.view_repo)
        return await view_repo.get_all_by_company(company=company)
