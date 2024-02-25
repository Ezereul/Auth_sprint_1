from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends, status

from src.schemas.responses import DetailResponse
from src.services.account import AccountService, get_account_service

account_router = APIRouter(tags=['Account'])


@account_router.post(
    path='/change_username',
    response_model=DetailResponse,
    responses={
        status.HTTP_403_FORBIDDEN: {'model': DetailResponse, 'description': 'Incorrect new username'},
        status.HTTP_404_NOT_FOUND: {'model': DetailResponse, 'description': 'User not found'},
    },
)
async def change_username(
    new_username: str,
    Authorize: AuthJWT = Depends(),
    account: AccountService = Depends(get_account_service),
):
    await Authorize.jwt_required()

    user_id = await Authorize.get_jwt_subject()

    await account.change_username(user_id, new_username)

    return {'detail': 'Username changed'}


@account_router.post(
    path='/change_password',
    response_model=DetailResponse,
    responses={
        status.HTTP_403_FORBIDDEN: {'model': DetailResponse, 'description': 'Incorrect new password'},
        status.HTTP_404_NOT_FOUND: {'model': DetailResponse, 'description': 'User not found'},
    },
)
async def change_password(
    old_password: str,
    new_password: str,
    Authorize: AuthJWT = Depends(),
    account: AccountService = Depends(get_account_service),
):
    await Authorize.jwt_required()

    user_id = await Authorize.get_jwt_subject()

    await account.change_password(user_id, old_password, new_password)

    return {'detail': 'Password changed'}
