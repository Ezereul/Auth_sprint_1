from functools import lru_cache

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User


class AccountDataException(ValueError):
    """Exception raised when new value for account is invalid"""


class AccountService:

    async def query_user_by_id(self, db_session: AsyncSession, user_id: str):
        stmt = select(User).where(User.id == user_id)  # noqa

        if not (user := (await db_session.scalars(stmt)).first()):
            raise AccountDataException('User not found')
        return user

    async def change_username(self, db_session: AsyncSession, user_id: str, new_username: str):
        user = await self.query_user_by_id(db_session, user_id)

        if new_username == user.username:
            raise AccountDataException('New username must be different')
        user.username = new_username

        await db_session.commit()

    async def change_password(self, db_session: AsyncSession, user_id: str, old_password: str, new_password: str):
        user = await self.query_user_by_id(db_session, user_id)

        if not user.is_correct_password(old_password):
            raise AccountDataException('Wrong password')
        if old_password == new_password:
            raise AccountDataException('New password must be different')

        user.password = new_password

        await db_session.commit()


@lru_cache
def get_account_service():
    return AccountService()
