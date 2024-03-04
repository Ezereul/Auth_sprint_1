import uuid
from http import HTTPStatus

import pytest
from sqlalchemy import select

from src.models import Role, User


@pytest.mark.asyncio
async def test_get_roles(superuser_authenticated_client, test_db_session, roles_fixture):
    db_roles = (await test_db_session.scalars(select(Role))).all()
    expected_roles = [{"id": role.id, "name": role.name, "access_level": role.access_level} for role in db_roles]

    response = await superuser_authenticated_client.get("/role/")

    assert response.status_code == HTTPStatus.OK

    response_data = response.json()

    for role_response, expected_role in zip(response_data, expected_roles):
        assert role_response['id'] == str(expected_role['id'])
        assert role_response["name"] == expected_role["name"]
        assert role_response["access_level"] == expected_role["access_level"]


@pytest.mark.asyncio
async def test_cant_create_existing_role(superuser_authenticated_client, test_db_session):
    response = await superuser_authenticated_client.post("/role/create", json={'name': 'testrole', 'access_level': 1})

    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.parametrize("action, body", [
    ("patch", {'name': 'testrole', 'access_level': 2}),
    ("delete", {})
])
@pytest.mark.asyncio
async def test_nonexistent_role(superuser_authenticated_client, action, body):
    nonexistent_id = str(uuid.uuid4())
    url = "/role/" + nonexistent_id
    method = getattr(superuser_authenticated_client, action)

    response = await method(url, json={'name': 'role', 'access_level': 2}) if action == "patch" else await method(url)

    assert response.status_code == HTTPStatus.NOT_FOUND


async def role_exists(test_db_session, role_data):
    result = await test_db_session.scalars(select(Role).where(Role.name == role_data['name']))
    return result.first() is not None


async def role_access_level_matches(test_db_session, role_data):
    result = await test_db_session.scalars(select(Role).where(Role.name == role_data['name']))
    role = result.first()
    await test_db_session.refresh(role)
    return role.access_level == role_data['access_level']


async def role_not_exists(test_db_session, role_data):
    result = await test_db_session.scalars(select(Role).where(Role.name == role_data['name']))
    return result.first() is None


@pytest.mark.asyncio
@pytest.mark.parametrize("action,role_data,expected_status,post_action", [
    # Создание новой роли
    (
            "post",
            {'name': 'newrole', 'access_level': 1},
            HTTPStatus.CREATED,
            role_exists
    ),
    # Обновление роли
    (
            "patch",
            {'name': 'testrole', 'access_level': 2},
            HTTPStatus.OK,
            role_access_level_matches
    ),
    # Удаление роли
    (
            "delete",
            {'name': 'testrole'},
            HTTPStatus.OK,
            role_not_exists
    ),
])
async def test_role_management(superuser_authenticated_client, test_db_session, roles_fixture, action, role_data,
                               expected_status, post_action):
    role_id = roles_fixture[role_data['name']].id if role_data.get('name') in roles_fixture else None
    url = "/role/" + ("create" if action == "post" else "") + (f"{role_id}" if role_id else "")
    method = getattr(superuser_authenticated_client, action)

    response = await method(url) if action == "delete" else await method(url, json=role_data)

    assert response.status_code == expected_status
    assert await post_action(test_db_session, role_data)


@pytest.mark.parametrize("method, endpoint, payload", [
    ("post", "/role/create", {'name': 'newrole', 'access_level': 1}),

    ("get", "/role/", None),

    ("patch", "/role/{role_id}", {'name': 'testrole', 'access_level': 2}),

    ("delete", "/role/{role_id}", None),
])
@pytest.mark.asyncio
async def test_user_cant_reach_roles(authenticated_client, method, endpoint, payload, roles_fixture):
    if "{role_id}" in endpoint:
        role_id = roles_fixture['testrole'].id
        endpoint = endpoint.format(role_id=role_id)

    request_method = getattr(authenticated_client, method)
    response = await request_method(endpoint, json=payload) if payload else await request_method(endpoint)

    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_assign_role_to_user(superuser_authenticated_client, test_db_session, user_fixture, roles_fixture):
    username = user_fixture.username
    role_name = roles_fixture['testrole'].name

    response = await superuser_authenticated_client.post(
        "/role/assign",
        params={"username": username, "role_name": role_name}
    )

    assert response.status_code == HTTPStatus.OK

    response_json = response.json()

    assert response_json["username"] == username
    assert response_json["role"]["name"] == role_name

    user = (await test_db_session.scalars(select(User).where(User.username == username))).first()
    await test_db_session.refresh(user)

    assert user.role.name == role_name


@pytest.mark.asyncio
async def test_revoke_role_from_user(superuser_authenticated_client, test_db_session, user_fixture, roles_fixture):
    username = user_fixture.username

    response = await superuser_authenticated_client.post(
        "/role/revoke",
        params={"username": username}
    )

    assert response.status_code == HTTPStatus.OK

    response_json = response.json()

    assert response_json["username"] == username
    assert response_json["role"]["name"] == roles_fixture['user'].name

    user = (await test_db_session.scalars(select(User).where(User.username == username))).first()

    assert user.role.name == roles_fixture['user'].name


@pytest.mark.parametrize("endpoint, params", [
    ("/role/assign", {"username": "nonexistent", "role_name": "testrole"}),
    ("/role/assign", {"username": "testuser", "role_name": "nonexistent"}),
    ("/role/revoke", {"username": "nonexistent", "role_name": "testrole"}),
    ("/role/revoke", {"username": "testuser", "role_name": "nonexistent"}),
])
@pytest.mark.asyncio
async def test_error_on_nonexistent_user_or_role(superuser_authenticated_client, endpoint, params):
    response = await superuser_authenticated_client.post(endpoint, params=params)

    assert response.status_code == HTTPStatus.NOT_FOUND
