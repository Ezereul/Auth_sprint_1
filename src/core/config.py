from pydantic import BaseModel


class Settings(BaseModel):
    database_url: str = 'postgresql+asyncpg://app:11111@localhost:5432/auth'
    authjwt_secret_key: str = "Secret key"
    authjwt_token_location: set = {"cookies"}
    # temporary disabling CSRF for development needs. Must be True on prod.
    authjwt_cookie_csrf_protect: bool = False

    class Config:
        env_file = '../../.env'


settings = Settings()
