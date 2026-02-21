"""Módulo do agregado User."""

from dataclasses import dataclass
from datetime import date
from uuid import UUID

import uuid7

from shared_core.domain.value_objects.address import Address
from shared_core.domain.value_objects.enums import AuditConstant, EntityType
from shared_core.domain.events.user import (
    UserCreated,
    UserDeleted,
    UserUpdated,
)
from messagebus.entities import Aggregate, OperationType
from shared_core.security import UserSecurity


@dataclass(kw_only=True)
class User(Aggregate, UserSecurity):
    """
    Agregado que representa um usuário no domínio.

    Os campos de endereço são armazenados de forma plana para compatibilidade
    com o mapeamento ORM. O endereço é exposto como value object via propriedade.
    """

    id: UUID
    company: UUID
    email: str
    cpf: str
    name: str
    phone: str
    street: str
    number: str
    zip_code: str
    district: str
    city: str
    state: str
    country: str
    admin: bool
    complement: str | None = None
    is_owner: bool = False
    birth_date: date | None = None

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def address(self) -> Address:
        """
        Retorna o endereço do usuário como value object imutável.

        Returns:
            Instância de Address construída a partir dos campos planos.
        """
        return Address(
            street=self.street,
            number=self.number,
            zip_code=self.zip_code,
            district=self.district,
            city=self.city,
            state=self.state,
            country=self.country,
            complement=self.complement,
        )

    @staticmethod
    def create_aggregate(
        company: UUID,
        email: str,
        cpf: str,
        password: str,
        name: str,
        phone: str,
        address: Address,
        active: bool = True,
        admin: bool = False,
        is_owner: bool = False,
        birth_date: date | None = None,
    ) -> "User":
        """
        Cria uma nova instância do agregado User.

        Args:
            company: ID da empresa associada.
            email: Email do usuário.
            cpf: CPF do usuário.
            password: Senha do usuário.
            name: Nome completo do usuário.
            phone: Telefone de contato do usuário.
            address: Endereço completo do usuário como value object.
            active: Se o usuário está ativo.
            admin: Se o usuário é administrador.
            is_owner: Se o usuário é o proprietário da empresa.
            birth_date: Data de nascimento (opcional).

        Returns:
            Nova instância de User com ID gerado.
        """
        return User(
            id=uuid7.create(),
            company=company,
            email=email,
            cpf=cpf,
            _password_hash=UserSecurity.encrypt_password(password),
            name=name,
            phone=phone,
            street=address.street,
            number=address.number,
            zip_code=address.zip_code,
            district=address.district,
            city=address.city,
            state=address.state,
            country=address.country,
            complement=address.complement,
            active=active,
            admin=admin,
            is_owner=is_owner,
            birth_date=birth_date,
        )

    def create(self, user_id: UUID | None = None) -> None:
        """Marca o agregado para inserção e emite evento de criação."""
        self._operation_type = OperationType.INSERT
        self._set_create_audit(user_id)

        self.add_event(
            UserCreated(
                id=self.id,
                company=self.company,
                entity_type=EntityType.USER,
                new_data={
                    "email": self.email,
                    "cpf": self.cpf,
                    "name": self.name,
                    "active": self.active,
                    "admin": self.admin,
                    "is_owner": self.is_owner,
                },
            )
        )

    def update(
        self,
        email: str | None = None,
        password: str | None = None,
        active: bool | None = None,
        admin: bool | None = None,
        is_owner: bool | None = None,
        name: str | None = None,
        phone: str | None = None,
        birth_date: date | None = None,
        address: Address | None = None,
        user_id: UUID | None = None,
    ) -> None:
        """
        Atualiza os dados do usuário e emite evento de atualização.

        Ao passar um novo endereço, todos os campos de endereço são substituídos.

        Args:
            email: Novo email (opcional).
            password: Nova senha (opcional).
            active: Novo status de ativação (opcional).
            admin: Novo status de administrador (opcional).
            is_owner: Novo status de proprietário (opcional).
            name: Novo nome completo (opcional).
            phone: Novo telefone (opcional).
            birth_date: Nova data de nascimento (opcional).
            address: Novo endereço completo como value object (opcional).
            user_id: ID do usuário que está realizando a atualização (opcional).
        """
        self._operation_type = OperationType.UPDATE
        self._set_update_audit(user_id)

        old_data: dict = {}
        new_data: dict = {}

        self._track_change(old_data, new_data, "email", email)
        self._track_change(old_data, new_data, "active", active)
        self._track_change(old_data, new_data, "admin", admin)
        self._track_change(old_data, new_data, "is_owner", is_owner)
        self._track_change(old_data, new_data, "name", name)
        self._track_change(old_data, new_data, "phone", phone)
        self._track_change(
            old_data, new_data, "birth_date", str(birth_date) if birth_date else None
        )

        if address is not None:
            old_data["address"] = self.address.to_dict()
            new_data["address"] = address.to_dict()
            self.street = address.street
            self.number = address.number
            self.zip_code = address.zip_code
            self.district = address.district
            self.city = address.city
            self.state = address.state
            self.country = address.country
            self.complement = address.complement

        if password is not None:
            new_data["password"] = AuditConstant.REDACTED_PASSWORD
            self._password_hash = self.encrypt_password(password)

        self.add_event(
            UserUpdated(
                id=self.id,
                company=self.company,
                entity_type=EntityType.USER,
                old_data=old_data,
                new_data=new_data,
            )
        )

    def deactivate(self, user_id: UUID | None = None) -> None:
        """
        Inativa o usuário sem soft delete (para casos de atraso de pagamento).

        Args:
            user_id: ID do usuário que está realizando a inativação (opcional).
        """
        self._operation_type = OperationType.UPDATE
        self._set_update_audit(user_id)
        self.active = False

        self.add_event(
            UserUpdated(
                id=self.id,
                company=self.company,
                entity_type=EntityType.USER,
                old_data={"active": True},
                new_data={"active": False},
            )
        )

    def delete(self, user_id: UUID | None = None) -> None:
        """Marca o agregado como deletado (soft delete) e emite evento de exclusão."""
        self._operation_type = OperationType.DELETE

        old_data = {
            "email": self.email,
            "cpf": self.cpf,
            "active": self.active,
            "admin": self.admin,
        }

        self._set_delete_audit(user_id)

        self.add_event(
            UserDeleted(
                id=self.id,
                company=self.company,
                entity_type=EntityType.USER,
                old_data=old_data,
            )
        )


@dataclass(kw_only=True)
class PublicUser(Aggregate, UserSecurity):
    """Agregado que representa um usuário público (dados criptografados) no domínio."""

    id: UUID
    company: UUID
    email_encrypted: bytes
    email_hash: str

    def __hash__(self) -> int:
        return hash(self.id)

    @classmethod
    def create_registration_aggregate(
        cls,
        user: User,
    ) -> "PublicUser":
        """
        Cria um agregado PublicUser a partir de um usuário privado para cadastro.

        Args:
            user: Agregado User de origem.

        Returns:
            Nova instância de PublicUser com email criptografado e hash.
        """
        encrypted_email = cls.encrypt_email(user.email)
        email_hash = cls.hash_email(user.email)

        return PublicUser(
            id=user.id,
            company=user.company,
            email_encrypted=encrypted_email,
            email_hash=email_hash,
            _password_hash=user.password_hash,
            active=user.active,
        )

    def register(self) -> None:
        """Marca o agregado para inserção no banco de dados."""
        self._operation_type = OperationType.INSERT

    def update(self, email: str, password: str, active: bool) -> None:
        """
        Atualiza os dados do usuário público.

        Args:
            email: Novo email (será criptografado e hasheado).
            password: Novo hash da senha.
            active: Novo status de ativação.
        """
        self._operation_type = OperationType.UPDATE

        self.email_encrypted = self.encrypt_email(email)
        self.email_hash = self.hash_email(email)
        self._password_hash = password
        self.active = active

    def remove(self) -> None:
        """Marca o agregado como deletado (soft delete)."""
        self._operation_type = OperationType.DELETE
        self._set_delete_audit(user_id=None)
