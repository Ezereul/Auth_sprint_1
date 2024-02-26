from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.permission import has_permission
from src.core.constants import RoleAccess
from src.core.db import get_async_session
from src.schemas.history import HistorySchema
from src.services.history import HistoryService, get_history_service

router = APIRouter()


@router.get('/', response_model=list[HistorySchema], dependencies=[Depends(has_permission(RoleAccess.USER))])
async def get_user_history(
        Authorize: AuthJWT = Depends(),
        history_service: HistoryService = Depends(get_history_service),
        session: AsyncSession = Depends(get_async_session)):
    await Authorize.jwt_refresh_token_required()

    user_id = await Authorize.get_jwt_subject()

    return await history_service.get_history(session, user_id)
