from functools import lru_cache
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Role
from src.models.user import User


class UserService:
    async def get_by_name(self, session: AsyncSession, username: str):
        return (await session.scalars(select(User).where(User.username == username))).first()  # noqa

    async def get(self, session: AsyncSession, user_id: UUID):
        return (await session.scalars(select(User).where(User.id == user_id))).first()  # noqa

    async def create(self, username: str, password: str, session: AsyncSession, role) -> User:
        if await self.get_by_name(session, username):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Username already registered')

        new_user = User(username=username, password=password, role=role)
        session.add(new_user)
        await session.commit()

        return new_user

    async def verify(self, username: str, password: str, session: AsyncSession):
        if not (user := await self.get_by_name(session, username)):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Username is not registered')

        if not user.is_correct_password(password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Wrong password')

        return user


@lru_cache
def get_user_service() -> UserService:
    return UserService()
