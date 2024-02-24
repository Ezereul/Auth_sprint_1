from http import HTTPStatus

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.schemas.user import UserLogin, UserCreateOrUpdate, UserDB
from src.services.history import HistoryService, get_history_service
from src.services.users import UserService, get_user_service

router = APIRouter()


@router.post('/register', response_model=UserDB, status_code=201)
async def register(
        user: UserCreateOrUpdate,
        user_service: UserService = Depends(get_user_service),
        session: AsyncSession = Depends(get_async_session)):

    user = await user_service.create(user.username, user.password, session)

    return user


@router.post('/login')
async def login(
        user: UserLogin,
        Authorize: AuthJWT = Depends(),
        user_service: UserService = Depends(get_user_service),
        history_service: HistoryService = Depends(get_history_service),
        session: AsyncSession = Depends(get_async_session)):
    user = await user_service.verify(user.username, user.password, session)
    await history_service.create(session, user.id)

    access_token = await Authorize.create_access_token(subject=str(user.id))
    refresh_token = await Authorize.create_refresh_token(subject=str(user.id))

    await Authorize.set_access_cookies(access_token)
    await Authorize.set_refresh_cookies(refresh_token)

    # rewrite old refresh token by new in Redis

    return {'msg': 'Successfully login'}


@router.post('/refresh')
async def refresh(Authorize: AuthJWT = Depends()):
    await Authorize.jwt_refresh_token_required()
    # add token expiration validation (or it is already valid?)
    # check token in Redis

    current_user = await Authorize.get_jwt_subject()

    new_access_token = await Authorize.create_access_token(subject=current_user)
    new_refresh_token = await Authorize.create_refresh_token(subject=current_user)

    await Authorize.set_access_cookies(new_access_token)
    await Authorize.set_refresh_cookies(new_refresh_token)

    # rewrite old refresh token by new in Redis
    return {'msg': 'The token has been refreshed'}


@router.post('/logout')
async def logout(Authorize: AuthJWT = Depends()):
    await Authorize.jwt_refresh_token_required()
    # add token expiration validation (or it is already valid?)

    # current_user = await Authorize.get_jwt_subject()
    # remove old refresh token from redis by current_user.id

    await Authorize.unset_access_cookies()
    await Authorize.unset_refresh_cookies()

    return {'msg': 'Successfully log out'}
