from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    test_database_url: str = 'postgresql+asyncpg://test:test@localhost:5432/test'


settings = Settings()
