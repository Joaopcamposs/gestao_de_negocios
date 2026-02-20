"""Módulo do repositório de consulta de User."""

from typing import Any
from uuid import UUID

from sqlalchemy import select

from shared_core.domain.aggregate.user import PublicUser as PublicUserAggregate
from shared_core.domain.aggregate.user import User as UserAggregate
from shared_core.domain.entities.user import PublicUser, User
from messagebus.entities import ViewRepository


class UserViewRepo(ViewRepository):
    """Repositório de consulta para User."""

    @staticmethod
    def _build_entity(row: Any) -> User:
        """
        Constrói uma entidade User de leitura a partir de uma linha ORM.

        Args:
            row: Linha mapeada pelo SQLAlchemy.

        Returns:
            Entidade User de leitura.
        """
        return User(
            id=row.id,
            company=row.company,
            email=row.email,
            cpf=row.cpf,
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
            _password_hash=row.password_hash,
            deleted_at=row.deleted_at,
            deleted_by=row.deleted_by,
            created_at=row.created_at,
            created_by=row.created_by,
            updated_at=row.updated_at,
            updated_by=row.updated_by,
        )

    async def get_by_email(
        self, email: str, include_deleted: bool = False
    ) -> User | None:
        """
        Busca um usuário pelo email (somente leitura).

        Args:
            email: Email do usuário.
            include_deleted: Se True, inclui usuários deletados.

        Returns:
            Entidade User ou None se não encontrado.
        """
        async with self.session as session:
            query = select(UserAggregate).where(UserAggregate.email == email)
            if not include_deleted:
                query = query.where(UserAggregate.deleted_at.is_(None))
            row = (await session.execute(query)).scalar_one_or_none()
        return self._build_entity(row) if row else None

    async def get_by_id(self, id: UUID) -> User | None:
        """
        Busca um usuário pelo ID (somente leitura).

        Args:
            id: UUID do usuário.

        Returns:
            Entidade User ou None se não encontrado.
        """
        async with self.session as session:
            row = (
                await session.execute(
                    select(UserAggregate).where(
                        UserAggregate.id == id,
                        UserAggregate.deleted_at.is_(None),
                    )
                )
            ).scalar_one_or_none()
        return self._build_entity(row) if row else None

    async def get_all(self, include_deleted: bool = False) -> list[User]:
        """
        Busca todos os usuários (somente leitura).

        Args:
            include_deleted: Se True, inclui usuários deletados.

        Returns:
            Lista de entidades User.
        """
        async with self.session as session:
            query = select(UserAggregate)
            if not include_deleted:
                query = query.where(UserAggregate.deleted_at.is_(None))
            rows = (await session.execute(query)).scalars().all()
        return [self._build_entity(row) for row in rows]

    async def get_public_user_by_email(self, email: str) -> PublicUser | None:
        """
        Busca um usuário público pelo email (somente leitura).

        Args:
            email: Email do usuário (será convertido em hash para busca).

        Returns:
            Entidade PublicUser ou None se não encontrado.
        """
        email_hash = PublicUser.hash_email(email)
        async with self.session as session:
            result = (
                await session.execute(
                    select(PublicUserAggregate).where(
                        PublicUserAggregate.email_hash == email_hash,
                        PublicUserAggregate.deleted_at.is_(None),
                    )
                )
            ).scalar_one_or_none()
            if not result:
                return None

            public_user_entity = PublicUser(
                id=result.id,
                company=result.company,
                active=result.active,
                email_encrypted=result.email_encrypted,
                email_hash=result.email_hash,
                _password_hash=result.password_hash,
            )
            return public_user_entity
