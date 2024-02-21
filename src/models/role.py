from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from src.core.db import Base


class Role(Base):
    name = Column(String, unique=True, index=True, nullable=False)
    users = relationship("User", secondary="user_roles", back_populates="roles")


user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("role_id", ForeignKey("role.id"), primary_key=True)
)