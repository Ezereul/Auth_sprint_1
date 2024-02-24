from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.schemas.history import HistorySchema
from src.services.history import HistoryService, get_history_service
from src.services.authentication import AuthenticationService, get_authentication_service


history_router = APIRouter()


@history_router.get('/history', response_model=list[HistorySchema], status_code=201)
async def register(
        auth_service: AuthenticationService = Depends(get_authentication_service),
        history_service: HistoryService = Depends(get_history_service),
        session: AsyncSession = Depends(get_async_session)):
    await auth_service.jwt_refresh_token_required()

    user_id = await auth_service.get_jwt_subject()

    return await history_service.get_history(session, user_id)
