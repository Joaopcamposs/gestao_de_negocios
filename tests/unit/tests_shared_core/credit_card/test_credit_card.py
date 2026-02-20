"""Testes unitários para o domínio de CreditCard no shared_core.

Cobre o agregado CreditCard, criptografia, comandos, eventos,
entidade de leitura e schemas.
"""

from uuid import UUID

import uuid7

from messagebus.entities import Aggregate, OperationType
from shared_core.domain.aggregate.credit_card import CreditCard
from shared_core.domain.commands.credit_card import CreateCreditCard, DeleteCreditCard
from shared_core.domain.entities.credit_card import CreditCard as CreditCardEntity
from shared_core.domain.events.credit_card import CreditCardCreated, CreditCardDeleted
from shared_core.domain.value_objects.enums import EntityType
from shared_core.entrypoints.schemas.credit_card import (
    CreateCreditCardSchema,
    ReadCreditCardSchema,
)
from shared_core.security import UserSecurity


_TEST_USER_ID = uuid7.create()


class TestCreditCardAggregate:
    """Testes para o agregado CreditCard."""

    def _make_card(self, **overrides) -> CreditCard:
        """Função auxiliar para criar um agregado CreditCard."""
        defaults = dict(
            user_id=_TEST_USER_ID,
            number="4111111111111111",
            expiry="12/28",
            cvv="123",
            cpf="12345678901",
            holder_name="John Doe",
        )
        defaults.update(overrides)
        return CreditCard.create_aggregate(**defaults)

    def test_create_aggregate_returns_credit_card_with_uuid(self) -> None:
        """Verifica que create_aggregate retorna um CreditCard com UUID válido."""
        card = self._make_card()

        assert isinstance(card.id, UUID)
        assert card.user_id == _TEST_USER_ID
        assert isinstance(card.card_key_encrypted, bytes)
        assert isinstance(card.number_encrypted, bytes)
        assert isinstance(card.expiry_encrypted, bytes)
        assert isinstance(card.cvv_encrypted, bytes)
        assert isinstance(card.cpf_encrypted, bytes)
        assert isinstance(card.holder_name_encrypted, bytes)

    def test_create_aggregate_generates_unique_ids(self) -> None:
        """Verifica que cada chamada gera um ID diferente."""
        card1 = self._make_card()
        card2 = self._make_card()

        assert card1.id != card2.id

    def test_create_aggregate_encrypts_fields(self) -> None:
        """Verifica que os campos sensíveis são criptografados."""
        card = self._make_card(number="4111111111111111")

        assert card.number_encrypted != b"4111111111111111"
        assert len(card.number_encrypted) > 0

    def test_decrypt_fields_returns_original_values(self) -> None:
        """Verifica que decrypt_fields retorna os valores originais."""
        card = self._make_card(
            number="4111111111111111",
            expiry="12/28",
            cvv="123",
            cpf="12345678901",
            holder_name="John Doe",
        )
        decrypted = card.decrypt_fields()

        assert decrypted["number"] == "4111111111111111"
        assert decrypted["expiry"] == "12/28"
        assert decrypted["cvv"] == "123"
        assert decrypted["cpf"] == "12345678901"
        assert decrypted["holder_name"] == "John Doe"

    def test_two_cards_with_same_data_have_different_ciphertexts(self) -> None:
        """Verifica que dois cartões com mesmos dados possuem cifragens diferentes."""
        card1 = self._make_card(number="4111111111111111")
        card2 = self._make_card(number="4111111111111111")

        assert card1.number_encrypted != card2.number_encrypted

    def test_credit_card_inherits_from_aggregate(self) -> None:
        """Verifica que CreditCard herda de Aggregate."""
        card = self._make_card()

        assert isinstance(card, Aggregate)

    def test_create_sets_insert_operation_type(self) -> None:
        """Verifica que create() define o tipo de operação como INSERT."""
        card = self._make_card()
        card.create()

        assert card._operation_type == OperationType.INSERT

    def test_create_emits_credit_card_created_event(self) -> None:
        """Verifica que create() emite o evento CreditCardCreated."""
        card = self._make_card()
        card.create()

        created_events = [e for e in card.events if isinstance(e, CreditCardCreated)]
        assert len(created_events) == 1
        assert created_events[0].id == card.id
        assert created_events[0].user_id == card.user_id
        assert created_events[0].entity_type == EntityType.CREDIT_CARD

    def test_create_sets_audit_fields(self) -> None:
        """Verifica que create() preenche created_at e created_by."""
        actor_id = uuid7.create()
        card = self._make_card()
        card.create(user_id=actor_id)

        assert card.created_at is not None
        assert card.created_by == actor_id

    def test_delete_sets_delete_operation_type(self) -> None:
        """Verifica que delete() define o tipo de operação como DELETE."""
        card = self._make_card()
        card.delete()

        assert card._operation_type == OperationType.DELETE
        assert card.is_deleted is True
        assert card.deleted_at is not None

    def test_delete_emits_credit_card_deleted_event(self) -> None:
        """Verifica que delete() emite o evento CreditCardDeleted."""
        card = self._make_card()
        card.delete()

        deleted_events = [e for e in card.events if isinstance(e, CreditCardDeleted)]
        assert len(deleted_events) == 1
        assert deleted_events[0].id == card.id
        assert deleted_events[0].entity_type == EntityType.CREDIT_CARD

    def test_hash_is_based_on_id(self) -> None:
        """Verifica que o hash é baseado no ID."""
        card = self._make_card()

        assert hash(card) == hash(card.id)


class TestCreditCardEncryption:
    """Testes para a criptografia de cartões de crédito em UserSecurity."""

    def test_generate_card_key_returns_32_bytes(self) -> None:
        """Verifica que generate_card_key retorna exatamente 32 bytes."""
        key = UserSecurity.generate_card_key()

        assert isinstance(key, bytes)
        assert len(key) == 32

    def test_generate_card_key_is_random(self) -> None:
        """Verifica que generate_card_key gera chaves únicas."""
        key1 = UserSecurity.generate_card_key()
        key2 = UserSecurity.generate_card_key()

        assert key1 != key2

    def test_encrypt_and_decrypt_card_key(self) -> None:
        """Verifica que encrypt_card_key e decrypt_card_key são reversíveis."""
        card_key = UserSecurity.generate_card_key()
        encrypted = UserSecurity.encrypt_card_key(card_key)
        decrypted = UserSecurity.decrypt_card_key(encrypted)

        assert decrypted == card_key

    def test_encrypt_card_key_generates_different_ciphertexts(self) -> None:
        """Verifica que encrypt_card_key gera cifras diferentes (nonce aleatório)."""
        card_key = UserSecurity.generate_card_key()
        enc1 = UserSecurity.encrypt_card_key(card_key)
        enc2 = UserSecurity.encrypt_card_key(card_key)

        assert enc1 != enc2

    def test_encrypt_and_decrypt_card_field(self) -> None:
        """Verifica que encrypt_card_field e decrypt_card_field são reversíveis."""
        card_key = UserSecurity.generate_card_key()
        value = "4111111111111111"
        encrypted = UserSecurity.encrypt_card_field(value, card_key)
        decrypted = UserSecurity.decrypt_card_field(encrypted, card_key)

        assert decrypted == value

    def test_encrypt_card_field_generates_different_ciphertexts(self) -> None:
        """Verifica que encrypt_card_field gera cifras diferentes (nonce aleatório)."""
        card_key = UserSecurity.generate_card_key()
        value = "4111111111111111"
        enc1 = UserSecurity.encrypt_card_field(value, card_key)
        enc2 = UserSecurity.encrypt_card_field(value, card_key)

        assert enc1 != enc2

    def test_decrypt_fields_on_entity(self) -> None:
        """Testa decrypt_fields na entidade CreditCard."""
        card_key = UserSecurity.generate_card_key()
        encrypted_key = UserSecurity.encrypt_card_key(card_key)

        number_enc = UserSecurity.encrypt_card_field("4111111111111111", card_key)
        expiry_enc = UserSecurity.encrypt_card_field("12/30", card_key)
        cvv_enc = UserSecurity.encrypt_card_field("123", card_key)
        cpf_enc = UserSecurity.encrypt_card_field("12345678901", card_key)
        holder_enc = UserSecurity.encrypt_card_field("Test", card_key)

        from shared_core.domain.entities.credit_card import CreditCard as CreditCardEntity

        card = CreditCardEntity(
            id=uuid7.create(),
            user_id=_TEST_USER_ID,
            card_key_encrypted=encrypted_key,
            number_encrypted=number_enc,
            expiry_encrypted=expiry_enc,
            cvv_encrypted=cvv_enc,
            cpf_encrypted=cpf_enc,
            holder_name_encrypted=holder_enc,
        )

        decrypted = card.decrypt_fields()

        assert decrypted["number"] == "4111111111111111"
        assert decrypted["expiry"] == "12/30"
        assert decrypted["cvv"] == "123"
        assert decrypted["cpf"] == "12345678901"
        assert decrypted["holder_name"] == "Test"


class TestCreditCardCommands:
    """Testes para os comandos de CreditCard."""

    def test_create_credit_card_command(self) -> None:
        """Verifica a criação do comando CreateCreditCard."""
        command = CreateCreditCard(
            user_id=_TEST_USER_ID,
            number="4111111111111111",
            expiry="12/28",
            cvv="123",
            cpf="12345678901",
            holder_name="John Doe",
        )

        assert command.user_id == _TEST_USER_ID
        assert command.number == "4111111111111111"
        assert command.expiry == "12/28"
        assert command.cvv == "123"
        assert command.cpf == "12345678901"
        assert command.holder_name == "John Doe"

    def test_delete_credit_card_command(self) -> None:
        """Verifica a criação do comando DeleteCreditCard."""
        card_id = uuid7.create()
        command = DeleteCreditCard(card_id=card_id)

        assert command.card_id == card_id


class TestCreditCardEvents:
    """Testes para os eventos de CreditCard."""

    def test_credit_card_created_event(self) -> None:
        """Verifica a criação do evento CreditCardCreated."""
        card_id = uuid7.create()
        user_id = uuid7.create()
        event = CreditCardCreated(
            id=card_id,
            user_id=user_id,
            entity_type=EntityType.CREDIT_CARD,
        )

        assert event.id == card_id
        assert event.user_id == user_id
        assert event.entity_type == EntityType.CREDIT_CARD

    def test_credit_card_deleted_event(self) -> None:
        """Verifica a criação do evento CreditCardDeleted."""
        card_id = uuid7.create()
        user_id = uuid7.create()
        event = CreditCardDeleted(
            id=card_id,
            user_id=user_id,
            entity_type=EntityType.CREDIT_CARD,
        )

        assert event.id == card_id
        assert event.user_id == user_id


class TestCreditCardEntity:
    """Testes para a entidade de leitura CreditCard."""

    def test_credit_card_entity_creation(self) -> None:
        """Verifica a criação da entidade CreditCard com todos os campos."""
        card_id = uuid7.create()
        user_id = uuid7.create()
        entity = CreditCardEntity(
            id=card_id,
            user_id=user_id,
            card_key_encrypted=b"encrypted_key",
            number_encrypted=b"encrypted_number",
            expiry_encrypted=b"encrypted_expiry",
            cvv_encrypted=b"encrypted_cvv",
            cpf_encrypted=b"encrypted_cpf",
            holder_name_encrypted=b"encrypted_name",
        )

        assert entity.id == card_id
        assert entity.user_id == user_id
        assert entity.number_encrypted == b"encrypted_number"


class TestCreditCardSchemas:
    """Testes para os schemas de CreditCard."""

    def test_create_credit_card_schema(self) -> None:
        """Verifica o schema de criação de cartão de crédito."""
        schema = CreateCreditCardSchema(
            number="4111111111111111",
            expiry="12/28",
            cvv="123",
            cpf="12345678901",
            holder_name="John Doe",
        )

        assert schema.number == "4111111111111111"
        assert schema.expiry == "12/28"
        assert schema.cvv == "123"
        assert schema.cpf == "12345678901"
        assert schema.holder_name == "John Doe"

    def test_read_credit_card_schema(self) -> None:
        """Verifica o schema de leitura de cartão de crédito."""
        card_id = uuid7.create()
        user_id = uuid7.create()
        schema = ReadCreditCardSchema(
            id=card_id,
            user_id=user_id,
            number="4111111111111111",
            expiry="12/28",
            cvv="123",
            cpf="12345678901",
            holder_name="John Doe",
        )

        assert schema.id == card_id
        assert schema.user_id == user_id
        assert schema.number == "4111111111111111"
        assert schema.holder_name == "John Doe"
