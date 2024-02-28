from functools import lru_cache
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import DEFAULT_ROLE_DATA
from src.models import User
from src.models.roles import Role


class RoleService:
    async def get(self, session: AsyncSession, role_id: UUID):
        return (await session.scalars(select(Role).where(Role.id == role_id))).first()  # noqa

    async def get_by_name(self, session: AsyncSession, role_name: str):
        return (await session.scalars(select(Role).where(Role.name == role_name))).first()  # noqa

    async def create(self, session: AsyncSession, role_data: dict):
        new_role = Role(**role_data)
        session.add(new_role)
        await session.commit()

        return new_role

    async def update(self, session: AsyncSession, role: Role, update_data: dict):
        for key, value in update_data.items():
            setattr(role, key, value)
        await session.commit()
        await session.refresh(role)

        return role

    async def delete(self, session: AsyncSession, role: Role):
        await session.delete(role)
        await session.commit()
        return role

    async def elements(self, session: AsyncSession):
        return (await session.scalars(select(Role))).all()

    async def assign_role(self, session: AsyncSession, role: Role, user: User):
        user.role = role
        await session.commit()
        await session.refresh(user)

        return user

    async def set_default_role(self, session: AsyncSession, user: User):
        if not (default_role := await self.get_by_name(session, DEFAULT_ROLE_DATA['name'])):
            default_role = await self.create(session, DEFAULT_ROLE_DATA)

        await self.assign_role(session, default_role, user)


@lru_cache
def get_role_service() -> RoleService:
    return RoleService()
