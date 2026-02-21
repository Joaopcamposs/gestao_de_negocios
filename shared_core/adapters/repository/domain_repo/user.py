"""Módulo do repositório de domínio de User."""

from abc import abstractmethod
from datetime import date
from typing import Any
from uuid import UUID

from sqlalchemy import select

from shared_core.adapters.repository.mixins.public_user import PublicUserMixin
from shared_core.adapters.repository.mixins.upsert import UpsertMixin
from shared_core.domain.aggregate.user import User
from shared_core.domain.value_objects.address import Address
from shared_core.domain.excecoes import (
    UserAlreadyRegistered,
    UserNotFound,
)
from messagebus.entities import DomainRepository


class AbstractUserDomainRepo(DomainRepository):
    """Repositório abstrato de domínio para User."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.seen: set[User] = set()

    async def add(self, user: User) -> None:
        """
        Adiciona um usuário ao repositório e à lista de rastreados.

        Args:
            user: Agregado User a ser adicionado.
        """
        self.seen.add(user)
        await self._add(user)

    @abstractmethod
    async def _add(self, user: User) -> None:
        """Implementação interna de adição."""
        raise NotImplementedError

    async def remove(self, user: User) -> None:
        """
        Remove um usuário do repositório.

        Args:
            user: Agregado User a ser removido.
        """
        self.seen.add(user)
        await self._remove(user)

    @abstractmethod
    async def _remove(self, user: User) -> None:
        """Implementação interna de remoção."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> User:
        """
        Busca um usuário pelo email.

        Args:
            email: Email do usuário.

        Returns:
            Agregado User encontrado.
        """
        raise NotImplementedError()


class UserDomainRepo(AbstractUserDomainRepo, PublicUserMixin, UpsertMixin):
    """Implementação concreta do repositório de domínio de User."""

    @staticmethod
    def _build_aggregate(row: Any) -> User:
        """
        Constrói um agregado User a partir de uma linha retornada pelo ORM.

        Args:
            row: Linha mapeada pelo SQLAlchemy.

        Returns:
            Instância do agregado User.
        """
        return User(
            id=row.id,
            company=row.company,
            email=row.email,
            cpf=row.cpf,
            _password_hash=row.password_hash,
            name=row.name,
            phone=row.phone,
            street=row.street,
            number=row.number,
            zip_code=row.zip_code,
            complement=row.complement,
            district=row.district,
            city=row.city,
            state=row.state,
            country=row.country,
            active=row.active,
            admin=row.admin,
            is_owner=row.is_owner,
            birth_date=row.birth_date,
            created_at=row.created_at,
            created_by=row.created_by,
            updated_at=row.updated_at,
            updated_by=row.updated_by,
            deleted_at=row.deleted_at,
            deleted_by=row.deleted_by,
        )

    async def create_aggregate(
        self,
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
    ) -> User:
        """
        Cria um novo agregado User, verificando duplicidade de email.

        Args:
            company: ID da empresa associada.
            email: Email do usuário.
            cpf: CPF do usuário.
            password: Senha do usuário.
            name: Nome completo do usuário.
            phone: Telefone de contato do usuário.
            address: Endereço completo do usuário.
            active: Se o usuário está ativo.
            admin: Se o usuário é administrador.
            is_owner: Se o usuário é o proprietário da empresa.
            birth_date: Data de nascimento (opcional).

        Returns:
            Nova instância do agregado User.

        Raises:
            UserAlreadyRegistered: Se já existe usuário com o mesmo email.
        """
        async with self.session as session:
            existing_user = (
                await session.execute(
                    select(User).where(
                        User.email == email,
                        User.deleted_at.is_(None),
                    )
                )
            ).scalar_one_or_none()
            if existing_user:
                raise UserAlreadyRegistered

        return User.create_aggregate(
            company=company,
            email=email,
            cpf=cpf,
            password=password,
            name=name,
            phone=phone,
            address=address,
            active=active,
            admin=admin,
            is_owner=is_owner,
            birth_date=birth_date,
        )

    async def get_by_email(self, email: str) -> User:
        """
        Busca um usuário pelo email.

        Args:
            email: Email do usuário.

        Returns:
            Agregado User encontrado.

        Raises:
            UserNotFound: Se o usuário não for encontrado.
        """
        async with self.session as session:
            row = (
                await session.execute(
                    select(User).where(
                        User.email == email,
                        User.deleted_at.is_(None),
                    )
                )
            ).scalar_one_or_none()
            if not row:
                raise UserNotFound
        return self._build_aggregate(row)

    async def get_by_id(self, id: UUID) -> User:
        """
        Busca um usuário pelo ID.

        Args:
            id: UUID do usuário.

        Returns:
            Agregado User encontrado.

        Raises:
            UserNotFound: Se o usuário não for encontrado.
        """
        async with self.session as session:
            row = (
                await session.execute(
                    select(User).where(
                        User.id == id,
                        User.deleted_at.is_(None),
                    )
                )
            ).scalar_one_or_none()
            if not row:
                raise UserNotFound
        return self._build_aggregate(row)

    async def get_all_by_company(self, company: UUID) -> list[User]:
        """
        Busca todos os usuários ativos de uma empresa.

        Args:
            company: UUID da empresa.

        Returns:
            Lista de agregados User da empresa.
        """
        async with self.session as session:
            rows = (
                (
                    await session.execute(
                        select(User).where(
                            User.company == company,
                            User.deleted_at.is_(None),
                        )
                    )
                )
                .scalars()
                .all()
            )
        return [self._build_aggregate(row) for row in rows]

    async def _add(self, user: User) -> None:
        """Persiste um usuário no banco de dados (inserção ou atualização)."""
        data = {
            "id": user.id,
            "company": user.company,
            "email": user.email,
            "cpf": user.cpf,
            "_password_hash": user.password_hash,
            "name": user.name,
            "phone": user.phone,
            "street": user.street,
            "number": user.number,
            "zip_code": user.zip_code,
            "complement": user.complement,
            "district": user.district,
            "city": user.city,
            "state": user.state,
            "country": user.country,
            "active": user.active,
            "admin": user.admin,
            "is_owner": user.is_owner,
            "birth_date": user.birth_date,
            "created_at": user.created_at,
            "created_by": user.created_by,
            "updated_at": user.updated_at,
            "updated_by": user.updated_by,
            "deleted_at": user.deleted_at,
            "deleted_by": user.deleted_by,
        }
        await self._execute_upsert(User, user, data)

    async def _remove(self, user: User) -> None:
        """Marca um usuário como deletado no banco de dados (soft delete)."""
        await self._execute_soft_delete(User, user)
