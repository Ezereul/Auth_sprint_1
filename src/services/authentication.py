from functools import lru_cache

import redis.exceptions
from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel, Field
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

    async def fresh_jwt_refresh_token_required(self):
        """Extend `jwt_refresh_token_required()` to also check if token available to use."""
        await self.auth_jwt.jwt_refresh_token_required()
        await self.is_token_fresh()

    async def new_token_pair(self, user_id: str = None, claims: dict | None = None):
        """Create new access and refresh tokens. Save to cookies and Redis."""
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
        """Mark refresh token as used in Redis. Clear tokens cookies."""
        token = await self._current_token()
        try:
            await self._mark_token_used(token.jti, token.user_id)
        except redis.exceptions.ResponseError:
            pass
        await self.auth_jwt.unset_jwt_cookies()

    async def logout_all(self):
        """Mark all refresh tokens as used for specific user. Clear tokens cookies."""
        user = await self.auth_jwt.get_jwt_subject()

        await self._mark_all_tokens_used(user)

        await self.auth_jwt.unset_jwt_cookies()

    async def _current_token(self) -> RedisToken | None:
        """Get token, which was required."""
        raw = await self.auth_jwt.get_raw_jwt()
        return RedisToken(**raw) if raw else None

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

        if await self.is_refresh_token_used():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token was used or does not exist')

        :param user_id: ID of the user.
        """
        async for record in self.redis.scan_iter(match='fresh:*:' + user_id, _type='STRING'):
            await self.redis.rename(record, 'used' + record[5:])

    async def jwt_required(self):
        return await self.auth_jwt.jwt_required()


@lru_cache
def get_authentication_service(redis: Redis = Depends(get_redis), auth_jwt: AuthJWT = Depends(AuthJWT)):
    return AuthenticationService(redis, auth_jwt)
