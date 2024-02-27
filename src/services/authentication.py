from functools import lru_cache

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel, Field, field_serializer
from redis.asyncio import Redis

from src.db.redis import get_redis


class RedisTokenModel(BaseModel):
    record_id: str = Field(validation_alias='sub')
    jti: str = Field(validation_alias='jti')
    expires_at: int = Field(validation_alias='exp')
    used: bool = False

    @field_serializer('used')
    def serialize_used_to_string(self, used: bool):
        return str(used)


class AuthenticationService:
    def __init__(self, redis: Redis, auth_jwt: AuthJWT):
        self.redis = redis
        self.auth_jwt = auth_jwt

    async def is_refresh_token_used(self) -> bool:
        """
        Check if current refresh token in the list of used tokens.

        :return: True if token was already used or does not exist, else False
        """
        record_id = await self.auth_jwt.get_jwt_subject()
        token_used = await self.redis.hget(name=record_id, key='used')
        return not token_used == 'False'

    async def new_token_pair(self, subject: str, claims: dict | None = None):
        """Create new access and refresh tokens. Write to cookies and Redis."""
        await self._refresh_token_mark_as_used(subject)

        claims = claims if claims else {}
        new_access_token = await self.auth_jwt.create_access_token(subject=subject, user_claims=claims)
        new_refresh_token = await self.auth_jwt.create_refresh_token(subject=subject)

        await self.auth_jwt.set_access_cookies(new_access_token)
        await self.auth_jwt.set_refresh_cookies(new_refresh_token)

        await self._save_refresh_token_to_redis(new_refresh_token)

    async def logout(self):
        """Mark refresh token as used in Redis. Remove tokens from cookies."""
        subject = await self.auth_jwt.get_jwt_subject()
        await self._refresh_token_mark_as_used(subject)
        await self.auth_jwt.unset_jwt_cookies()

    async def _save_refresh_token_to_redis(self, encoded_token: str):
        """Save refresh token to Redis."""
        raw_jwt_token = await self.auth_jwt.get_raw_jwt(encoded_token)
        token_model = RedisTokenModel(**raw_jwt_token)
        await self.redis.hset(name=token_model.record_id, mapping=token_model.dict(exclude={'record_id'}))
        await self.redis.expireat(name=token_model.record_id, when=token_model.expires_at)

    async def _refresh_token_mark_as_used(self, record_id: str):
        """
        Change refresh token 'used' status in redis storage to True.
        :param record_id: ID of the token in Redis.
        """
        await self.redis.hset(name=record_id, key='used', value='True')

    async def jwt_refresh_token_required(self):
        await self.auth_jwt.jwt_refresh_token_required()

        if await self.is_refresh_token_used():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token was used or does not exist')

    async def get_jwt_subject(self):
        return await self.auth_jwt.get_jwt_subject()

    async def jwt_required(self):
        return await self.auth_jwt.jwt_required()


@lru_cache
def get_authentication_service(redis: Redis = Depends(get_redis), auth_jwt: AuthJWT = Depends(AuthJWT)):
    return AuthenticationService(redis, auth_jwt)
