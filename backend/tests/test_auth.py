async def test_get_current_user(client):
    register_response = await client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
        },
    )

    assert register_response.status_code == 201

    login_response = await client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = await client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["id"], int)
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"