import uuid
from functools import lru_cache

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.history import LoginHistory
from src.schemas.history import HistorySchema
from src.schemas.requests import PageParams
from src.schemas.responses import PagedResponseSchema
from src.utils.paginate import paginate


class HistoryService:
    async def create(self, session: AsyncSession, user_id: uuid):
        history = LoginHistory(user_id=user_id)
        session.add(history)
        await session.commit()
        await session.refresh(history)

    async def get_history_paginated(
        self, session: AsyncSession, user_id: uuid, page_params: PageParams, response_schema: HistorySchema
    ) -> PagedResponseSchema:
        stmt = (select(LoginHistory)
                .where(LoginHistory.user_id == user_id)  # noqa
                .order_by(desc(LoginHistory.login_time)))  # noqa

        return await paginate(session, stmt, page_params, response_schema)


@lru_cache
def get_history_service() -> HistoryService:
    return HistoryService()
