from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.core.db import Base


class Role(Base):
    name = Column(String(50), unique=True, index=True, nullable=False)
    access_level = Column(Integer, nullable=False)
    users = relationship("User", back_populates="role")
