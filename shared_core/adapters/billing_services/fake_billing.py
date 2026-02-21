"""Implementação fake do serviço de cobrança para testes e desenvolvimento.

Esta implementação não realiza cobranças reais. Registra todas as operações
em memória e retorna respostas de sucesso simuladas.

Para usar em produção, substitua pela implementação real (ex: StripeBillingService).
"""

import uuid
from datetime import UTC, datetime
from uuid import UUID

from shared_core.adapters.billing_services.abstract_billing import (
    AbstractBillingService,
    BillingCustomer,
    ChargeResult,
    SubscriptionResult,
)


class FakeBillingService(AbstractBillingService):
    """
    Serviço de cobrança fake para testes e desenvolvimento local.

    Todas as operações são simuladas em memória — nenhuma cobrança real é feita.
    Registra os dados em listas acessíveis para validação em testes.
    """

    def __init__(self) -> None:
        self.customers: list[BillingCustomer] = []
        self.subscriptions: list[SubscriptionResult] = []
        self.charges: list[ChargeResult] = []
        self.cancelled_subscriptions: list[str] = []

    async def create_customer(
        self,
        company_id: UUID,
        email: str,
        name: str,
    ) -> BillingCustomer:
        """
        Simula a criação de um cliente no provedor de cobrança.

        Args:
            company_id: UUID da empresa no sistema.
            email: Email de cobrança da empresa.
            name: Nome da empresa ou responsável.

        Returns:
            BillingCustomer com ID externo gerado localmente.
        """
        customer = BillingCustomer(
            external_id=f"fake_cus_{uuid.uuid4().hex[:12]}",
            company_id=company_id,
            email=email,
        )
        self.customers.append(customer)
        return customer

    async def create_subscription(
        self,
        customer_external_id: str,
        price_id: str,
    ) -> SubscriptionResult:
        """
        Simula a criação de uma assinatura recorrente.

        Args:
            customer_external_id: ID externo do cliente.
            price_id: ID do plano/preço.

        Returns:
            SubscriptionResult com status 'active'.
        """
        result = SubscriptionResult(
            subscription_id=f"fake_sub_{uuid.uuid4().hex[:12]}",
            customer_id=customer_external_id,
            status="active",
            current_period_end=datetime(2099, 12, 31, tzinfo=UTC),
        )
        self.subscriptions.append(result)
        return result

    async def cancel_subscription(self, subscription_id: str) -> bool:
        """
        Simula o cancelamento de uma assinatura.

        Args:
            subscription_id: ID da assinatura a cancelar.

        Returns:
            True sempre (simulação de sucesso).
        """
        self.cancelled_subscriptions.append(subscription_id)
        return True

    async def charge_now(
        self,
        customer_external_id: str,
        amount_cents: int,
        currency: str,
        description: str,
    ) -> ChargeResult:
        """
        Simula uma cobrança avulsa imediata.

        Args:
            customer_external_id: ID externo do cliente.
            amount_cents: Valor em centavos.
            currency: Código da moeda ISO 4217.
            description: Descrição da cobrança.

        Returns:
            ChargeResult com status 'succeeded' e paid=True.
        """
        result = ChargeResult(
            charge_id=f"fake_ch_{uuid.uuid4().hex[:12]}",
            amount=amount_cents / 100,
            currency=currency,
            status="succeeded",
            paid=True,
        )
        self.charges.append(result)
        return result

    async def get_subscription_status(self, subscription_id: str) -> str:
        """
        Simula a consulta de status de uma assinatura.

        Args:
            subscription_id: ID da assinatura.

        Returns:
            'canceled' se cancelada, 'active' caso contrário.
        """
        if subscription_id in self.cancelled_subscriptions:
            return "canceled"
        return "active"
