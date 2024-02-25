from fastapi import Depends, APIRouter, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.schemas.responses import DetailResponse
from src.schemas.user import UserLogin, UserCreateOrUpdate, UserDB
from src.services.authentication import AuthenticationService, get_authentication_service
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
    auth_service: AuthenticationService = Depends(get_authentication_service),
    user_service: UserService = Depends(get_user_service),
    session: AsyncSession = Depends(get_async_session),
):
    user = await user_service.verify(user.username, user.password, session)

    await auth_service.new_token_pair(subject=str(user.id), claims={'role': 'stub'})  # вместо 'stub' будет user.role

    return {'detail': 'Successfully login'}


@router.post('/refresh', response_model=DetailResponse)
async def refresh(auth_service: AuthenticationService = Depends(get_authentication_service)):
    await auth_service.jwt_refresh_token_required()

    subject = await auth_service.get_jwt_subject()
    await auth_service.new_token_pair(subject=subject, claims={'role': 'stub'})

    return {'detail': 'The token has been refreshed'}


@router.post('/logout', response_model=DetailResponse)
async def logout(auth_service: AuthenticationService = Depends(get_authentication_service)):
    await auth_service.jwt_refresh_token_required()

    await auth_service.logout()

    return {'detail': 'Successfully log out'}
