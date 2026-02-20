"""Módulo da entidade de leitura CreditCard."""

from dataclasses import dataclass
from uuid import UUID

from messagebus.entities import AuditReadBase
from shared_core.security import UserSecurity


@dataclass(frozen=True, kw_only=True)
class CreditCard(AuditReadBase):
    """Entidade de leitura que representa um cartão de crédito (dados criptografados)."""

    id: UUID
    user_id: UUID
    card_key_encrypted: bytes
    number_encrypted: bytes
    expiry_encrypted: bytes
    cvv_encrypted: bytes
    cpf_encrypted: bytes
    holder_name_encrypted: bytes

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
