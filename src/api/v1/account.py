from fastapi import APIRouter, Depends, status

from src.schemas.responses import DetailResponse
from src.services.account import AccountService, get_account_service
from src.services.authentication import AuthenticationService, get_authentication_service

account_router = APIRouter(tags=['Account'])


@account_router.post(
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
    account: AccountService = Depends(get_account_service),
):
    await auth.jwt_required()

    user_id = await auth.get_jwt_subject()

    await account.change_username(user_id, new_username)

    return {'detail': 'Username changed'}


@account_router.post(
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
    account: AccountService = Depends(get_account_service),
):
    await auth.jwt_required()

    user_id = await auth.get_jwt_subject()

    await account.change_password(user_id, old_password, new_password)

    return {'detail': 'Password changed'}
