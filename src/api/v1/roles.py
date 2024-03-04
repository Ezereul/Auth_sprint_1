from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.permission import has_permission
from src.core.constants import RoleAccess
from src.core.db import get_async_session
from src.schemas.roles import RoleCRUD, RoleDB
from src.schemas.user import UserWithRole
from src.services.roles import RoleService, get_role_service
from src.services.users import UserService, get_user_service

router = APIRouter()


@router.post(
    '/create', response_model=RoleDB, status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(has_permission(RoleAccess.SUPERUSER))])
async def create_role(
        role_data: RoleCRUD,
        role_service: RoleService = Depends(get_role_service),
        session: AsyncSession = Depends(get_async_session)):
    if await role_service.get_by_name(session, role_data.name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role already exists")

    return await role_service.create(session, role_data.dict())


@router.get('/', response_model=list[RoleDB], dependencies=[Depends(has_permission(RoleAccess.SUPERUSER))])
async def get_roles(
        role_service: RoleService = Depends(get_role_service),
        session: AsyncSession = Depends(get_async_session)):

    return await role_service.elements(session)


@router.patch('/{role_id}', response_model=RoleDB, dependencies=[Depends(has_permission(RoleAccess.SUPERUSER))])
async def update_role(
        role_id: UUID,
        role_data: RoleCRUD,
        role_service: RoleService = Depends(get_role_service),
        session: AsyncSession = Depends(get_async_session)):

    if not (update_role := await role_service.get(session, role_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Role not found')
    if update_role.name in ('superuser', 'user'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cant change default role')

    return await role_service.update(session, update_role, role_data.dict())


@router.delete('/{role_id}', response_model=RoleDB, dependencies=[Depends(has_permission(RoleAccess.SUPERUSER))])
async def delete_role(
        role_id: UUID,
        role_service: RoleService = Depends(get_role_service),
        session: AsyncSession = Depends(get_async_session)):

    if not (delete_role := await role_service.get(session, role_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Role not found')
    if delete_role.name in ('superuser', 'user'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cant delete default role')

    return await role_service.delete(session, delete_role)


@router.post('/assign', response_model=UserWithRole, dependencies=[Depends(has_permission(RoleAccess.SUPERUSER))])
async def assign_role(
        username: str,
        role_name: str,
        role_service: RoleService = Depends(get_role_service),
        user_service: UserService = Depends(get_user_service),
        session: AsyncSession = Depends(get_async_session)):

    if not (user := await user_service.get_by_name(session, username)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    if not (role := await role_service.get_by_name(session, role_name)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Role not found')

    user = await role_service.assign_role(session, role, user)

    return UserWithRole(
        username=user.username,
        role=RoleCRUD(name=role.name, access_level=role.access_level)
    )


@router.post('/revoke', response_model=UserWithRole, dependencies=[Depends(has_permission(RoleAccess.SUPERUSER))])
async def revoke_role(
        username: str,
        role_service: RoleService = Depends(get_role_service),
        user_service: UserService = Depends(get_user_service),
        session: AsyncSession = Depends(get_async_session)):

    if not (user := await user_service.get_by_name(session, username)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    default_role = await role_service.get_default_role(session)
    user = await role_service.assign_role(session, default_role, user)

    return UserWithRole(
        username=user.username,
        role=RoleCRUD(name=default_role.name, access_level=default_role.access_level)
    )
