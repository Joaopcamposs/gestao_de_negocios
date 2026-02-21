"""Módulo do agregado Payment."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

import uuid7

from shared_core.domain.value_objects.enums import EntityType, PaymentStatus
from shared_core.domain.events.payment import PaymentCreated, PaymentUpdated
from messagebus.entities import Aggregate, OperationType


@dataclass(kw_only=True)
class Payment(Aggregate):
    """Agregado que representa um pagamento de empresa."""

    id: UUID
    company: UUID
    amount: float
    due_date: datetime
    status: str
    paid_at: datetime | None = None

    def __hash__(self) -> int:
        return hash(self.id)

    @staticmethod
    def create_aggregate(
        company: UUID,
        amount: float,
        due_date: datetime,
    ) -> "Payment":
        """
        Cria uma nova instância do agregado Payment.

        Args:
            company: ID da empresa associada ao pagamento.
            amount: Valor do pagamento.
            due_date: Data de vencimento do pagamento.

        Returns:
            Nova instância de Payment com status pendente.
        """
        return Payment(
            id=uuid7.create(),
            company=company,
            amount=amount,
            due_date=due_date,
            status=PaymentStatus.PENDING,
        )

    def create(self, user_id: UUID | None = None) -> None:
        """Marca o agregado para inserção e emite evento de criação."""
        self._operation_type = OperationType.INSERT
        self._set_create_audit(user_id)

        self.add_event(
            PaymentCreated(
                id=self.id,
                company=self.company,
                entity_type=EntityType.PAYMENT,
                new_data={
                    "amount": float(self.amount),
                    "due_date": self.due_date.isoformat(),
                    "status": self.status,
                },
            )
        )

    def mark_as_paid(self, user_id: UUID | None = None) -> None:
        """
        Registra o pagamento como realizado e emite evento de atualização.

        Args:
            user_id: ID do usuário que está registrando o pagamento (opcional).
        """
        from datetime import timezone

        self._operation_type = OperationType.UPDATE
        self._set_update_audit(user_id)

        old_status = self.status
        self.status = PaymentStatus.PAID
        self.paid_at = datetime.now(timezone.utc)

        self.add_event(
            PaymentUpdated(
                id=self.id,
                company=self.company,
                entity_type=EntityType.PAYMENT,
                old_data={"status": old_status},
                new_data={"status": self.status, "paid_at": self.paid_at.isoformat()},
            )
        )

    def mark_as_overdue(self, user_id: UUID | None = None) -> None:
        """
        Marca o pagamento como em atraso e emite evento de atualização.

        Args:
            user_id: ID do usuário que está marcando o pagamento (opcional).
        """
        self._operation_type = OperationType.UPDATE
        self._set_update_audit(user_id)

        old_status = self.status
        self.status = PaymentStatus.OVERDUE

        self.add_event(
            PaymentUpdated(
                id=self.id,
                company=self.company,
                entity_type=EntityType.PAYMENT,
                old_data={"status": old_status},
                new_data={"status": self.status},
            )
        )
