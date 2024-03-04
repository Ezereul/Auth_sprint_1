import pytest
import pytest_asyncio
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.db import Base, get_async_session
from src.main import app
from src.models import LoginHistory, Role, User
from tests.functional.settings import settings


@pytest_asyncio.fixture(autouse=True)
async def clean_db(test_db_session):
    models = [LoginHistory, User, Role]
    for model in models:
        await test_db_session.execute(delete(model))
    await test_db_session.commit()


@pytest_asyncio.fixture
async def test_db_session():
    engine = create_async_engine(settings.test_database_url)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        yield session
        await session.rollback()

    await engine.dispose()


@pytest.fixture
def app_with_overridden_db(test_db_session):
    app.dependency_overrides[get_async_session] = lambda: test_db_session
    return app
