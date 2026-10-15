from app.core.config import settings


async def register_user(client, email: str, username: str):
    response = await client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": "Testpassword123!",
        },
    )

    assert response.status_code == 201


async def test_login_sets_configured_authentication_cookie(client):
    await register_user(client, "cookie-login@example.com", "cookie-login")

    response = await client.post(
        "/auth/login",
        headers={"Origin": settings.FRONTEND_ORIGIN},
        json={
            "email": "cookie-login@example.com",
            "password": "Testpassword123!",
        },
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert "access_token" in response.json()

    set_cookie = response.headers["set-cookie"]
    assert f"{settings.AUTH_COOKIE_NAME}=" in set_cookie
    assert "HttpOnly" in set_cookie
    assert f"Path={settings.AUTH_COOKIE_PATH}" in set_cookie
    assert f"SameSite={settings.AUTH_COOKIE_SAMESITE}" in set_cookie
    assert "Max-Age=" in set_cookie

    if settings.AUTH_COOKIE_SECURE:
        assert "Secure" in set_cookie


async def test_login_rejects_invalid_credentials_without_setting_cookie(client):
    await register_user(client, "invalid-login@example.com", "invalid-login")

    response = await client.post(
        "/auth/login",
        headers={"Origin": settings.FRONTEND_ORIGIN},
        json={
            "email": "invalid-login@example.com",
            "password": "Wrongpassword123!",
        },
    )

    assert response.status_code == 401
    assert "set-cookie" not in response.headers


async def test_login_rejects_untrusted_or_missing_origin(client):
    await register_user(client, "origin-login@example.com", "origin-login")

    for headers in ({}, {"Origin": "https://untrusted.example"}):
        response = await client.post(
            "/auth/login",
            headers=headers,
            json={
                "email": "origin-login@example.com",
                "password": "Testpassword123!",
            },
        )

        assert response.status_code == 403
        assert response.json() == {"detail": "CSRF validation failed"}


async def test_logout_clears_authentication_cookie_with_trusted_origin(client):
    response = await client.post(
        "/auth/logout",
        headers={"Origin": settings.FRONTEND_ORIGIN},
    )

    assert response.status_code == 204
    set_cookie = response.headers["set-cookie"]
    assert f"{settings.AUTH_COOKIE_NAME}=" in set_cookie
    assert "Max-Age=0" in set_cookie
    assert f"Path={settings.AUTH_COOKIE_PATH}" in set_cookie


async def test_logout_rejects_missing_or_untrusted_origin(client):
    for headers in ({}, {"Origin": "https://untrusted.example"}):
        response = await client.post("/auth/logout", headers=headers)

        assert response.status_code == 403
        assert response.json() == {"detail": "CSRF validation failed"}
