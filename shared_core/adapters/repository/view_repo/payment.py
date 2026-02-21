"""Módulo do repositório de consulta de Payment."""

from uuid import UUID

from sqlalchemy import select

from shared_core.domain.aggregate.payment import Payment as PaymentAggregate
from shared_core.domain.entities.payment import Payment
from messagebus.entities import ViewRepository


class PaymentViewRepo(ViewRepository):
    """Repositório de consulta para Payment."""

    async def get_by_id(self, payment_id: UUID) -> Payment | None:
        """
        Busca um pagamento pelo ID (somente leitura).

        Args:
            payment_id: UUID do pagamento.

        Returns:
            Entidade Payment ou None se não encontrado.
        """
        async with self.session as session:
            payment = (
                await session.execute(
                    select(PaymentAggregate).where(
                        PaymentAggregate.id == payment_id,
                        PaymentAggregate.deleted_at.is_(None),
                    )
                )
            ).scalar_one_or_none()
            if not payment:
                return None
            return self._to_entity(payment)

    async def get_all_by_company(self, company: UUID) -> list[Payment]:
        """
        Busca todos os pagamentos de uma empresa (somente leitura).

        Args:
            company: UUID da empresa.

        Returns:
            Lista de entidades Payment da empresa.
        """
        async with self.session as session:
            payments = (
                (
                    await session.execute(
                        select(PaymentAggregate).where(
                            PaymentAggregate.company == company,
                            PaymentAggregate.deleted_at.is_(None),
                        )
                    )
                )
                .scalars()
                .all()
            )
            return [self._to_entity(p) for p in payments]

    @staticmethod
    def _to_entity(payment: PaymentAggregate) -> Payment:
        """Converte uma linha ORM em entidade Payment."""
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
