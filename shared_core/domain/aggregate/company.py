"""Módulo do agregado Company."""

from dataclasses import dataclass
from uuid import UUID

import uuid7

from datetime import datetime

from shared_core.consts import ADMIN_USER_PREFIX
from shared_core.domain.value_objects.enums import EntityType
from shared_core.domain.events.company import (
    CompanyCreated,
    CompanyDeleted,
    CompanyPaymentStatusUpdated,
    CompanyUpdated,
)
from shared_core.domain.events.user import (
    TimeToCreateCompanyAdminUser,
    TimeToCreateInitialCompanyUser,
)
from libs.basic_types import Email
from messagebus.entities import Aggregate, OperationType


@dataclass(kw_only=True)
class Company(Aggregate):
    """Agregado que representa uma empresa no domínio."""

    id: UUID
    legal_name: str
    responsible_name: str
    email: str
    cpf: str
    trade_name: str | None = None
    cnpj: str | None = None
    payment_up_to_date: bool = True
    last_payment_date: datetime | None = None

    _first_company_id: UUID | None = None

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def first_company_id(self) -> UUID | None:
        return self._first_company_id

    @staticmethod
    def create_aggregate(
        legal_name: str,
        trade_name: str | None,
        responsible_name: str,
        email: str,
        cpf: str,
        cnpj: str | None,
        active: bool,
        _first_company_id: UUID | None = None,
    ) -> "Company":
        """
        Cria uma nova instância do agregado Company.

        Args:
            legal_name: Razão social da empresa.
            trade_name: Nome fantasia da empresa (opcional).
            responsible_name: Nome do responsável.
            email: Email de contato da empresa.
            cpf: CPF do responsável.
            cnpj: CNPJ da empresa (opcional).
            active: Se a empresa está ativa.
            _first_company_id: ID fixo para a primeira empresa (opcional).

        Returns:
            Nova instância de Company com ID gerado.
        """
        company_id = _first_company_id or uuid7.create()

        return Company(
            id=company_id,
            legal_name=legal_name,
            trade_name=trade_name,
            responsible_name=responsible_name,
            email=email,
            cpf=cpf,
            cnpj=cnpj,
            active=active,
            payment_up_to_date=True,
            _first_company_id=_first_company_id,
        )

    def create(
        self,
        password: str,
        should_create_user: bool = True,
        user_id: UUID | None = None,
    ) -> None:
        """
        Marca o agregado para inserção e emite eventos de criação.

        Emite CompanyCreated e, se should_create_user for True,
        TimeToCreateInitialCompanyUser. Para empresas que não são a primeira,
        também emite TimeToCreateCompanyAdminUser.

        Args:
            password: Senha para o usuário inicial da empresa.
            should_create_user: Se True, emite eventos para criar usuários.
            user_id: ID do usuário que está criando a empresa (opcional).
        """
        self._operation_type = OperationType.INSERT
        self._set_create_audit(user_id)

        new_data = {
            "legal_name": self.legal_name,
            "trade_name": self.trade_name,
            "responsible_name": self.responsible_name,
            "email": self.email,
            "cpf": self.cpf,
            "cnpj": self.cnpj,
            "active": self.active,
        }

        self.add_event(
            CompanyCreated(
                id=self.id,
                entity_type=EntityType.COMPANY,
                new_data=new_data,
            )
        )

        if not should_create_user:
            return

        self.add_event(
            TimeToCreateInitialCompanyUser(
                name=self.responsible_name,
                email=self.email,
                cpf=self.cpf,
                password=password,
                active=True,
                admin=True,
                company=self.id,
            )
        )
        if self._first_company_id is None:
            admin_user_email = Email(f"{ADMIN_USER_PREFIX}@{self.id!s}.com")
            self.add_event(
                TimeToCreateCompanyAdminUser(company=self.id, email=admin_user_email)
            )

    def update(
        self,
        legal_name: str | None = None,
        trade_name: str | None = None,
        responsible_name: str | None = None,
        email: str | None = None,
        active: bool | None = None,
        user_id: UUID | None = None,
    ) -> None:
        """
        Atualiza os dados da empresa e emite evento de atualização.

        Args:
            legal_name: Nova razão social (opcional).
            trade_name: Novo nome fantasia (opcional).
            responsible_name: Novo nome do responsável (opcional).
            email: Novo email (opcional).
            active: Novo status de ativação (opcional).
            user_id: ID do usuário que está realizando a atualização (opcional).
        """
        self._operation_type = OperationType.UPDATE
        self._set_update_audit(user_id)

        old_data: dict = {}
        new_data: dict = {}

        self._track_change(old_data, new_data, "legal_name", legal_name)
        self._track_change(old_data, new_data, "trade_name", trade_name)
        self._track_change(old_data, new_data, "responsible_name", responsible_name)
        self._track_change(old_data, new_data, "email", email)
        self._track_change(old_data, new_data, "active", active)

        self.add_event(
            CompanyUpdated(
                id=self.id,
                entity_type=EntityType.COMPANY,
                old_data=old_data,
                new_data=new_data,
            )
        )

    def update_payment_status(
        self,
        payment_up_to_date: bool,
        last_payment_date: "datetime | None" = None,
        user_id: UUID | None = None,
    ) -> None:
        """
        Atualiza o status de pagamento da empresa e emite evento.

        Args:
            payment_up_to_date: Se True, pagamento está em dia; se False, está em atraso.
            last_payment_date: Data do último pagamento realizado (opcional).
            user_id: ID do usuário que está realizando a atualização (opcional).
        """
        self._operation_type = OperationType.UPDATE
        self._set_update_audit(user_id)

        old_data = {"payment_up_to_date": self.payment_up_to_date}
        self.payment_up_to_date = payment_up_to_date
        if last_payment_date is not None:
            self.last_payment_date = last_payment_date
        new_data = {"payment_up_to_date": self.payment_up_to_date}

        self.add_event(
            CompanyPaymentStatusUpdated(
                id=self.id,
                entity_type=EntityType.COMPANY,
                old_data=old_data,
                new_data=new_data,
            )
        )

    def deactivate(self, user_id: UUID | None = None) -> None:
        """
        Inativa a empresa sem soft delete (para casos de atraso de pagamento).

        Args:
            user_id: ID do usuário que está realizando a inativação (opcional).
        """
        self._operation_type = OperationType.UPDATE
        self._set_update_audit(user_id)
        self.active = False

        self.add_event(
            CompanyUpdated(
                id=self.id,
                entity_type=EntityType.COMPANY,
                old_data={"active": True},
                new_data={"active": False},
            )
        )

    def delete(self, user_id: UUID | None = None) -> None:
        """Marca o agregado como deletado (soft delete) e emite evento de exclusão."""
        self._operation_type = OperationType.DELETE

        old_data = {
            "legal_name": self.legal_name,
            "trade_name": self.trade_name,
            "responsible_name": self.responsible_name,
            "email": self.email,
            "cpf": self.cpf,
            "cnpj": self.cnpj,
            "active": self.active,
        }

        self._set_delete_audit(user_id)

        self.add_event(
            CompanyDeleted(
                id=self.id,
                entity_type=EntityType.COMPANY,
                old_data=old_data,
            )
        )
