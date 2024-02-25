from functools import lru_cache

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.models.user import User


class AccountService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def change_username(self, user_id, new_username):
        stmt = select(User).where(User.id == user_id)  # noqa

        if not (user := (await self.db_session.scalars(stmt)).first()):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

        if new_username == user.username:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='New username must be different')

        user.username = new_username

        await self.db_session.commit()

    async def change_password(self, user_id, old_password, new_password):
        stmt = select(User).where(User.id == user_id)  # noqa

        if not (user := (await self.db_session.scalars(stmt)).first()):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

        if not user.is_correct_password(old_password):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Wrong password')

        if old_password == new_password:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='New password must be different')

        user.password = new_password

        await self.db_session.commit()


@lru_cache
def get_account_service(db_session: AsyncSession = Depends(get_async_session)):
    return AccountService(db_session)
