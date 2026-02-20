"""Abstração para serviços de cobrança de assinatura.

Sugestão de implementação real: Stripe (https://stripe.com/docs/api).
O Stripe oferece APIs para criação de clientes, assinaturas recorrentes,
cobranças únicas, webhooks de eventos de pagamento e portal do cliente.

Para integrar com Stripe:
    1. Instalar: pip install stripe
    2. Configurar: stripe.api_key = os.environ["STRIPE_API_KEY"]
    3. Implementar esta interface usando stripe.Customer, stripe.Subscription, stripe.PaymentIntent
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class BillingCustomer:
    """Representa um cliente de cobrança criado no provedor externo."""

    external_id: str
    company_id: UUID
    email: str


@dataclass(frozen=True)
class SubscriptionResult:
    """Resultado de uma operação de assinatura."""

    subscription_id: str
    customer_id: str
    status: str
    current_period_end: datetime | None = None


@dataclass(frozen=True)
class ChargeResult:
    """Resultado de uma cobrança avulsa."""

    charge_id: str
    amount: float
    currency: str
    status: str
    paid: bool


class AbstractBillingService(ABC):
    """
    Abstração para serviços de cobrança de assinatura do sistema.

    Implementação real sugerida: Stripe API.
    Documentação: https://stripe.com/docs/api

    Exemplo de integração com Stripe:

        class StripeBillingService(AbstractBillingService):
            def __init__(self) -> None:
                import stripe
                stripe.api_key = os.environ["STRIPE_API_KEY"]
                self._stripe = stripe

            async def create_customer(self, company_id, email, name):
                customer = self._stripe.Customer.create(
                    email=email, name=name,
                    metadata={"company_id": str(company_id)}
                )
                return BillingCustomer(
                    external_id=customer.id,
                    company_id=company_id,
                    email=email,
                )
    """

    @abstractmethod
    async def create_customer(
        self,
        company_id: UUID,
        email: str,
        name: str,
    ) -> BillingCustomer:
        """
        Cria um cliente no provedor de cobrança externo.

        Args:
            company_id: UUID da empresa no sistema.
            email: Email de cobrança da empresa.
            name: Nome da empresa ou responsável.

        Returns:
            Dados do cliente criado no provedor externo.
        """
        raise NotImplementedError

    @abstractmethod
    async def create_subscription(
        self,
        customer_external_id: str,
        price_id: str,
    ) -> SubscriptionResult:
        """
        Cria uma assinatura recorrente para um cliente.

        Args:
            customer_external_id: ID externo do cliente no provedor (ex: cus_xxx do Stripe).
            price_id: ID do plano/preço no provedor (ex: price_xxx do Stripe).

        Returns:
            Dados da assinatura criada.
        """
        raise NotImplementedError

    @abstractmethod
    async def cancel_subscription(self, subscription_id: str) -> bool:
        """
        Cancela uma assinatura existente.

        Args:
            subscription_id: ID da assinatura no provedor externo.

        Returns:
            True se cancelada com sucesso.
        """
        raise NotImplementedError

    @abstractmethod
    async def charge_now(
        self,
        customer_external_id: str,
        amount_cents: int,
        currency: str,
        description: str,
    ) -> ChargeResult:
        """
        Realiza uma cobrança avulsa imediata.

        Args:
            customer_external_id: ID externo do cliente no provedor.
            amount_cents: Valor em centavos (ex: 1999 = R$19,99).
            currency: Código da moeda ISO 4217 (ex: 'brl', 'usd').
            description: Descrição da cobrança para o cliente.

        Returns:
            Dados da cobrança realizada.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_subscription_status(self, subscription_id: str) -> str:
        """
        Consulta o status atual de uma assinatura.

        Args:
            subscription_id: ID da assinatura no provedor externo.

        Returns:
            Status da assinatura (ex: 'active', 'past_due', 'canceled').
        """
        raise NotImplementedError
