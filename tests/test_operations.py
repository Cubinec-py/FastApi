from httpx import AsyncClient


async def test_add_specific_operations(ac: AsyncClient):
    token = await ac.post(
        "/api/v1/login",
        json={
            "email": "string@example.com",
            "password": "string",
        }
    )
    response = await ac.post(
        "/api/v1/operations",
        headers={"accept": "application/json", "Authorization": f"Bearer {token.json()['access_token']}"},
        json={
            "id": 1,
            "quantity": "25.5",
            "figi": "figi_CODE",
            "instrument_type": "bond",
            "date": "2023-05-07T13:17:30.795",
            "type": "Выплата купонов",
        },
    )
    assert response.status_code == 200


async def test_get_specific_operations(ac: AsyncClient):
    token = await ac.post(
        "/api/v1/login",
        json={
            "email": "string@example.com",
            "password": "string",
        }
    )
    response = await ac.get(
        "/api/v1/operations",
        headers={"accept": "application/json", "Authorization": f"Bearer {token.json()['access_token']}"},
        params={
            "operation_type": "Выплата купонов",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert len(response.json()["data"]) == 1
