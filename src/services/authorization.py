from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends
from redis.asyncio import Redis

from src.db.redis import get_redis


class AuthorizationService:
    def __init__(self, redis, auth_jwt):
        self.redis: Redis = redis
        self.auth_jwt: AuthJWT = auth_jwt

    async def new_token_pair(self, user_id):
        # await self.refresh_token_set_used()

        new_access_token = await self.auth_jwt.create_access_token(subject=user_id)
        new_refresh_token = await self.auth_jwt.create_refresh_token(subject=user_id)

        await self.auth_jwt.set_access_cookies(new_access_token)
        await self.auth_jwt.set_refresh_cookies(new_refresh_token)

        await self.refresh_token_set_ready(token=new_refresh_token)

    # async def refresh_token_set_used(self):
    #     # await self.auth_jwt.get_jwt_subject()
    #     self.auth_jwt.get_jti()
    #     raw_refresh_token = await self.auth_jwt.get_raw_jwt()
    #     if not raw_refresh_token:
    #         return None
    #     jti = raw_refresh_token['jti']
    #     await self.redis.set(name=jti, value='used', keepttl=True)

    async def refresh_token_set_ready(self, token=None):
        raw_refresh_token = await self.auth_jwt.get_raw_jwt(token)
        jti = raw_refresh_token['jti']
        exp = raw_refresh_token['exp']
        await self.redis.set(name=jti, value='ready', exat=exp)


async def get_authorization_service(redis: Redis = Depends(get_redis), auth_jwt: AuthJWT = Depends(AuthJWT)):
    return AuthorizationService(redis, auth_jwt)


# @AuthJWT.token_in_denylist_loader
# async def check_if_refresh_token_in_denylist(
#     decrypted_token: dict, redis: Annotated[Redis, Depends(get_redis)]
# ) -> bool:
#     """
#     Callback which checks if refresh token in the list of used tokens.
#     Refresh token intended for single use. So used marks as 'used'.
#
#     If callback result():
#         False -> The user gets one-time accesses to the endpoint where the refresh token is required.
#         True -> The user has no valid refresh token in cookies. Access is not allowed.
#
#     Each key in Redis is a JTI (=unique ID) of refresh token.
#     Each value can get one of three states:
#         None: A token is not in Redis. Expected callback result = True.
#             Possible when submitted token is fake.
#         'used': A token already was used. Expected callback result = True.
#             Possible when user (or attacker) is trying to reuse token.
#         'ready': A token is ready to use. Expected callback result = False.
#             Possible when user has correct refresh token.
#
#     Returns:
#         False: If token JTI == 'ready'.
#         True: In any other cases.
#     """
#     jti = decrypted_token['jti']
#
#     token_status = await redis.get(jti)
#     if token_status == 'ready':
#         return False
#     return True
#     # if token_status == 'ready':
#     #     await redis.set(name=jti, value='used', keepttl=True)
#     #     return False
#     #
#     # return True
