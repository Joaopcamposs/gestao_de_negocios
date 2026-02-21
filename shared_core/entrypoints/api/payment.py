"""Módulo de endpoints da API para Payment."""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from shared_core.adapters.views.payment import view_payments
from shared_core.domain.commands.payment import (
    CheckAndDeactivateOverdueCompanies,
    CreatePayment,
    MarkPaymentAsOverdue,
    MarkPaymentAsPaid,
)
from shared_core.entrypoints.schemas.payment import CreatePaymentSchema, ReadPaymentSchema
from shared_core.services.handlers.security import current_user, get_current_user
from shared_core.bootstrap import bootstrap
from shared_core.consts import SERVICE_TYPE
from messagebus.unity_of_work import UnitOfWork

payment_router = APIRouter(
    prefix="/v1", tags=["Payments"], dependencies=[Depends(get_current_user)]
)


@payment_router.post("/payment", response_model=UUID, status_code=status.HTTP_201_CREATED)
async def post_payment(body: CreatePaymentSchema) -> UUID:
    """Registra um novo pagamento para uma empresa."""
    bus = bootstrap(user=current_user.get(), service_type=SERVICE_TYPE)

    command = CreatePayment(
        company=body.company,
        amount=body.amount,
        due_date=body.due_date,
    )
    payment_id: UUID = await bus.handle(command)
    return payment_id


@payment_router.get("/payment", response_model=list[ReadPaymentSchema])
async def get_payments(company: UUID | None = None) -> list[ReadPaymentSchema]:
    """Lista pagamentos. Se company for informado, filtra pela empresa."""
    target_company = company or current_user.get().company
    uow = UnitOfWork(user=current_user.get(), service_type=SERVICE_TYPE)
    return await view_payments(uow, company=target_company)


@payment_router.patch("/payment/{payment_id}/paid", status_code=status.HTTP_200_OK)
async def patch_payment_paid(payment_id: UUID) -> None:
    """Registra um pagamento como realizado."""
    bus = bootstrap(user=current_user.get(), service_type=SERVICE_TYPE)
    await bus.handle(MarkPaymentAsPaid(payment_id=payment_id))


@payment_router.patch("/payment/{payment_id}/overdue", status_code=status.HTTP_200_OK)
async def patch_payment_overdue(payment_id: UUID) -> None:
    """Marca um pagamento como em atraso."""
    bus = bootstrap(user=current_user.get(), service_type=SERVICE_TYPE)
    await bus.handle(MarkPaymentAsOverdue(payment_id=payment_id))


@payment_router.post("/payment/check-overdue", status_code=status.HTTP_200_OK)
async def post_check_overdue() -> list[UUID]:
    """Verifica e inativa empresas com atraso de pagamento superior a 30 dias."""
    bus = bootstrap(user=current_user.get(), service_type=SERVICE_TYPE)
    result: list[UUID] = await bus.handle(CheckAndDeactivateOverdueCompanies())
    return result or []
