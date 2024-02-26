from pydantic import BaseModel

from src.schemas.roles import RoleCRUD


class UserBase(BaseModel):
    username: str


class UserDB(UserBase):
    pass


class UserLogin(UserBase):
    password: str


class UserCreateOrUpdate(UserLogin):
    pass


class UserWithRole(BaseModel):
    username: str
    role: RoleCRUD | None = None
