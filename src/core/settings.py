from pathlib import Path

from async_fastapi_jwt_auth import AuthJWT
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_PATH = PROJECT_ROOT / '.env'


class RedisSettings(BaseSettings):
    host: str = '127.0.0.1'
    port: int = 6379

    model_config = SettingsConfigDict(env_prefix='REDIS_', env_file=ENV_PATH, extra='ignore')


class LoggerSettings(BaseSettings):
    level: str
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    default_handlers: list = ['console', ]
    level_console: str = 'DEBUG'
    level_handlers: str = 'INFO'
    level_unicorn_errors: str = 'INFO'
    level_unicorn_access: str = 'INFO'
    level_root: str = 'INFO'

    model_config = SettingsConfigDict(env_prefix='LOG_', env_file=ENV_PATH, extra='ignore')


class AuthSettings(BaseSettings):
    """
    More about config:
    https://sijokun.github.io/async-fastapi-jwt-auth/configuration/cookies/
    """
    authjwt_algorithm: str
    authjwt_public_key: str
    authjwt_private_key: str
    authjwt_access_token_expires: int
    authjwt_refresh_token_expires: int
    authjwt_cookie_secure: bool  # now False, recommended to True in prod
    authjwt_cookie_csrf_protect: bool  # now False, recommended tot True in prod
    authjwt_cookie_samesite: str = 'none'  # def: 'none', recommended 'lax' in prod, available 'strict', 'lax', 'none'

    # Never changes! Required to core functions.
    authjwt_denylist_enabled: bool = False  # now False, must be True but denylist is not ready yet
    authjwt_denylist_token_checks: set = {'refresh'}
    authjwt_token_location: set = {'cookies'}

    model_config = SettingsConfigDict(env_file=ENV_PATH, extra='ignore')


class Settings(BaseSettings):
    redis: RedisSettings = RedisSettings()
    logger: LoggerSettings = LoggerSettings()
    auth: AuthSettings = AuthSettings()

    project_name: str
    version: str

    model_config = SettingsConfigDict(env_file=ENV_PATH, extra='ignore')


settings = Settings()


@AuthJWT.load_config
def set_auth_settings():
    return settings.auth
