from contextlib import asynccontextmanager

from async_fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from redis.asyncio import Redis

from src.api.routers import main_router
from src.api.errors import authjwt_exception_handler, account_exception_handler
from src.core import logger
from src.core.config import settings
from src.db import redis
from src.services.account import AccountDataException


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(host=settings.redis.host, port=settings.redis.port, decode_responses=True)
    yield
    await redis.redis.close()


app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    lifespan=lifespan,
    log_config=logger.LOGGING_DICT_CONFIG,
    log_level=settings.logger.level,
    default_response_class=JSONResponse,
)
app.include_router(account.account_router, prefix='/account')
app.add_exception_handler(AuthJWTException, authjwt_exception_handler)
app.add_exception_handler(AccountDataException, account_exception_handler)
app.include_router(main_router)


@app.exception_handler(AuthJWTException)  # add orjson to tweak performance
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={'detail': exc.message})


if __name__ == '__main__':
    import uvicorn

    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
