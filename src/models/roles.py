from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from src.core.db import Base


class Role(Base):
    name = Column(String, unique=True, index=True, nullable=False)
    access_level = Column(Integer, nullable=False)
    users = relationship("User", back_populates="role")
