from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.schemas.responses import DetailResponse
from src.services.account import AccountService, get_account_service
from src.services.authentication import AuthenticationService, get_authentication_service

router = APIRouter()


@router.post(
    path='/change_username',
    response_model=DetailResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': DetailResponse, 'description': 'Incorrect new username'},
        status.HTTP_404_NOT_FOUND: {'model': DetailResponse, 'description': 'User not found'},
    },
)
async def change_username(
    new_username: str,
    auth: AuthenticationService = Depends(get_authentication_service),
    db_session: AsyncSession = Depends(get_async_session),
    account: AccountService = Depends(get_account_service),
):
    await auth.jwt_required()

    user_id = await auth.get_jwt_subject()

    await account.change_username(db_session, user_id, new_username)

    return {'detail': 'Username changed'}


@router.post(
    path='/change_password',
    response_model=DetailResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': DetailResponse, 'description': 'Incorrect new password'},
        status.HTTP_404_NOT_FOUND: {'model': DetailResponse, 'description': 'User not found'},
    },
)
async def change_password(
    old_password: str,
    new_password: str,
    auth: AuthenticationService = Depends(get_authentication_service),
    db_session: AsyncSession = Depends(get_async_session),
    account: AccountService = Depends(get_account_service),
):
    await auth.jwt_required()

    user_id = await auth.get_jwt_subject()

    await account.change_password(db_session, user_id, old_password, new_password)

    return {'detail': 'Password changed'}
