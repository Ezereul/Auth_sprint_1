from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from passlib.context import CryptContext

from src.core.db import Base


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    roles = relationship("Role", secondary="user_roles", back_populates="users", lazy='dynamic')
    login_history = relationship("LoginHistory", back_populates="user", lazy='dynamic')

    @property
    def password(self):
        return None

    @password.setter
    def password(self, password: str):
        self.password_hash = pwd_context.hash(password)

    def is_correct_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password_hash)

    def __repr__(self):
        return (f'<User(email={self.username}>')
