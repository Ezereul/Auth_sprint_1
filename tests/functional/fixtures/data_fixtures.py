import pytest_asyncio

from src.core.constants import DEFAULT_ROLE_DATA, SUPERUSER_ROLE_DATA
from src.models import Role, User


@pytest_asyncio.fixture
async def user_fixture(test_db_session, roles_fixture):
    user_role = roles_fixture['user']
    new_user = User(username="testuser", password="testpassword", role=user_role)
    test_db_session.add(new_user)
    await test_db_session.commit()
    await test_db_session.refresh(new_user)
    yield new_user


@pytest_asyncio.fixture
async def superuser_fixture(test_db_session, roles_fixture):
    superuser_role = roles_fixture['superuser']
    superuser = User(username="testsuperuser", password="testpassword", role=superuser_role)
    test_db_session.add(superuser)
    await test_db_session.commit()
    await test_db_session.refresh(superuser)
    yield superuser


@pytest_asyncio.fixture
async def roles_fixture(test_db_session):
    roles = {
        "user": Role(**DEFAULT_ROLE_DATA),
        "superuser": Role(**SUPERUSER_ROLE_DATA),
        "testrole": Role(name="testrole", access_level=1)
    }
    test_db_session.add_all(roles.values())
    await test_db_session.commit()
    yield roles
