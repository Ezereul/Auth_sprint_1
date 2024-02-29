from typing import Annotated

from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.permission import has_permission
from src.core.constants import RoleAccess
from src.core.db import get_async_session
from src.schemas.history import HistorySchema
from src.schemas.requests import PageParams
from src.schemas.responses import PagedResponseSchema
from src.services.history import HistoryService, get_history_service

router = APIRouter()


@router.get(
    '/',
    response_model=PagedResponseSchema[HistorySchema],
    dependencies=[Depends(has_permission(RoleAccess.USER))],
    response_model_exclude_none=True,
)
async def get_user_history(
        page_params: Annotated[PageParams, Depends()],
        Authorize: AuthJWT = Depends(),
        history_service: HistoryService = Depends(get_history_service),
        session: AsyncSession = Depends(get_async_session)):
    await Authorize.jwt_required()

    user_id = await Authorize.get_jwt_subject()

    data, pages_count = await history_service.get_history_paginated(session, user_id, page_params)

    return PagedResponseSchema(
        last=pages_count,
        items=[HistorySchema.from_orm(item) for item in data],
        **page_params.model_dump(),
    )
