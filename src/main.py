from async_fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.api import v1
from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from src.core.settings import settings

from src.core.settings import Settings

app = FastAPI()


@AuthJWT.load_config
def get_settings():
    return Settings()
app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    debug=True,
    log_config=logger.LOGGING_DICT_CONFIG,
    log_level=settings.logger.level,
)

app.include_router(v1.router)


@app.exception_handler(AuthJWTException)  # add orjson to tweak performance
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
