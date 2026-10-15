import pytest

from app.core.config import settings


def cookie_headers(token: str) -> dict[str, str]:
    return {"Cookie": f"{settings.AUTH_COOKIE_NAME}={token}"}


async def register_and_login(client, email: str, username: str) -> str:
    register_response = await client.post(
        "/auth/register",
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

    return login_response.json()["access_token"]


async def create_task(client, headers: dict[str, str]):
    return await client.post(
        "/tasks",
        headers=headers,
        json={"title": "CSRF-protected task"},
    )


async def test_cookie_authenticated_post_allows_trusted_origin(client):
    token = await register_and_login(
        client,
        "trusted@example.com",
        "trusted-user",
    )

    response = await create_task(
        client,
        {
            **cookie_headers(token),
            "Origin": settings.FRONTEND_ORIGIN,
        },
    )

    assert response.status_code == 201


async def test_cookie_authenticated_post_rejects_untrusted_origin(client):
    token = await register_and_login(
        client,
        "untrusted@example.com",
        "untrusted-user",
    )

    response = await create_task(
        client,
        {
            **cookie_headers(token),
            "Origin": "https://untrusted.example",
        },
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "CSRF validation failed"}


@pytest.mark.parametrize("origin", [None, "null", "https://example.com/path"])
async def test_cookie_authenticated_post_rejects_missing_or_malformed_origin(
    client,
    origin,
):
    token = await register_and_login(
        client,
        f"csrf-{origin is None}@example.com",
        f"csrf-{origin is None}",
    )
    headers = cookie_headers(token)

    if origin is not None:
        headers["Origin"] = origin

    response = await create_task(client, headers)

    assert response.status_code == 403
    assert response.json() == {"detail": "CSRF validation failed"}


async def test_cookie_authenticated_safe_get_does_not_require_origin(client):
    token = await register_and_login(
        client,
        "safe-get@example.com",
        "safe-get-user",
    )

    response = await client.get(
        "/auth/me",
        headers=cookie_headers(token),
    )

    assert response.status_code == 200


async def test_bearer_only_post_does_not_require_origin(client):
    token = await register_and_login(
        client,
        "bearer-only@example.com",
        "bearer-only-user",
    )
    client.cookies.clear()

    response = await create_task(
        client,
        {"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201


async def test_mixed_bearer_and_cookie_post_requires_origin(client):
    token = await register_and_login(
        client,
        "mixed@example.com",
        "mixed-user",
    )

    response = await create_task(
        client,
        {
            **cookie_headers(token),
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "CSRF validation failed"}
