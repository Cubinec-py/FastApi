from sqlalchemy import insert, select

from auth.models import Role
from conftest import client, async_session_maker


async def test_add_role():
    async with async_session_maker() as session:
        stmt = insert(Role).values(id=1, name="admin", permissions=None)
        await session.execute(stmt)
        await session.commit()

        query = select(Role)
        result = await session.execute(query)
        assert result.all() == [(1, "admin", None)], "Роль не добавилась"


def test_register():
    response = client.post(
        "/api/v1/register",
        json={
            "email": "string@example.com",
            "password": "string",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
            "username": "string",
            "role_id": 1,
        },
    )

    assert response.status_code == 201


async def test_login():
    response = await client.post(
        "/api/v1/login",
        json={
            "email": "string@example.com",
            "password": "string",
        },
    )

    assert response.status_code == 200
