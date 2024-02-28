from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends, HTTPException, status


def has_permission(required_access_level: int):
    async def access_level_checker(Authorize: AuthJWT = Depends()):
        await Authorize.jwt_required()
        token_access_level = (await Authorize.get_raw_jwt()).get("access_level", 0)

        if not check_access_level(token_access_level, required_access_level):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    return access_level_checker


def check_access_level(token_access_level: int, required_access_level: int) -> bool:
    return token_access_level >= required_access_level
