"""Módulo de handlers de comandos e eventos do domínio Payment."""

from datetime import UTC, datetime
from typing import cast
from uuid import UUID

from shared_core.adapters.repository.domain_repo.company import CompanyDomainRepo
from shared_core.adapters.repository.domain_repo.payment import PaymentDomainRepo
from shared_core.adapters.repository.domain_repo.user import UserDomainRepo
from shared_core.domain.commands.payment import (
    CheckAndDeactivateOverdueCompanies,
    CreatePayment,
    MarkPaymentAsOverdue,
    MarkPaymentAsPaid,
)
from shared_core.domain.events.payment import (
    CompanyAndUsersDeactivated,
    CompanyPaymentOverdue,
    CompanyPaymentPaid,
    PaymentCreated,
    PaymentUpdated,
)
from shared_core.domains import Domain
from messagebus.messagebus import logger
from messagebus.unity_of_work import UnitOfWork


async def create_payment(command: CreatePayment, uow: UnitOfWork) -> UUID:
    """Handler para criação de um pagamento para uma empresa."""
    async with uow(Domain.payment) as uow:
        domain_repo: PaymentDomainRepo = cast(PaymentDomainRepo, uow.domain_repo)

        payment = await domain_repo.create_aggregate(
            company=command.company,
            amount=command.amount,
            due_date=command.due_date,
        )
        payment.create(user_id=uow.user_id)

        await domain_repo.add(payment)
        await uow.commit()

        return payment.id


async def mark_payment_as_paid(command: MarkPaymentAsPaid, uow: UnitOfWork) -> None:
    """Handler para registrar um pagamento como realizado e atualizar o status da empresa."""
    company_id: UUID | None = None
    payment_id: UUID | None = None

    async with uow(Domain.payment) as uow:
        payment_repo: PaymentDomainRepo = cast(PaymentDomainRepo, uow.domain_repo)
        payment = await payment_repo.get_by_id(payment_id=command.payment_id)
        payment.mark_as_paid(user_id=uow.user_id)
        await payment_repo.add(payment)
        await uow.commit()
        company_id = payment.company
        payment_id = payment.id

    async with uow(Domain.company) as uow:
        company_repo: CompanyDomainRepo = cast(CompanyDomainRepo, uow.domain_repo)
        company = await company_repo.get_by_id(company_id=company_id)
        company.update_payment_status(
            payment_up_to_date=True,
            last_payment_date=datetime.now(UTC),
            user_id=uow.user_id,
        )
        company.add_event(CompanyPaymentPaid(company=company.id, payment_id=payment_id))
        await company_repo.add(company)
        await uow.commit()


async def mark_payment_as_overdue(command: MarkPaymentAsOverdue, uow: UnitOfWork) -> None:
    """Handler para marcar um pagamento como em atraso e sinalizar a empresa."""
    company_id: UUID | None = None

    async with uow(Domain.payment) as uow:
        payment_repo: PaymentDomainRepo = cast(PaymentDomainRepo, uow.domain_repo)
        payment = await payment_repo.get_by_id(payment_id=command.payment_id)
        payment.mark_as_overdue(user_id=uow.user_id)
        await payment_repo.add(payment)
        await uow.commit()
        company_id = payment.company

    async with uow(Domain.company) as uow:
        company_repo: CompanyDomainRepo = cast(CompanyDomainRepo, uow.domain_repo)
        company = await company_repo.get_by_id(company_id=company_id)
        company.update_payment_status(payment_up_to_date=False, user_id=uow.user_id)
        company.add_event(CompanyPaymentOverdue(company=company.id))
        await company_repo.add(company)
        await uow.commit()


async def check_and_deactivate_overdue_companies(
    command: CheckAndDeactivateOverdueCompanies, uow: UnitOfWork
) -> list[UUID]:
    """
    Handler para verificar e inativar empresas com atraso de pagamento superior a 30 dias.

    Returns:
        Lista de IDs das empresas inativadas.
    """
    deactivated: list[UUID] = []

    async with uow(Domain.payment) as uow:
        payment_repo: PaymentDomainRepo = cast(PaymentDomainRepo, uow.domain_repo)
        overdue_company_ids = await payment_repo.get_overdue_companies(days=30)

    for company_id in overdue_company_ids:
        async with uow(Domain.company) as uow:
            company_repo: CompanyDomainRepo = cast(CompanyDomainRepo, uow.domain_repo)
            try:
                company = await company_repo.get_by_id(company_id=company_id)
            except Exception:
                continue
            if not company.active:
                continue
            company.deactivate(user_id=uow.user_id)
            company.add_event(CompanyAndUsersDeactivated(company=company.id))
            await company_repo.add(company)
            await uow.commit()
            deactivated.append(company_id)

        async with uow(Domain.user) as uow:
            user_repo: UserDomainRepo = cast(UserDomainRepo, uow.domain_repo)
            users = await user_repo.get_all_by_company(company=company_id)
            for user in users:
                user.deactivate(user_id=uow.user_id)
                await user_repo.add(user)
            if users:
                await uow.commit()

    return deactivated


async def payment_created(event: PaymentCreated, uow: UnitOfWork) -> None:
    """Handler para o evento de pagamento criado."""
    logger.info(f"Event PaymentCreated for company: {event.company} payment: {event.id}")


async def payment_updated(event: PaymentUpdated, uow: UnitOfWork) -> None:
    """Handler para o evento de pagamento atualizado."""
    logger.info(f"Event PaymentUpdated for company: {event.company} payment: {event.id}")


async def company_payment_paid(event: CompanyPaymentPaid, uow: UnitOfWork) -> None:
    """Handler para o evento de pagamento confirmado."""
    logger.info(f"Event CompanyPaymentPaid for company: {event.company}")


async def company_payment_overdue(event: CompanyPaymentOverdue, uow: UnitOfWork) -> None:
    """Handler para o evento de pagamento em atraso."""
    logger.info(f"Event CompanyPaymentOverdue for company: {event.company}")


async def company_and_users_deactivated(
    event: CompanyAndUsersDeactivated, uow: UnitOfWork
) -> None:
    """Handler para o evento de inativação de empresa e usuários por atraso."""
    logger.info(f"Event CompanyAndUsersDeactivated for company: {event.company}")
