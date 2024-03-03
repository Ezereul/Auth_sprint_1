import fakeredis
import pytest
import pytest_asyncio

from src.db.redis import get_redis
from src.main import app


@pytest_asyncio.fixture
async def fake_redis():
    redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield redis
    await redis.aclose()


@pytest.fixture
def app_with_overridden_redis(fake_redis):
    app.dependency_overrides[get_redis] = lambda: fake_redis
    return app
