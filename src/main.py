from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import AuthJWTException

app = FastAPI()


class User(BaseModel):
    username: str
    password: str


class Settings(BaseModel):
    authjwt_secret_key: str = "Secret key"


@AuthJWT.load_config
def get_config():
    return Settings()


@app.exception_handler(AuthJWTException)  # add orjson to tweak performance
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.post("/login")
async def login(user: User, Authorize: AuthJWT = Depends()):
    if user.username != "test" or user.password != "test":
        raise HTTPException(status_code=401, detail="Bad username or password")

    access_token = await Authorize.create_access_token(subject=user.username)
    return {"access_token": access_token}


@app.get("/user")
async def user(Authorize: AuthJWT = Depends()):
    await Authorize.jwt_required()

    current_user = await Authorize.get_jwt_subject()
    return {"user": current_user}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
