import uuid
from functools import lru_cache
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from src.models.history import LoginHistory


class HistoryService:
    async def create(self, session: AsyncSession, user_id: uuid.UUID):
        history = LoginHistory(user_id=user_id)
        session.add(history)
        await session.commit()
        await session.refresh(history)

    async def get_history(self, session: AsyncSession, user_id: uuid.UUID):
        return (await session.scalars(
            select(LoginHistory)
            .where(LoginHistory.user_id == user_id)  # noqa
            .order_by(desc(LoginHistory.login_time))  # noqa
            .limit(10)
        )).all()


@lru_cache
def get_history_service() -> HistoryService:
    return HistoryService()