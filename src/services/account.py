from functools import lru_cache

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.models.user import User


class AccountDataException(ValueError):
    """Exception raised when new value for account is invalid"""


class AccountService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def query_user_by_id(self, user_id):
        stmt = select(User).where(User.id == user_id)  # noqa

        if not (user := (await self.db_session.scalars(stmt)).first()):
            raise AccountDataException('User not found')
        return user

    async def change_username(self, user_id, new_username):
        user = await self.query_user_by_id(user_id)

        if new_username == user.username:
            raise AccountDataException('New username must be different')
        user.username = new_username

        await self.db_session.commit()

    async def change_password(self, user_id, old_password, new_password):
        user = await self.query_user_by_id(user_id)

        if not user.is_correct_password(old_password):
            raise AccountDataException('Wrong password')
        if old_password == new_password:
            raise AccountDataException('New password must be different')

        user.password = new_password

        await self.db_session.commit()


@lru_cache
def get_account_service(db_session: AsyncSession = Depends(get_async_session)):
    return AccountService(db_session)
