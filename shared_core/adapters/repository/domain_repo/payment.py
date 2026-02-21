"""Módulo do repositório de domínio de Payment."""

from abc import abstractmethod
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import select

from shared_core.adapters.repository.mixins.upsert import UpsertMixin
from shared_core.domain.aggregate.payment import Payment
from shared_core.domain.excecoes import PaymentNotFound
from shared_core.domain.value_objects.enums import PaymentStatus
from messagebus.entities import DomainRepository


class AbstractPaymentDomainRepo(DomainRepository):
    """Repositório abstrato de domínio para Payment."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.seen: set[Payment] = set()

    async def add(self, payment: Payment) -> None:
        """
        Adiciona um pagamento ao repositório e à lista de rastreados.

        Args:
            payment: Agregado Payment a ser adicionado.
        """
        self.seen.add(payment)
        await self._add(payment)

    @abstractmethod
    async def _add(self, payment: Payment) -> None:
        """Implementação interna de adição."""
        raise NotImplementedError

    async def remove(self, payment: Payment) -> None:
        """
        Remove um pagamento do repositório (soft delete).

        Args:
            payment: Agregado Payment a ser removido.
        """
        self.seen.add(payment)
        await self._remove(payment)

    @abstractmethod
    async def _remove(self, payment: Payment) -> None:
        """Implementação interna de remoção."""
        raise NotImplementedError


class PaymentDomainRepo(AbstractPaymentDomainRepo, UpsertMixin):
    """Implementação concreta do repositório de domínio de Payment."""

    async def create_aggregate(
        self,
        company: UUID,
        amount: float,
        due_date: datetime,
    ) -> Payment:
        """
        Cria um novo agregado Payment.

        Args:
            company: ID da empresa associada ao pagamento.
            amount: Valor do pagamento.
            due_date: Data de vencimento do pagamento.

        Returns:
            Nova instância do agregado Payment.
        """
        return Payment.create_aggregate(
            company=company,
            amount=amount,
            due_date=due_date,
        )

    async def get_by_id(self, payment_id: UUID) -> Payment:
        """
        Busca um pagamento pelo ID.

        Args:
            payment_id: UUID do pagamento.

        Returns:
            Agregado Payment encontrado.

        Raises:
            PaymentNotFound: Se o pagamento não for encontrado.
        """
        async with self.session as session:
            payment = (
                await session.execute(
                    select(Payment).where(
                        Payment.id == payment_id,
                        Payment.deleted_at.is_(None),
                    )
                )
            ).scalar_one_or_none()
            if not payment:
                raise PaymentNotFound

            return self._to_aggregate(payment)

    async def get_all_by_company(self, company: UUID) -> list[Payment]:
        """
        Busca todos os pagamentos de uma empresa.

        Args:
            company: UUID da empresa.

        Returns:
            Lista de agregados Payment da empresa.
        """
        async with self.session as session:
            payments = (
                (
                    await session.execute(
                        select(Payment).where(
                            Payment.company == company,
                            Payment.deleted_at.is_(None),
                        )
                    )
                )
                .scalars()
                .all()
            )
            return [self._to_aggregate(p) for p in payments]

    async def get_overdue_companies(self, days: int = 30) -> list[UUID]:
        """
        Busca IDs de empresas com pagamento em atraso há mais de N dias.

        Args:
            days: Número de dias de atraso para considerar como crítico.

        Returns:
            Lista de UUIDs das empresas com atraso crítico.
        """
        cutoff = datetime.now(UTC) - timedelta(days=days)
        async with self.session as session:
            payments = (
                (
                    await session.execute(
                        select(Payment).where(
                            Payment.status == PaymentStatus.OVERDUE,
                            Payment.updated_at <= cutoff,
                            Payment.deleted_at.is_(None),
                        )
                    )
                )
                .scalars()
                .all()
            )
            return list({p.company for p in payments})

    @staticmethod
    def _to_aggregate(payment: Any) -> Payment:
        """Converte uma linha ORM em um agregado Payment."""
        return Payment(
            id=payment.id,
            company=payment.company,
            amount=float(payment.amount),
            due_date=payment.due_date,
            status=payment.status,
            paid_at=payment.paid_at,
            created_at=payment.created_at,
            created_by=payment.created_by,
            updated_at=payment.updated_at,
            updated_by=payment.updated_by,
            deleted_at=payment.deleted_at,
            deleted_by=payment.deleted_by,
        )

    async def _add(self, payment: Payment) -> None:
        """Persiste um pagamento no banco de dados (inserção ou atualização)."""
        data = {
            "id": payment.id,
            "company": payment.company,
            "amount": payment.amount,
            "due_date": payment.due_date,
            "paid_at": payment.paid_at,
            "status": payment.status,
            "created_at": payment.created_at,
            "created_by": payment.created_by,
            "updated_at": payment.updated_at,
            "updated_by": payment.updated_by,
            "deleted_at": payment.deleted_at,
            "deleted_by": payment.deleted_by,
        }
        await self._execute_upsert(Payment, payment, data)

    async def _remove(self, payment: Payment) -> None:
        """Marca um pagamento como deletado no banco de dados (soft delete)."""
        await self._execute_soft_delete(Payment, payment)
