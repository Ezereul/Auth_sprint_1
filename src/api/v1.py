from typing import Annotated, Any

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends, HTTPException, APIRouter, status
from redis.asyncio import Redis

from src.db.redis import get_redis
from src.db.stub import stub_database
from src.schemas import UserSchema
from src.schemas.responses import DetailResponse
from src.services.authorization import get_authorization_service
from src.utils import passwords
from src.utils.passwords import verify

router = APIRouter()


@router.post(
    '/register',
    response_model=DetailResponse,
    responses={
        status.HTTP_409_CONFLICT: {'model': DetailResponse, 'description': 'Username already registered'},
        status.HTTP_403_FORBIDDEN: {'model': DetailResponse, 'description': 'Password is too weak'},
    },
)
async def register(user: UserSchema):
    """
    Password requirements:
    1. Has length >= 8.
    2. Contains at least one upper-case letter.
    3. Contains at least one lower-case letter.
    4. Contains at least one digit.
    """
    if stub_database.get_data('username', user.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Username already registered')
    if not passwords.is_password_safe(user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Password is too weak')

    user.password = passwords.to_hash(user.password)

    stub_database.save_data(user.model_dump())  # refactor to service, add DI

    # send registration email
    return {'detail': 'Successfully registered. Verification email send on email: {}'.format(user.username)}


@router.post(
    '/login',
    response_model=DetailResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {'model': DetailResponse, 'description': 'Wrong password'},
        status.HTTP_404_NOT_FOUND: {'model': DetailResponse, 'description': 'Username is not registered'},
    },
)
async def login(user: UserSchema, auth: Annotated[Any, Depends(get_authorization_service)]):
    db_user_data = stub_database.get_data('username', user.username)  # refactor to service, add DI

    if not db_user_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Username is not registered')
    if not verify(user.password, db_user_data.get('password')):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Wrong password')

    # add role payload to access token
    await auth.new_token_pair(db_user_data['id'])

    return {'detail': 'Successfully login'}


@router.post('/refresh', response_model=DetailResponse)
async def refresh(redis: Annotated[Redis, Depends(get_redis)], auth_jwt: Annotated[AuthJWT, Depends(AuthJWT)]):
    await auth_jwt.jwt_refresh_token_required()

    current_user_id = await auth_jwt.get_jwt_subject()

    new_access_token = await auth_jwt.create_access_token(subject=current_user_id)
    new_refresh_token = await auth_jwt.create_refresh_token(subject=current_user_id)

    await auth_jwt.set_access_cookies(new_access_token)
    await auth_jwt.set_refresh_cookies(new_refresh_token)

    # This block marks new refresh token as 'ready' in Redis. Expiration in Redis = token expiration.
    raw_refresh_token = await auth_jwt.get_raw_jwt()
    jti = raw_refresh_token['jti']
    exp = raw_refresh_token['exp']
    await redis.set(name=jti, value='ready', exat=exp)

    return {'detail': 'The token has been refreshed'}


@router.post('/logout', response_model=DetailResponse)
async def logout(auth_jwt: Annotated[AuthJWT, Depends(AuthJWT)]):
    await auth_jwt.jwt_refresh_token_required()

    await auth_jwt.unset_jwt_cookies()

    return {'detail': 'Successfully log out'}
