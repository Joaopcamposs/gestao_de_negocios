"""Testes unitários para billing e email services do shared_core.

Cobre FakeBillingService, FakeEmailService e os data classes relacionados.
"""

import uuid7

from shared_core.adapters.billing_services.abstract_billing import (
    BillingCustomer,
    ChargeResult,
    SubscriptionResult,
)
from shared_core.adapters.billing_services.fake_billing import FakeBillingService
from shared_core.adapters.email_services.abstract_email import (
    EmailMessage,
    EmailResult,
)
from shared_core.adapters.email_services.fake_email import FakeEmailService


_COMPANY_ID = uuid7.create()


class TestAbstractBillingNotImplemented:
    """Testes para cobertura dos raise NotImplementedError do AbstractBillingService."""

    async def test_create_customer_raises(self) -> None:
        """Cobre o raise NotImplementedError de create_customer."""
        import pytest
        from shared_core.adapters.billing_services.abstract_billing import (
            AbstractBillingService,
        )

        class Stub(AbstractBillingService):
            async def create_customer(self, company_id, email, name):
                return await super().create_customer(company_id, email, name)

            async def create_subscription(self, cid, pid):
                pass

            async def cancel_subscription(self, sid):
                pass

            async def charge_now(self, cid, amt, cur, desc):
                pass

            async def get_subscription_status(self, sid):
                pass

        with pytest.raises(NotImplementedError):
            await Stub().create_customer(None, "e@e.com", "T")

    async def test_create_subscription_raises(self) -> None:
        """Cobre o raise NotImplementedError de create_subscription."""
        import pytest
        from shared_core.adapters.billing_services.abstract_billing import (
            AbstractBillingService,
        )

        class Stub(AbstractBillingService):
            async def create_customer(self, company_id, email, name):
                pass

            async def create_subscription(self, cid, pid):
                return await super().create_subscription(cid, pid)

            async def cancel_subscription(self, sid):
                pass

            async def charge_now(self, cid, amt, cur, desc):
                pass

            async def get_subscription_status(self, sid):
                pass

        with pytest.raises(NotImplementedError):
            await Stub().create_subscription("cid", "pid")

    async def test_cancel_subscription_raises(self) -> None:
        """Cobre o raise NotImplementedError de cancel_subscription."""
        import pytest
        from shared_core.adapters.billing_services.abstract_billing import (
            AbstractBillingService,
        )

        class Stub(AbstractBillingService):
            async def create_customer(self, company_id, email, name):
                pass

            async def create_subscription(self, cid, pid):
                pass

            async def cancel_subscription(self, sid):
                return await super().cancel_subscription(sid)

            async def charge_now(self, cid, amt, cur, desc):
                pass

            async def get_subscription_status(self, sid):
                pass

        with pytest.raises(NotImplementedError):
            await Stub().cancel_subscription("sid")

    async def test_charge_now_raises(self) -> None:
        """Cobre o raise NotImplementedError de charge_now."""
        import pytest
        from shared_core.adapters.billing_services.abstract_billing import (
            AbstractBillingService,
        )

        class Stub(AbstractBillingService):
            async def create_customer(self, company_id, email, name):
                pass

            async def create_subscription(self, cid, pid):
                pass

            async def cancel_subscription(self, sid):
                pass

            async def charge_now(self, cid, amt, cur, desc):
                return await super().charge_now(cid, amt, cur, desc)

            async def get_subscription_status(self, sid):
                pass

        with pytest.raises(NotImplementedError):
            await Stub().charge_now("cid", 100, "brl", "desc")

    async def test_get_subscription_status_raises(self) -> None:
        """Cobre o raise NotImplementedError de get_subscription_status."""
        import pytest
        from shared_core.adapters.billing_services.abstract_billing import (
            AbstractBillingService,
        )

        class Stub(AbstractBillingService):
            async def create_customer(self, company_id, email, name):
                pass

            async def create_subscription(self, cid, pid):
                pass

            async def cancel_subscription(self, sid):
                pass

            async def charge_now(self, cid, amt, cur, desc):
                pass

            async def get_subscription_status(self, sid):
                return await super().get_subscription_status(sid)

        with pytest.raises(NotImplementedError):
            await Stub().get_subscription_status("sid")


class TestAbstractEmailNotImplemented:
    """Testes para cobertura dos raise NotImplementedError do AbstractEmailService."""

    async def test_send_raises(self) -> None:
        """Cobre o raise NotImplementedError de send."""
        import pytest
        from shared_core.adapters.email_services.abstract_email import (
            AbstractEmailService,
            EmailMessage,
        )

        class Stub(AbstractEmailService):
            async def send(self, msg):
                return await super().send(msg)

            async def send_welcome(self, to, name):
                pass

            async def send_payment_overdue(self, to, cn, dd, amt):
                pass

            async def send_account_deactivated(self, to, cn):
                pass

            async def send_password_reset(self, to, token):
                pass

        msg = EmailMessage(to="a@b.com", subject="T", body_html="<p>H</p>")
        with pytest.raises(NotImplementedError):
            await Stub().send(msg)

    async def test_send_welcome_raises(self) -> None:
        """Cobre o raise NotImplementedError de send_welcome."""
        import pytest
        from shared_core.adapters.email_services.abstract_email import (
            AbstractEmailService,
        )

        class Stub(AbstractEmailService):
            async def send(self, msg):
                pass

            async def send_welcome(self, to, name):
                return await super().send_welcome(to, name)

            async def send_payment_overdue(self, to, cn, dd, amt):
                pass

            async def send_account_deactivated(self, to, cn):
                pass

            async def send_password_reset(self, to, token):
                pass

        with pytest.raises(NotImplementedError):
            await Stub().send_welcome("a@b.com", "T")

    async def test_send_payment_overdue_raises(self) -> None:
        """Cobre o raise NotImplementedError de send_payment_overdue."""
        import pytest
        from shared_core.adapters.email_services.abstract_email import (
            AbstractEmailService,
        )

        class Stub(AbstractEmailService):
            async def send(self, msg):
                pass

            async def send_welcome(self, to, name):
                pass

            async def send_payment_overdue(self, to, cn, dd, amt):
                return await super().send_payment_overdue(to, cn, dd, amt)

            async def send_account_deactivated(self, to, cn):
                pass

            async def send_password_reset(self, to, token):
                pass

        with pytest.raises(NotImplementedError):
            await Stub().send_payment_overdue("a@b.com", "Corp", "2026-01-01", 100.0)

    async def test_send_account_deactivated_raises(self) -> None:
        """Cobre o raise NotImplementedError de send_account_deactivated."""
        import pytest
        from shared_core.adapters.email_services.abstract_email import (
            AbstractEmailService,
        )

        class Stub(AbstractEmailService):
            async def send(self, msg):
                pass

            async def send_welcome(self, to, name):
                pass

            async def send_payment_overdue(self, to, cn, dd, amt):
                pass

            async def send_account_deactivated(self, to, cn):
                return await super().send_account_deactivated(to, cn)

            async def send_password_reset(self, to, token):
                pass

        with pytest.raises(NotImplementedError):
            await Stub().send_account_deactivated("a@b.com", "Corp")

    async def test_send_password_reset_raises(self) -> None:
        """Cobre o raise NotImplementedError de send_password_reset."""
        import pytest
        from shared_core.adapters.email_services.abstract_email import (
            AbstractEmailService,
        )

        class Stub(AbstractEmailService):
            async def send(self, msg):
                pass

            async def send_welcome(self, to, name):
                pass

            async def send_payment_overdue(self, to, cn, dd, amt):
                pass

            async def send_account_deactivated(self, to, cn):
                pass

            async def send_password_reset(self, to, token):
                return await super().send_password_reset(to, token)

        with pytest.raises(NotImplementedError):
            await Stub().send_password_reset("a@b.com", "token123")


class TestBillingDataClasses:
    """Testes para os data classes de billing."""

    def test_billing_customer(self) -> None:
        """Verifica a criação de BillingCustomer com campos corretos."""
        c = BillingCustomer(external_id="ext_1", company_id=_COMPANY_ID, email="e@e.com")
        assert c.external_id == "ext_1"
        assert c.company_id == _COMPANY_ID

    def test_subscription_result(self) -> None:
        """Verifica a criação de SubscriptionResult com campos corretos."""
        s = SubscriptionResult(
            subscription_id="sub_1", customer_id="cust_1", status="active"
        )
        assert s.subscription_id == "sub_1"
        assert s.current_period_end is None

    def test_charge_result(self) -> None:
        """Verifica a criação de ChargeResult com campos corretos."""
        r = ChargeResult(
            charge_id="ch_1", amount=10.0, currency="brl", status="succeeded", paid=True
        )
        assert r.paid is True


class TestFakeBillingService:
    """Testes para o FakeBillingService."""

    async def test_create_customer(self) -> None:
        """Verifica que create_customer cria um cliente fake corretamente."""
        svc = FakeBillingService()
        customer = await svc.create_customer(_COMPANY_ID, "e@e.com", "Test")
        assert customer.company_id == _COMPANY_ID
        assert customer.email == "e@e.com"
        assert customer.external_id.startswith("fake_cus_")
        assert len(svc.customers) == 1

    async def test_create_subscription(self) -> None:
        """Verifica que create_subscription cria uma assinatura fake corretamente."""
        svc = FakeBillingService()
        result = await svc.create_subscription("cust_ext_1", "price_1")
        assert result.status == "active"
        assert result.customer_id == "cust_ext_1"
        assert result.subscription_id.startswith("fake_sub_")
        assert len(svc.subscriptions) == 1

    async def test_cancel_subscription(self) -> None:
        """Verifica que cancel_subscription cancela a assinatura corretamente."""
        svc = FakeBillingService()
        result = await svc.cancel_subscription("sub_1")
        assert result is True
        assert "sub_1" in svc.cancelled_subscriptions

    async def test_charge_now(self) -> None:
        """Verifica que charge_now realiza a cobrança fake corretamente."""
        svc = FakeBillingService()
        result = await svc.charge_now("cust_ext_1", 1999, "brl", "Test charge")
        assert result.paid is True
        assert result.amount == 19.99
        assert result.currency == "brl"
        assert result.status == "succeeded"
        assert len(svc.charges) == 1

    async def test_get_subscription_status_active(self) -> None:
        """Verifica que get_subscription_status retorna 'active' por padrão."""
        svc = FakeBillingService()
        status = await svc.get_subscription_status("sub_1")
        assert status == "active"

    async def test_get_subscription_status_canceled(self) -> None:
        """Verifica que get_subscription_status retorna 'canceled' após cancelamento."""
        svc = FakeBillingService()
        await svc.cancel_subscription("sub_1")
        status = await svc.get_subscription_status("sub_1")
        assert status == "canceled"


class TestEmailDataClasses:
    """Testes para os data classes de email."""

    def test_email_message(self) -> None:
        """Verifica a criação de EmailMessage com campos corretos."""
        m = EmailMessage(to="a@b.com", subject="Test", body_html="<p>Hi</p>")
        assert m.to == "a@b.com"
        assert m.body_text == ""
        assert m.from_email == "noreply@gestao.app"
        assert m.reply_to is None

    def test_email_result(self) -> None:
        """Verifica a criação de EmailResult com campos corretos."""
        r = EmailResult(success=True, message_id="msg_1")
        assert r.success is True
        assert r.error is None


class TestFakeEmailService:
    """Testes para o FakeEmailService."""

    async def test_send(self) -> None:
        """Verifica que send envia email fake corretamente."""
        svc = FakeEmailService()
        msg = EmailMessage(to="a@b.com", subject="Test", body_html="<p>Hi</p>")
        result = await svc.send(msg)
        assert result.success is True
        assert result.message_id.startswith("fake_msg_")
        assert len(svc.sent) == 1

    async def test_send_welcome(self) -> None:
        """Verifica que send_welcome envia email de boas-vindas corretamente."""
        svc = FakeEmailService()
        result = await svc.send_welcome("user@test.com", "João")
        assert result.success is True
        assert len(svc.sent) == 1
        assert "Bem-vindo" in svc.sent[0].subject

    async def test_send_payment_overdue(self) -> None:
        """Verifica que send_payment_overdue envia email de atraso corretamente."""
        svc = FakeEmailService()
        result = await svc.send_payment_overdue(
            "admin@test.com", "Test Corp", "2026-03-01", 199.99
        )
        assert result.success is True
        assert "atraso" in svc.sent[0].subject

    async def test_send_account_deactivated(self) -> None:
        """Verifica que send_account_deactivated envia email de suspensão corretamente."""
        svc = FakeEmailService()
        result = await svc.send_account_deactivated("admin@test.com", "Test Corp")
        assert result.success is True
        assert "suspensa" in svc.sent[0].subject

    async def test_send_password_reset(self) -> None:
        """Verifica que send_password_reset envia email de redefinição corretamente."""
        svc = FakeEmailService()
        result = await svc.send_password_reset("user@test.com", "reset_token_123")
        assert result.success is True
        assert "Redefinição" in svc.sent[0].subject
        assert "reset_token_123" in svc.sent[0].body_html
