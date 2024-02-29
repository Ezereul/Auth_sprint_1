from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import UUID, Column, ForeignKey, String
from sqlalchemy.orm import relationship, validates

from src.core.db import Base

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class User(Base):
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role_id = Column(UUID, ForeignKey('role.id'), nullable=False)

    role = relationship("Role", back_populates='users')
    login_history = relationship("LoginHistory", back_populates="user", lazy='dynamic', cascade='all, delete')

    @validates('username')
    def validate_username(self, key, username):
        if len(username) < 4:
            raise ValueError('Username length must be > 3')
        if self.is_correct_password(username):
            raise ValueError('Username cannot be same as password')
        return username

    @property
    def password(self):
        return None

    @password.setter
    def password(self, password: str):
        if len(password) < 8:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Password length must be > 7')
        if password == self.username:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Password cannot be same as Username')

        self.password_hash = pwd_context.hash(password)

    def is_correct_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password_hash)

    def __repr__(self):
        return f'<User(email={self.username})>'
