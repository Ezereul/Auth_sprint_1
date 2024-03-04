from http import HTTPStatus

import pytest
from sqlalchemy import select

from src.models import User


@pytest.mark.asyncio
async def test_register_success(client_fixture, test_db_session, roles_fixture):
    response = await client_fixture.post('/auth/register', json={
        'username': 'newuser',
        'password': 'strongpassword'
    })

    assert response.status_code == HTTPStatus.CREATED
    assert 'username' in response.json()
    assert response.json()['username'] == 'newuser'

    user = (await test_db_session.scalars(select(User).where(User.username == 'newuser'))).first()  # noqa

    assert user is not None
    assert user.role_id == roles_fixture["user"].id


@pytest.mark.asyncio
async def test_register_weak_password(client_fixture, test_db_session):
    response = await client_fixture.post('/auth/register', json={
        'username': 'anotheruser',
        'password': 'weak'
    })

    assert response.status_code == HTTPStatus.BAD_REQUEST

    user = (await test_db_session.scalars(select(User).where(User.username == 'newuser'))).first()  # noqa

    assert user is None


@pytest.mark.asyncio
async def test_register_existing_username(client_fixture, user_fixture):
    response = await client_fixture.post('/auth/register', json={
        'username': user_fixture.username,
        'password': 'anotherstrongpassword'
    })

    assert response.status_code == HTTPStatus.CONFLICT


@pytest.mark.asyncio
async def test_login_success(client_fixture, user_fixture):
    response = await client_fixture.post('/auth/login', json={
        'username': user_fixture.username,
        'password': 'testpassword'
    })

    assert response.status_code == HTTPStatus.OK
    assert 'detail' in response.json()
    assert response.json()['detail'] == 'Successfully login'

    cookies = response.headers.get('set-cookie')

    assert cookies is not None
    assert 'access_token_cookie=' in cookies


@pytest.mark.asyncio
async def test_login_wrong_password(client_fixture, user_fixture):
    response = await client_fixture.post('/auth/login', json={
        'username': user_fixture.username,
        'password': 'wrongpassword'
    })

    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_login_nonexistent_user(client_fixture):
    response = await client_fixture.post('/auth/login', json={
        'username': 'nonexistentuser',
        'password': 'somepassword'
    })

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_refresh_token(authenticated_client):
    response = await authenticated_client.post("/auth/refresh")

    assert response.status_code == HTTPStatus.OK

    cookies = response.headers.get('set-cookie')

    assert cookies is not None
    assert 'access_token_cookie=' in cookies


@pytest.mark.asyncio
async def test_logout(authenticated_client):
    refresh_token_cookie = authenticated_client.cookies.get("refresh_token_cookie")
    logout_response = await authenticated_client.post(
        "/auth/logout",
        cookies={"refresh_token_cookie": refresh_token_cookie}
    )

    assert logout_response.status_code == HTTPStatus.OK
    assert "set-cookie" in logout_response.headers
    assert 'refresh_token_cookie=""' in logout_response.headers["set-cookie"]

    protected_response = await authenticated_client.post(
        "/auth/refresh",
        cookies={"refresh_token_cookie": refresh_token_cookie}
    )

    assert protected_response.status_code == HTTPStatus.UNAUTHORIZED
