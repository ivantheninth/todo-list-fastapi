from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings


def cookie_headers(token: str) -> dict[str, str]:
    return {"Cookie": f"{settings.AUTH_COOKIE_NAME}={token}"}


async def register_and_login(client, email: str, username: str):
    register_response = await client.post(
        "/auth/register",
        headers={"Origin": settings.FRONTEND_ORIGIN},
        json={
            "username": username,
            "email": email,
            "password": "Testpassword123!",
        },
    )
    login_response = await client.post(
        "/auth/login",
        headers={"Origin": settings.FRONTEND_ORIGIN},
        json={
            "email": email,
            "password": "Testpassword123!",
        },
    )

    assert register_response.status_code == 201
    assert login_response.status_code == 200

    return register_response.json()["id"], login_response.json()["access_token"]


async def test_authenticated_user_can_use_valid_jwt_cookie(client):
    _, token = await register_and_login(
        client,
        "cookie-user@example.com",
        "cookie-user",
    )

    response = await client.get(
        "/auth/me",
        headers=cookie_headers(token),
    )

    assert response.status_code == 200
    assert response.json()["email"] == "cookie-user@example.com"


async def test_expired_jwt_cookie_is_rejected(client):
    user_id, _ = await register_and_login(
        client,
        "expired-cookie@example.com",
        "expired-cookie",
    )
    expired_token = jwt.encode(
        {
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    response = await client.get(
        "/auth/me",
        headers=cookie_headers(expired_token),
    )

    assert response.status_code == 401


async def test_missing_credentials_are_rejected(client):
    response = await client.get("/auth/me")

    assert response.status_code == 401


async def test_authenticated_user_can_use_valid_bearer_token(client):
    _, token = await register_and_login(
        client,
        "bearer-user@example.com",
        "bearer-user",
    )

    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "bearer-user@example.com"


async def test_conflicting_cookie_and_bearer_credentials_are_rejected(
    client,
):
    _, bearer_token = await register_and_login(
        client,
        "bearer-user@example.com",
        "bearer-user",
    )
    _, cookie_token = await register_and_login(
        client,
        "cookie-user@example.com",
        "cookie-user",
    )

    response = await client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {bearer_token}",
            **cookie_headers(cookie_token),
        },
    )

    assert response.status_code == 401
