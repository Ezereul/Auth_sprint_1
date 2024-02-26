from functools import lru_cache
from uuid import UUID

from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.user import User

# alembic revision --autogenerate -m "user role and history models" --rev-id 01
# alembic upgrade head
class UserService:
    async def get_by_name(self, session: AsyncSession, username: str):
        return (await session.scalars(select(User).where(User.username == username))).first()  # noqa

    async def get(self, session: AsyncSession, user_id: UUID):
        return (await session.scalars(select(User).where(User.id == user_id))).first()  # noqa

    async def create(self, username: str, password: str, session: AsyncSession):
        if len(password) < 8:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Password length must be >= 8')
        if password == username:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Password cannot be equal to login')

        if user := await self.get_by_name(session, username):  # noqa
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Username already registered')

        new_user = User(username=username, password=password)
        session.add(new_user)
        await session.commit()

        return new_user

    async def verify(self, username: str, password: str, session: AsyncSession):
        if not (user := await self.get_by_name(session, username)):  # noqa
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Username is not registered')

        if not user.is_correct_password(password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Wrong password')

        return user


@lru_cache
def get_user_service() -> UserService:
    return UserService()
