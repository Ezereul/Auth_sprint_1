from http import HTTPStatus

import pytest
from sqlalchemy import select

from src.models import LoginHistory


@pytest.mark.asyncio
async def test_get_history(authenticated_client, test_db_session, user_fixture):
    history = (await test_db_session.scalars(select(LoginHistory).where(LoginHistory.user_id == user_fixture.id))).all()  # noqa
    expected_history = [{"user_id": user_fixture.id, "login_time": login.login_time} for login in history]

    response = await authenticated_client.get("/history/")

    assert response.status_code == HTTPStatus.OK

    response_data = response.json()["items"]

    for role_response, expected_login in zip(response_data, expected_history):
        assert role_response['user_id'] == str(expected_login['user_id'])
        assert role_response["login_time"] == expected_login["login_time"].isoformat()


@pytest.mark.parametrize('query_data, expected_status', [
    ({"page": 1, "size": 50}, HTTPStatus.OK),
    ({"page": 0, "size": 50}, HTTPStatus.BAD_REQUEST),
    ({"page": 1, "size": 0}, HTTPStatus.BAD_REQUEST),
])
@pytest.mark.asyncio
async def test_get_history_validation(authenticated_client, query_data, expected_status):
    response = await authenticated_client.get("/history/", params=query_data)

    assert response.status_code == expected_status
