from typing import Annotated

from fastapi import Depends, APIRouter, status, Header
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.schemas.responses import DetailResponse
from src.schemas.user import UserLogin, UserCreateOrUpdate, UserDB
from src.services.authentication import AuthenticationService, get_authentication_service
from src.services.history import HistoryService, get_history_service
from src.services.users import UserService, get_user_service

router = APIRouter()


@router.post(
    '/register',
    response_model=UserDB,
    status_code=201,
    responses={
        status.HTTP_409_CONFLICT: {'model': DetailResponse, 'description': 'Username already registered'},
        status.HTTP_403_FORBIDDEN: {'model': DetailResponse, 'description': 'Password is too weak'},
    },
)
async def register(
    user: UserCreateOrUpdate,
    user_service: UserService = Depends(get_user_service),
    session: AsyncSession = Depends(get_async_session),
):

    user = await user_service.create(user.username, user.password, session)

    return user


@router.post(
    '/login',
    response_model=DetailResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {'model': DetailResponse, 'description': 'Wrong password'},
        status.HTTP_404_NOT_FOUND: {'model': DetailResponse, 'description': 'Username is not registered'},
    },
)
async def login(
    user: UserLogin,
    user_agent: Annotated[str, Header(include_in_schema=False)] = 'None',
    auth_service: AuthenticationService = Depends(get_authentication_service),
    history_service: HistoryService = Depends(get_history_service),
    user_service: UserService = Depends(get_user_service),
    session: AsyncSession = Depends(get_async_session),
):
    user = await user_service.verify(user.username, user.password, session)
    await history_service.create(session, user.id)

    await auth_service.new_token_pair(user_id=str(user.id), claims={'role': 'stub', 'device': user_agent})

    return {'detail': 'Successfully login'}


@router.post('/refresh', response_model=DetailResponse)
async def refresh(
    auth_service: AuthenticationService = Depends(get_authentication_service),
    user_agent: Annotated[str, Header(include_in_schema=False)] = 'None',
):
    await auth_service.fresh_jwt_refresh_token_required()

    await auth_service.new_token_pair(claims={'role': 'stub', 'device': user_agent})

    return {'detail': 'The token has been refreshed'}


@router.post('/logout', response_model=DetailResponse)
async def logout(auth_service: AuthenticationService = Depends(get_authentication_service)):
    await auth_service.auth_jwt.jwt_refresh_token_required()

    await auth_service.logout()

    return {'detail': 'Successfully log out'}


@router.post('/logout_all', response_model=DetailResponse)
async def logout_all(auth_service: AuthenticationService = Depends(get_authentication_service)):
    await auth_service.fresh_jwt_refresh_token_required()

    await auth_service.logout_all()

    return {'detail': 'Successfully log out from all devices'}
