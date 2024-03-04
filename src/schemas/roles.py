from pydantic import UUID4, BaseModel, ConfigDict


class RoleDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    name: str
    access_level: int


class RoleCRUD(BaseModel):
    name: str
    access_level: int
