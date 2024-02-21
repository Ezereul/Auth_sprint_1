from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.api.v1 import auth
from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import AuthJWTException

from src.core.config import Settings

app = FastAPI()


@AuthJWT.load_config
def get_settings():
    return Settings()


@app.exception_handler(AuthJWTException)  # add orjson to tweak performance
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


app.include_router(auth.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
