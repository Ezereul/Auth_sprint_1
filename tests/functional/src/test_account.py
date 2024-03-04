from http import HTTPStatus

import pytest
from sqlalchemy import select

from src.models import User


@pytest.mark.asyncio
async def test_change_username(authenticated_client, test_db_session, user_fixture):
    request_params = {"new_username": "new_name"}
    response = await authenticated_client.post("/account/change_username", params=request_params)

    assert response.status_code == HTTPStatus.OK

    user = (await test_db_session.scalars(select(User).where(User.username == request_params["new_username"]))).first()  # noqa

    assert user is not None
    assert user.id == user_fixture.id


@pytest.mark.parametrize("params, expected", [
    ({"old_password": "wrong_password", "new_password": "password"}, HTTPStatus.BAD_REQUEST),
    ({"old_password": "testpassword", "new_password": "testpassword"}, HTTPStatus.BAD_REQUEST),
    ({"old_password": "testpassword", "new_password": "123"}, HTTPStatus.BAD_REQUEST),
    ({"old_password": "testpassword", "new_password": "new_password"}, HTTPStatus.OK)
])
@pytest.mark.asyncio
async def test_change_password(authenticated_client, params, expected, user_fixture, test_db_session):
    response = await authenticated_client.post("/account/change_password", params=params)

    assert response.status_code == expected

    if response.status_code == HTTPStatus.OK:
        await test_db_session.refresh(user_fixture)
        assert user_fixture.is_correct_password(params["new_password"])
