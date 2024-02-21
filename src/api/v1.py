from http import HTTPStatus

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends, HTTPException, APIRouter

from src.db.stub import stub_database
from src.models.security import pwd_context
from src.models.user import User


router = APIRouter()


@router.post('/register')
async def register(user: User):
    if stub_database.get_data(user.username):
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Username already registered')

    # add password strength check
    password_hash = pwd_context.hash(user.password)

    stub_database.save_data({user.username: password_hash})  # refactor to service, add DI

    # send registration email

    return {'msg': 'Successfully registered. Verification email send on your email: %s' % user.username}


@router.post('/login')
async def login(user: User, authorization: AuthJWT = Depends()):
    db_user_data = stub_database.get_data(user.username)  # refactor to service, add DI

    if not db_user_data:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Username is not registered')
    if not pwd_context.verify(user.password, db_user_data.get('password')):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Wrong password')

    access_token = await authorization.create_access_token(subject=user.username)
    refresh_token = await authorization.create_refresh_token(subject=user.username)

    await authorization.set_access_cookies(access_token)
    await authorization.set_refresh_cookies(refresh_token)

    # rewrite old refresh token by new in Redis

    return {'msg': 'Successfully login'}


@router.post('/refresh')
async def refresh(authorization: AuthJWT = Depends()):
    await authorization.jwt_refresh_token_required()
    # add token expiration validation (or it is already valid?)
    # check token in Redis

    current_user = await authorization.get_jwt_subject()

    new_access_token = await authorization.create_access_token(subject=current_user)
    new_refresh_token = await authorization.create_refresh_token(subject=current_user)

    await authorization.set_access_cookies(new_access_token)
    await authorization.set_refresh_cookies(new_refresh_token)

    # rewrite old refresh token by new in Redis
    return {'msg': 'The token has been refreshed'}


@router.post('/logout')
async def logout(authorization: AuthJWT = Depends()):
    await authorization.jwt_refresh_token_required()
    # add token expiration validation (or it is already valid?)

    # current_user = await Authorize.get_jwt_subject()
    # remove old refresh token from redis by current_user.id

    await authorization.unset_access_cookies()
    await authorization.unset_refresh_cookies()

    return {'msg': 'Successfully log out'}
