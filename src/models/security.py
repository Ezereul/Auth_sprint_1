from passlib.context import CryptContext

# add restoring CryptContext (?)
pwd_context = CryptContext(
    schemes=['bcrypt',],
    deprecated='auto',
)
