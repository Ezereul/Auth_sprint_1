from fastapi import APIRouter

from src.api.v1 import account_router, auth_router, history_router, role_router

main_router = APIRouter()

main_router.include_router(
    auth_router, prefix='/auth', tags=['User Authentication']
)
main_router.include_router(
    history_router, prefix='/history', tags=['Login History']
)
main_router.include_router(
    role_router, prefix='/role', tags=['Roles']
)
main_router.include_router(
    account_router, prefix='/account', tags=['Account']
)
