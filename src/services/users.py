from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.user import User


class UserService:
    async def create(self, username: str, password: str, session: AsyncSession):
        if len(password) < 8:
            raise ValueError('Пароль слишком короткий')
        if password == username:
            raise ValueError('Пароль совпадает с логином')

        if (user := (await session.scalars(select(User).where(User.username == username))).first()):  # noqa
            raise ValueError('Пользователь уже существует')

        new_user = User(username=username, password=password)
        session.add(new_user)
        await session.commit()

        return new_user

    async def verify(self, username: str, password: str, session: AsyncSession):
        user = (await session.scalars(select(User).where(User.username == username))).first()  # noqa

        if user and user.is_correct_password(password):
            return True

        return False


@lru_cache
def get_user_service() -> UserService:
    return UserService()
