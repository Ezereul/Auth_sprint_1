from passlib.context import CryptContext


# add restoring CryptContext (?)
pwd_context = CryptContext(
    schemes=[
        'pbkdf2_sha256',
    ],
    deprecated='auto',
)


def to_hash(not_hashed: str) -> str:
    password_hash = pwd_context.hash(not_hashed)
    return password_hash


def verify(not_hashed: str, hashed: str) -> bool:
    return pwd_context.verify(not_hashed, hashed)


def is_password_safe(password: str) -> bool:
    """
    Check password for safety.

    Requirements:
        1. Has length >= 8.
        2. Contains at least one upper-case letter.
        3. Contains at least one lower-case letter.
        4. Contains at least one digit.

    :param password: A password string.
    :return: True if all checks passed, else False.
    """
    constraints = (
        len(password) > 7,
        any(symbol.isupper() for symbol in password),
        any(symbol.islower() for symbol in password),
        any(symbol.isdigit() for symbol in password),
    )
    return all(constraints)
