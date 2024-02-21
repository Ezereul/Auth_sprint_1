from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends, HTTPException, APIRouter, status

from src.db.stub import stub_database
from src.models.security import pwd_context
from src.schemas.responses import DetailResponse
from src.schemas.user import UserSchema


router = APIRouter()

@router.post(
    '/register',
    response_model=DetailResponse,
    responses={
        status.HTTP_409_CONFLICT: {'model': DetailResponse, 'description': 'Username already registered'},
    },
)
async def register(user: UserSchema):
    if stub_database.get_data('username', user.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Username already registered')

    # add password strength check
    password_hash = pwd_context.hash(user.password)
    user.password = password_hash

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
async def login(user: UserSchema, authorization: AuthJWT = Depends()):
    db_user_data = stub_database.get_data('username', user.username)  # refactor to service, add DI

    if not db_user_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Username is not registered')
    if not pwd_context.verify(user.password, db_user_data.get('password')):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Wrong password')

    # add to access token payload user_id and role
    access_token = await authorization.create_access_token(subject=db_user_data['id'])
    refresh_token = await authorization.create_refresh_token(subject=db_user_data['id'])

    await authorization.set_access_cookies(access_token)
    await authorization.set_refresh_cookies(refresh_token)

    # rewrite old refresh token by new in Redis

    return {'detail': 'Successfully login'}


@router.post('/refresh', response_model=DetailResponse)
async def refresh(authorization: AuthJWT = Depends()):
    await authorization.jwt_refresh_token_required()
    # check token in Redis

    current_user = await authorization.get_jwt_subject()

    new_access_token = await authorization.create_access_token(subject=current_user)
    new_refresh_token = await authorization.create_refresh_token(subject=current_user)

    await authorization.set_access_cookies(new_access_token)
    await authorization.set_refresh_cookies(new_refresh_token)

    # rewrite old refresh token by new in Redis
    return {'detail': 'The token has been refreshed'}


@router.post('/logout', response_model=DetailResponse)
async def logout(authorization: AuthJWT = Depends()):
    await authorization.jwt_refresh_token_required()

    # current_user = await Authorize.get_jwt_subject()
    # remove old refresh token from redis by current_user.id

    await authorization.unset_access_cookies()
    await authorization.unset_refresh_cookies()

    return {'detail': 'Successfully log out'}
