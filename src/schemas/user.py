from pydantic import BaseModel


class UserBase(BaseModel):
    email: str


class UserDB(UserBase):
    pass


class UserLogin(UserBase):
    password: str


class UserCreate(UserLogin):
    pass
