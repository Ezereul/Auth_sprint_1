from pydantic import BaseModel


class UserDB(BaseModel):
    id: str
    username: str
    password: str
