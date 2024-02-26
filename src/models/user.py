from passlib.context import CryptContext
from sqlalchemy import Column, String, UUID, ForeignKey
from sqlalchemy.orm import relationship

from src.core.db import Base


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class User(Base):
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role_id = Column(UUID, ForeignKey('role.id'))

    role = relationship("Role", back_populates='users')
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
