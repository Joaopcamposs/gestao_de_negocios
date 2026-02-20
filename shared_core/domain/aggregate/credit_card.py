"""Módulo do agregado CreditCard."""

from dataclasses import dataclass
from uuid import UUID

import uuid7

from shared_core.domain.value_objects.enums import EntityType
from shared_core.domain.events.credit_card import CreditCardCreated, CreditCardDeleted
from shared_core.security import UserSecurity
from messagebus.entities import Aggregate, OperationType


@dataclass(kw_only=True)
class CreditCard(Aggregate):
    """Agregado que representa um cartão de crédito (dados sensíveis criptografados)."""

    id: UUID
    user_id: UUID
    card_key_encrypted: bytes
    number_encrypted: bytes
    expiry_encrypted: bytes
    cvv_encrypted: bytes
    cpf_encrypted: bytes
    holder_name_encrypted: bytes

    def __hash__(self) -> int:
        return hash(self.id)

    @staticmethod
    def create_aggregate(
        user_id: UUID,
        number: str,
        expiry: str,
        cvv: str,
        cpf: str,
        holder_name: str,
    ) -> "CreditCard":
        """
        Cria uma nova instância do agregado CreditCard com campos criptografados.

        Args:
            user_id: ID do usuário proprietário do cartão.
            number: Número do cartão (será criptografado).
            expiry: Data de vencimento do cartão (será criptografado).
            cvv: Código de segurança do cartão (será criptografado).
            cpf: CPF do titular do cartão (será criptografado).
            holder_name: Nome do titular do cartão (será criptografado).

        Returns:
            Nova instância de CreditCard com dados criptografados.
        """
        card_key = UserSecurity.generate_card_key()
        card_key_encrypted = UserSecurity.encrypt_card_key(card_key)

        return CreditCard(
            id=uuid7.create(),
            user_id=user_id,
            card_key_encrypted=card_key_encrypted,
            number_encrypted=UserSecurity.encrypt_card_field(number, card_key),
            expiry_encrypted=UserSecurity.encrypt_card_field(expiry, card_key),
            cvv_encrypted=UserSecurity.encrypt_card_field(cvv, card_key),
            cpf_encrypted=UserSecurity.encrypt_card_field(cpf, card_key),
            holder_name_encrypted=UserSecurity.encrypt_card_field(holder_name, card_key),
        )

    def decrypt_fields(self) -> dict:
        """
        Descriptografa todos os campos sensíveis do cartão.

        Returns:
            Dicionário com os dados descriptografados do cartão.
        """
        card_key = UserSecurity.decrypt_card_key(self.card_key_encrypted)
        return {
            "number": UserSecurity.decrypt_card_field(self.number_encrypted, card_key),
            "expiry": UserSecurity.decrypt_card_field(self.expiry_encrypted, card_key),
            "cvv": UserSecurity.decrypt_card_field(self.cvv_encrypted, card_key),
            "cpf": UserSecurity.decrypt_card_field(self.cpf_encrypted, card_key),
            "holder_name": UserSecurity.decrypt_card_field(
                self.holder_name_encrypted, card_key
            ),
        }

    def create(self, user_id: UUID | None = None) -> None:
        """Marca o agregado para inserção e emite evento de criação."""
        self._operation_type = OperationType.INSERT
        self._set_create_audit(user_id)

        self.add_event(
            CreditCardCreated(
                id=self.id,
                user_id=self.user_id,
                entity_type=EntityType.CREDIT_CARD,
                new_data={"user_id": str(self.user_id)},
            )
        )

    def delete(self, user_id: UUID | None = None) -> None:
        """Marca o agregado como deletado (soft delete) e emite evento de exclusão."""
        self._operation_type = OperationType.DELETE
        self._set_delete_audit(user_id)

        self.add_event(
            CreditCardDeleted(
                id=self.id,
                user_id=self.user_id,
                entity_type=EntityType.CREDIT_CARD,
                old_data={"user_id": str(self.user_id)},
            )
        )
