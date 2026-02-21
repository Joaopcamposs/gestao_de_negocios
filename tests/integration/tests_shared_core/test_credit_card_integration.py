"""Testes de integração para o fluxo de CreditCard."""

from uuid import UUID

import pytest

from shared_core.bootstrap import bootstrap
from shared_core.domain.commands.company import CreateCompany
from shared_core.domain.commands.credit_card import CreateCreditCard, DeleteCreditCard
from shared_core.domain.commands.user import CreateUser
from shared_core.domain.excecoes import CreditCardNotFound
from shared_core.domain.value_objects.address import Address

_TEST_ADDRESS = Address(
    street="Rua das Flores",
    number="123",
    zip_code="01310100",
    district="Bela Vista",
    city="São Paulo",
    state="SP",
    country="Brasil",
)


async def _create_company(
    legal_name: str, email: str, cpf: str = "12345678901"
) -> tuple[UUID, str]:
    """Helper para criar empresa."""
    import uuid7

    schema = str(uuid7.create())
    bus = bootstrap(schema=schema, create_schema=True, raise_event_errors=True)
    company_id = await bus.handle(
        CreateCompany(
            legal_name=legal_name,
            responsible_name="Test User",
            active=True,
            cpf=cpf,
            email=email,
            password="secret123",
            should_create_user=True,
        )
    )
    return company_id, schema


async def _create_user(company_id: UUID, email: str, cpf: str, schema: str) -> UUID:
    """Helper para criar usuário."""
    bus = bootstrap(schema=schema, raise_event_errors=True)
    return await bus.handle(
        CreateUser(
            company=company_id,
            email=email,
            cpf=cpf,
            password="secret123",
            name="Test User",
            phone="11999999999",
            address=_TEST_ADDRESS,
            active=True,
            admin=False,
        )
    )


async def _create_card(
    user_id: UUID, schema: str, number: str = "4111111111111111"
) -> UUID:
    """Helper para criar cartão de crédito."""
    bus = bootstrap(schema=schema, raise_event_errors=True)
    return await bus.handle(
        CreateCreditCard(
            user_id=user_id,
            number=number,
            expiry="12/28",
            cvv="123",
            cpf="12345678901",
            holder_name="John Doe",
        )
    )


class TestCreateCreditCard:
    """Testes de integração para criação de cartão de crédito."""

    async def test_create_credit_card_returns_uuid(self, engine) -> None:
        """Verifica que criar cartão retorna UUID válido."""
        company_id, schema = await _create_company("CC Create Corp", "cccreate@test.com")
        user_id = await _create_user(company_id, "ccuser@test.com", "11122233344", schema)

        card_id = await _create_card(user_id, schema)

        assert isinstance(card_id, UUID)

    async def test_create_multiple_cards_for_same_user(self, engine) -> None:
        """Verifica que um usuário pode ter múltiplos cartões."""
        company_id, schema = await _create_company("CC Multi Corp", "ccmulti@test.com")
        user_id = await _create_user(
            company_id, "ccmultiuser@test.com", "22233344455", schema
        )

        card_id_1 = await _create_card(user_id, schema, number="4111111111111111")
        card_id_2 = await _create_card(user_id, schema, number="5555555555554444")

        assert card_id_1 != card_id_2
        assert isinstance(card_id_1, UUID)
        assert isinstance(card_id_2, UUID)

    async def test_create_card_stores_encrypted_data(self, engine) -> None:
        """Verifica que o cartão é criado com dados criptografados (não armazena texto puro)."""
        from shared_core.adapters.repository.domain_repo.credit_card import (
            CreditCardDomainRepo,
        )
        from shared_core.domains import Domain

        company_id, schema = await _create_company(
            "CC Encrypt Corp", "ccencrypt@test.com"
        )
        user_id = await _create_user(
            company_id, "ccencryptuser@test.com", "33344455566", schema
        )
        card_id = await _create_card(user_id, schema, number="4111111111111111")

        bus = bootstrap(schema=schema, raise_event_errors=True)
        async with bus.uow(Domain.credit_card) as uow:
            repo: CreditCardDomainRepo = uow.domain_repo
            card = await repo.get_by_id(card_id=card_id)

        assert card.number_encrypted != b"4111111111111111"
        decrypted = card.decrypt_fields()
        assert decrypted["number"] == "4111111111111111"


class TestDeleteCreditCard:
    """Testes de integração para exclusão de cartão de crédito."""

    async def test_delete_credit_card_soft_deletes(self, engine) -> None:
        """Verifica que deletar cartão realiza soft delete."""
        from shared_core.adapters.repository.domain_repo.credit_card import (
            CreditCardDomainRepo,
        )
        from shared_core.domains import Domain

        company_id, schema = await _create_company("CC Delete Corp", "ccdelete@test.com")
        user_id = await _create_user(
            company_id, "ccdeleteuser@test.com", "44455566677", schema
        )
        card_id = await _create_card(user_id, schema)

        bus = bootstrap(schema=schema, raise_event_errors=True)
        await bus.handle(DeleteCreditCard(card_id=card_id))

        async with bus.uow(Domain.credit_card) as uow:
            repo: CreditCardDomainRepo = uow.domain_repo
            with pytest.raises(CreditCardNotFound):
                await repo.get_by_id(card_id=card_id)
