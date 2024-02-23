from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends
from pydantic import BaseModel, Field
from redis.asyncio import Redis

from src.db.redis import get_redis


class RedisTokenModel(BaseModel):
    user_id: str = Field(validation_alias='sub')
    jti: str = Field(validation_alias='jti')
    expires_at: int = Field(validation_alias='exp')
    state: str = 'ready'


class AuthorizationService:
    def __init__(self, redis, auth_jwt):
        self.redis: Redis = redis
        self.auth_jwt: AuthJWT = auth_jwt

    async def is_refresh_token_in_whitelist(self, decrypted_token) -> bool:
        """
        Callback which checks if refresh token in the list of used tokens.

        If refresh token correct (exists in Redis and status='ready'), status on Redis becomes 'used'.

        If callback result():
            True -> The user gets access to the endpoint where the refresh token is required.
            False -> The user has no valid refresh token in cookies. Access is not allowed.

        Returns:
            True: If token JTI == 'ready'.
            False: In any other cases.
        """
        token_model = RedisTokenModel.model_validate(decrypted_token)
        token_id = token_model.user_id
        token_record = await self.redis.hget(name='redis_index', key=token_id)

        if 'ready' in token_record:
            token_model.state = 'used'
            record_data: dict = token_model.model_dump(exclude={'user_id'})
            await self.redis.hset(name=token_id, mapping=record_data)

            return True
        return False

    async def new_token_pair(self, user_id: str):
        """Create new access and refresh tokens. Write to cookies."""
        new_access_token = await self.auth_jwt.create_access_token(subject=user_id)
        new_refresh_token = await self.auth_jwt.create_refresh_token(subject=user_id)

        await self.auth_jwt.set_access_cookies(new_access_token)
        await self.auth_jwt.set_refresh_cookies(new_refresh_token)

        await self.save_refresh_token_to_redis(new_refresh_token)

        return new_access_token, new_refresh_token

    async def save_refresh_token_to_redis(self, token_data: str | dict | RedisTokenModel):
        """Save refresh token to Redis. Available formats: [str, dict, RedisTokenModel]"""
        if type(token_data) is str:
            token_data = await self.encoded_to_raw_jwt(token_data)

        if type(token_data) is dict:
            token_data = await self.raw_jwt_to_model(token_data)

        record_id = token_data.user_id
        record_data: dict = token_data.model_dump(exclude={'user_id'})

        await self.redis.hset(name=record_id, mapping=record_data)

    async def raw_jwt_to_model(self, raw_jwt_token: dict):
        """Convert raw jwt token to Redis model."""
        return RedisTokenModel.model_validate(raw_jwt_token)

    async def encoded_to_raw_jwt(self, encoded_token: str):
        """Convert encoded token to raw jwt token."""
        return await self.auth_jwt.get_raw_jwt(encoded_token)

    async def jwt_refresh_token_required(self):
        return await self.auth_jwt.jwt_refresh_token_required()

    async def get_jwt_subject(self):
        return await self.auth_jwt.get_jwt_subject()

    async def unset_jwt_cookies(self):
        return await self.auth_jwt.unset_jwt_cookies()


async def get_authorization_service(redis: Redis = Depends(get_redis), auth_jwt: AuthJWT = Depends(AuthJWT)):
    return AuthorizationService(redis, auth_jwt)
