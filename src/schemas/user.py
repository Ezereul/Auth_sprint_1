from pydantic import BaseModel

class UserBase(BaseModel):
    username: str


class UserDB(UserBase):
    pass


class UserLogin(UserBase):
    password: str


class UserCreateOrUpdate(UserLogin):
    pass
