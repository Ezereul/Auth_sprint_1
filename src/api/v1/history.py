from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from async_fastapi_jwt_auth import AuthJWT

from src.core.db import get_async_session
from src.schemas.history import HistorySchema
from src.services.history import HistoryService, get_history_service


history_router = APIRouter()


@history_router.get('/history', response_model=list[HistorySchema], status_code=201)
async def get_user_history(
        Authorize: AuthJWT = Depends(),
        history_service: HistoryService = Depends(get_history_service),
        session: AsyncSession = Depends(get_async_session)):
    await Authorize.jwt_refresh_token_required()

    user_id = (await Authorize.get_jwt_subject()).partition(':')[0]

    return await history_service.get_history(session, user_id)