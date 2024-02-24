import uuid
from functools import lru_cache
from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.history import LoginHistory


class HistoryService:
    async def get_history(self, session: AsyncSession, user_id: uuid):
        return (await session.scalars(select(LoginHistory).where(LoginHistory.user_id == user_id))).all()  # noqa


@lru_cache
def get_history_service() -> HistoryService:
    return HistoryService()
