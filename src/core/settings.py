from pydantic import BaseModel


class Settings(BaseModel):
    authjwt_secret_key: str = "Secret key"
    authjwt_token_location: set = {"cookies"}
    # temporary disabling CSRF for development needs. Must be True on prod.
    authjwt_cookie_csrf_protect: bool = False
