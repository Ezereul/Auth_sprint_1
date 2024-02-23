from functools import lru_cache
from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.user import User


class UserService:
    async def create(self, username: str, password: str, session: AsyncSession):
        if len(password) < 8:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Password length must be >= 8')
        if password == username:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Password cannot be equal to login')

        if user := (await session.scalars(select(User).where(User.username == username))).first():  # noqa
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Username already registered')

        new_user = User(username=username, password=password)
        session.add(new_user)
        await session.commit()

        return new_user

    async def verify(self, username: str, password: str, session: AsyncSession):
        if not (user := (await session.scalars(select(User).where(User.username == username))).first()):  # noqa
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Username is not registered')

        if not user.is_correct_password(password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Wrong password')

        return user


@lru_cache
def get_user_service() -> UserService:
    return UserService()
