from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from src.core.db import Base


class LoginHistory(Base):
    user_id = Column(Integer, ForeignKey("user.id"))
    login_time = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="loginhistory")