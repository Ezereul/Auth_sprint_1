from functools import lru_cache

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel, Field, field_serializer
from redis.asyncio import Redis
from src.db.redis import get_redis


class RedisToken(BaseModel):
    user_id: str = Field(validation_alias='sub')
    jti: str = Field(validation_alias='jti')
    device: str = Field(validation_alias='device')
    expires_at: int = Field(validation_alias='exp')


class AuthenticationService:
    def __init__(self, redis: Redis, auth_jwt: AuthJWT):
        self.redis = redis
        self.auth_jwt = auth_jwt

    async def jwt_required(self):
        await self.auth_jwt.jwt_required()

    async def is_token_fresh(self) -> bool:
        """
        Check if current refresh token in the list of used tokens.

        :return: True if token was already used or does not exist, else False
        """
        raw = await self.auth_jwt.get_raw_jwt()

        record_name = 'fresh:%s:%s' % (raw['jti'], raw['sub'])
        if not await self.redis.exists(record_name):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token was used or doesn't exist")

        return True

    async def jwt_refresh_token_required(self):
        """Extend `jwt_refresh_token_required()` to also check is token available to use."""
        await self.auth_jwt.jwt_refresh_token_required()
        await self.is_token_fresh()

    async def _current_token(self) -> RedisToken | None:
        raw = await self.auth_jwt.get_raw_jwt()
        return RedisToken(**raw) if raw else None

    async def new_token_pair(self, user_id: str = None, claims: dict | None = None):
        """Create new access and refresh tokens. Write to cookies and Redis."""
        token = await self._current_token()
        if token:
            await self._mark_token_used(token.jti, token.user_id)

        user_id = user_id if user_id else token.user_id
        claims = claims if claims else {}

        new_access_token = await self.auth_jwt.create_access_token(subject=user_id, user_claims=claims)
        new_refresh_token = await self.auth_jwt.create_refresh_token(subject=user_id, user_claims=claims)

        await self.auth_jwt.set_access_cookies(new_access_token)
        await self.auth_jwt.set_refresh_cookies(new_refresh_token)

        await self._save_token(new_refresh_token)

    async def logout(self):
        """Mark refresh token as used in Redis. Remove tokens from cookies."""
        try:
            await self.jwt_refresh_token_required()
            token = await self._current_token()
            await self._mark_token_used(token.jti, token.user_id)
        except HTTPException:
            pass
        finally:
            await self.auth_jwt.unset_jwt_cookies()

    async def logout_all(self):
        user = await self.auth_jwt.get_jwt_subject()
        await self._mark_all_tokens_used(user)
        await self.auth_jwt.unset_jwt_cookies()

    async def _save_token(self, encoded_token: str):
        """Save refresh token to Redis."""
        raw_jwt_token = await self.auth_jwt.get_raw_jwt(encoded_token)
        token = RedisToken(**raw_jwt_token)
        await self.redis.set('fresh:%s:%s' % (token.jti, token.user_id), token.device, exat=token.expires_at)

    async def _mark_token_used(self, jti: str, user_id: str):
        """
        Mark user token as used in Redis by renaming it.

        'fresh:[jti_1]:[user_id]' -> 'used:[jti_1]:[user_id]'

        :param jti: JTI of the token.
        :param user_id: ID of the user.
        """
        await self.redis.rename('fresh:%s:%s' % (jti, user_id), 'used:%s:%s' % (jti, user_id))

    async def _mark_all_tokens_used(self, user_id: str):
        """
        Mark user tokens as used in Redis by renaming them.

        'fresh:[jti_1]:[user_id]' -> 'used:[jti_1]:[user_id]'
        'fresh:[jti_2]:[user_id]' -> 'used:[jti_2]:[user_id]'

        :param user_id: ID of the user.
        """
        async for record in self.redis.scan_iter(name='fresh:*:' + user_id, _type='STRING'):
            await self.redis.rename(record, 'used' + record[5:])


@lru_cache
def get_authentication_service(redis: Redis = Depends(get_redis), auth_jwt: AuthJWT = Depends(AuthJWT)):
    return AuthenticationService(redis, auth_jwt)
