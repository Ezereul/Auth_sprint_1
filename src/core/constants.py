from enum import IntEnum

DEFAULT_ROLE_DATA = {
    'name': 'user',
    'access_level': 1
}

SUPERUSER_ROLE_DATA = {
    'name': 'superuser',
    'access_level': 20
}


class RoleAccess(IntEnum):
    USER = 1
    ADMIN = 10
    SUPERUSER = 20
