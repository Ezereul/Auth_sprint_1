from pydantic import UUID4, BaseModel


class RoleDB(BaseModel):
    id: UUID4
    name: str
    access_level: int

    class Config:
        from_attributes = True


class RoleCRUD(BaseModel):
    name: str
    access_level: int
