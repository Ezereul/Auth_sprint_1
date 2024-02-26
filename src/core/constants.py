from enum import IntEnum

DEFAULT_ROLE_DATA = {
    'name': 'user',
    'access_level': 1
}

SUPERUSER_ROLE_DATA = {
    'name': 'admin',
    'access_level': 10
}


class RoleAccess(IntEnum):
    USER = 1
    ADMIN = 10
    SUPERUSER = 20
