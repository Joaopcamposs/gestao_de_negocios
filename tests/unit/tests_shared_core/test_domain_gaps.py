"""Testes unitários para cobrir gaps no domínio."""

from datetime import timedelta

import uuid7

from messagebus.entities import OperationType
from shared_core.domain.aggregate.company import Company
from shared_core.domain.aggregate.user import User
from shared_core.domain.value_objects.address import Address
from shared_core.entrypoints.schemas.user import AddressSchema


_COMPANY_ID = uuid7.create()
_USER_ID = uuid7.create()


class TestCompanyDeactivate:
    def test_deactivate_sets_active_false(self) -> None:
        company = Company.create_aggregate(
            legal_name="Test",
            trade_name="T",
            responsible_name="R",
            email="e@e.com",
            cpf="12345678901",
            cnpj=None,
            active=True,
        )

        company.deactivate(user_id=_USER_ID)

        assert company.active is False
        assert company.operation_type == OperationType.UPDATE
        assert len(company.events) == 1

    def test_first_company_id_property(self) -> None:
        company = Company.create_aggregate(
            legal_name="Test",
            trade_name="T",
            responsible_name="R",
            email="e@e.com",
            cpf="12345678901",
            cnpj=None,
            active=True,
            _first_company_id=_COMPANY_ID,
        )

        assert company.first_company_id == _COMPANY_ID

    def test_first_company_id_none(self) -> None:
        company = Company.create_aggregate(
            legal_name="Test",
            trade_name="T",
            responsible_name="R",
            email="e@e.com",
            cpf="12345678901",
            cnpj=None,
            active=True,
        )

        assert company.first_company_id is None


class TestUserDeactivate:
    def test_deactivate_sets_active_false(self) -> None:
        address = Address(
            street="Rua A",
            number="1",
            zip_code="12345000",
            district="Centro",
            city="SP",
            state="SP",
            country="BR",
        )
        user = User.create_aggregate(
            company=_COMPANY_ID,
            email="user@test.com",
            cpf="12345678901",
            password="pass123",
            name="Test",
            phone="11999999999",
            address=address,
            active=True,
        )

        user.deactivate(user_id=_USER_ID)

        assert user.active is False
        assert user.operation_type == OperationType.UPDATE
        assert len(user.events) == 1


class TestCreditCardDecrypt:
    def test_decrypt_fields(self) -> None:
        """Testa decrypt_fields na entidade CreditCard."""
        from shared_core.security import UserSecurity

        card_key = UserSecurity.generate_card_key()
        encrypted_key = UserSecurity.encrypt_card_key(card_key)

        number_enc = UserSecurity.encrypt_card_field("4111111111111111", card_key)
        expiry_enc = UserSecurity.encrypt_card_field("12/30", card_key)
        cvv_enc = UserSecurity.encrypt_card_field("123", card_key)
        cpf_enc = UserSecurity.encrypt_card_field("12345678901", card_key)
        holder_enc = UserSecurity.encrypt_card_field("Test", card_key)

        from shared_core.domain.entities.credit_card import CreditCard

        card = CreditCard(
            id=uuid7.create(),
            user_id=_USER_ID,
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


class TestAddressSchemaToValueObject:
    def test_to_value_object(self) -> None:
        schema = AddressSchema(
            street="Rua B",
            number="200",
            zip_code="54321000",
            district="Vila",
            city="RJ",
            state="RJ",
            country="BR",
            complement="Apt 10",
        )

        addr = schema.to_value_object()

        assert addr.street == "Rua B"
        assert addr.number == "200"
        assert addr.complement == "Apt 10"


class TestSecurityGenerateToken:
    def test_generate_token_with_custom_expiry(self) -> None:
        """Testa generate_token com expires_delta customizado."""
        address = Address(
            street="Rua A",
            number="1",
            zip_code="12345000",
            district="Centro",
            city="SP",
            state="SP",
            country="BR",
        )
        user = User.create_aggregate(
            company=_COMPANY_ID,
            email="token@test.com",
            cpf="12345678901",
            password="pass123",
            name="Token User",
            phone="11999999999",
            address=address,
        )

        from shared_core.security import UserSecurity

        encrypted_email = UserSecurity.encrypt_email("token@test.com")

        token = user.generate_token(
            company_id=_COMPANY_ID,
            encrypted_email=encrypted_email,
            expires_delta=timedelta(minutes=5),
        )

        assert token.access_token is not None
        assert token.token_type == "bearer"


class TestCreateCompanyCommand:
    def test_first_company_id_property(self) -> None:
        """Testa a propriedade first_company_id do CreateCompany."""
        from shared_core.domain.commands.company import CreateCompany

        cmd = CreateCompany(
            legal_name="Test",
            responsible_name="R",
            active=True,
            cpf="12345678901",
            email="e@e.com",
            password="pass",
        )
        assert cmd.first_company_id is None


class TestUserEntityAddress:
    def test_user_entity_address_property(self) -> None:
        """Testa a propriedade address da entidade de leitura User."""
        from shared_core.domain.entities.user import User as UserEntity

        user = UserEntity(
            id=uuid7.create(),
            company=_COMPANY_ID,
            email="test@t.com",
            cpf="12345678901",
            name="T",
            phone="11",
            street="R",
            number="1",
            zip_code="12345",
            district="D",
            city="C",
            state="S",
            country="BR",
            admin=False,
        )

        addr = user.address
        assert addr.street == "R"
        assert addr.city == "C"
