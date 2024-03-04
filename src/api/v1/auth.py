from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.permission import has_permission
from src.core.constants import RoleAccess
from src.core.db import get_async_session
from src.schemas.responses import DetailResponse
from src.schemas.user import UserCreateOrUpdate, UserDB, UserLogin
from src.services.authentication import AuthenticationService, get_authentication_service
from src.services.history import HistoryService, get_history_service
from src.services.roles import RoleService, get_role_service
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
    role_service: RoleService = Depends(get_role_service),
    session: AsyncSession = Depends(get_async_session),
):
    default_role = await role_service.get_default_role(session)
    user = await user_service.create(user.username, user.password, session, default_role)

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
    history_service: HistoryService = Depends(get_history_service),
    user_service: UserService = Depends(get_user_service),
    session: AsyncSession = Depends(get_async_session),
):
    user = await user_service.verify(user.username, user.password, session)
    await history_service.create(session, user.id)

    role = await user.awaitable_attrs.role

    await auth_service.new_token_pair(subject=str(user.id), claims={'access_level': role.access_level})

    return {'detail': 'Successfully login'}


@router.post('/refresh', response_model=DetailResponse, dependencies=[Depends(has_permission(RoleAccess.USER))])
async def refresh(
        auth_service: AuthenticationService = Depends(get_authentication_service),
        user_service: UserService = Depends(get_user_service),
        session: AsyncSession = Depends(get_async_session)
):
    await auth_service.jwt_refresh_token_required()

    subject = await auth_service.get_jwt_subject()
    user = await user_service.get(session, subject)
    role = await user.awaitable_attrs.role

    await auth_service.new_token_pair(subject=subject, claims={'access_level': role.access_level})

    return {'detail': 'Token has been refreshed'}


@router.post('/logout', response_model=DetailResponse)
async def logout(auth_service: AuthenticationService = Depends(get_authentication_service)):
    await auth_service.jwt_refresh_token_required()

    await auth_service.logout()

    return {'detail': 'Successfully log out'}
