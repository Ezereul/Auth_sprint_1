from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship, validates

from src.core.db import Base


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class User(Base):
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    roles = relationship("Role", secondary="user_roles", back_populates="users", lazy='dynamic')
    login_history = relationship("LoginHistory", back_populates="user", lazy='dynamic')

    @validates('username')
    def validate_username(self, key, username):
        if len(username) < 4:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Username length must be > 3')
        if self.is_correct_password(username):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Username cannot be same as password')
        return username

    @property
    def password(self):
        return None

    @password.setter
    def password(self, password: str):
        if len(password) < 8:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Password length must be > 7')
        if password == self.username:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Password cannot be same as Username')

        self.password_hash = pwd_context.hash(password)

    def is_correct_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password_hash)

    def __repr__(self):
        return f'<User(email={self.username})>'
