from pydantic import BaseModel


class UserBase(BaseModel):
    """Base model for User."""
    username: str


class UserDB(UserBase):
    """Output model for registration handler."""
    pass


class UserLogin(UserBase):
    """Input model for login handler."""
    password: str


class UserCreateOrUpdate(UserLogin):
    """Input model for registration handler."""
    pass
