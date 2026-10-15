from types import SimpleNamespace
from http.cookies import SimpleCookie
from urllib.parse import parse_qs, urlparse

from app.api.routes import google_oauth
from app.core.config import settings
from app.core.security import create_access_token, decode_access_token
from app.crud.oauth_identity import oauth_identity_crud
from app.crud.user import user_crud
from app.db.models.oauth_identity import OAuthIdentity
from app.db.models.user import User


async def start_google_login(client):
    response = await client.get(
        "/auth/google/login",
        follow_redirects=False,
    )

    assert response.status_code == 302

    authorization_params = parse_qs(
        urlparse(response.headers["location"]).query,
    )
    oauth_cookie = response.cookies.get(
        google_oauth.GOOGLE_OAUTH_COOKIE_NAME,
    )

    assert oauth_cookie is not None

    return response, authorization_params, oauth_cookie


def cookie_headers(oauth_cookie: str) -> dict[str, str]:
    return {
        "Cookie": (
            f"{google_oauth.GOOGLE_OAUTH_COOKIE_NAME}={oauth_cookie}"
        ),
    }


def assert_oauth_cookie_was_cleared(response) -> None:
    set_cookie = next(
        value
        for value in response.headers.get_list("set-cookie")
        if value.startswith(f"{google_oauth.GOOGLE_OAUTH_COOKIE_NAME}=")
    )

    assert f"{google_oauth.GOOGLE_OAUTH_COOKIE_NAME}=" in set_cookie
    assert "Max-Age=0" in set_cookie


def get_response_cookie(response, name: str) -> tuple[str, str]:
    set_cookie = next(
        value
        for value in response.headers.get_list("set-cookie")
        if value.startswith(f"{name}=")
    )
    cookie = SimpleCookie()
    cookie.load(set_cookie)

    return cookie[name].value, set_cookie


def assert_authentication_cookie_was_issued(response) -> str:
    value, set_cookie = get_response_cookie(
        response,
        settings.AUTH_COOKIE_NAME,
    )

    assert "HttpOnly" in set_cookie
    assert f"Path={settings.AUTH_COOKIE_PATH}" in set_cookie
    assert f"SameSite={settings.AUTH_COOKIE_SAMESITE}" in set_cookie
    assert "Max-Age=" in set_cookie

    if settings.AUTH_COOKIE_SECURE:
        assert "Secure" in set_cookie

    return value


def assert_google_login_redirect(response) -> None:
    assert response.status_code == 303
    assert response.headers["location"] == settings.FRONTEND_ORIGIN
    assert not urlparse(response.headers["location"]).query


def assert_no_authentication_cookie(response) -> None:
    assert all(
        not value.startswith(f"{settings.AUTH_COOKIE_NAME}=")
        for value in response.headers.get_list("set-cookie")
    )


def mock_verified_google_identity(
    monkeypatch,
    email: str,
    subject: str,
) -> None:
    async def fake_exchange(*args, **kwargs) -> str:
        return "mock-id-token"

    async def fake_verify(*args, **kwargs):
        return google_oauth.VerifiedGoogleIdentity(
            subject=subject,
            email=email,
        )

    monkeypatch.setattr(
        google_oauth,
        "exchange_authorization_code",
        fake_exchange,
    )
    monkeypatch.setattr(
        google_oauth,
        "verify_google_id_token",
        fake_verify,
    )


async def complete_google_callback(
    client,
    oauth_cookie,
    state: str,
    authentication_cookie: str | None = None,
):
    headers = cookie_headers(oauth_cookie)
    if authentication_cookie is not None:
        headers["Cookie"] += (
            f"; {settings.AUTH_COOKIE_NAME}={authentication_cookie}"
        )

    return await client.get(
        "/auth/google/callback",
        params={
            "code": "authorization-code",
            "state": state,
        },
        headers=headers,
        follow_redirects=False,
    )


async def test_google_login_binds_state_nonce_and_pkce_to_secure_cookie(
    client,
):
    response, authorization_params, _ = await start_google_login(client)

    set_cookie = response.headers["set-cookie"]

    assert authorization_params["response_type"] == ["code"]
    assert authorization_params["scope"] == ["openid email profile"]
    assert authorization_params["state"][0]
    assert authorization_params["nonce"][0]
    assert authorization_params["code_challenge"][0]
    assert authorization_params["code_challenge_method"] == ["S256"]
    assert "HttpOnly" in set_cookie
    assert "Secure" in set_cookie
    assert "SameSite=lax" in set_cookie
    assert "Max-Age=300" in set_cookie


async def test_google_callback_exchanges_code_and_verifies_identity(
    client,
    monkeypatch,
):
    _, authorization_params, oauth_cookie = await start_google_login(client)
    oauth_data = google_oauth.oauth_serializer.loads(oauth_cookie)

    async def fake_exchange(code: str, code_verifier: str) -> str:
        assert code == "authorization-code"
        assert code_verifier == oauth_data["code_verifier"]
        return "mock-id-token"

    async def fake_verify(id_token: str, expected_nonce: str):
        assert id_token == "mock-id-token"
        assert expected_nonce == oauth_data["nonce"]
        return google_oauth.VerifiedGoogleIdentity(
            subject="google-subject-123",
            email="user@example.com",
        )

    monkeypatch.setattr(
        google_oauth,
        "exchange_authorization_code",
        fake_exchange,
    )
    monkeypatch.setattr(
        google_oauth,
        "verify_google_id_token",
        fake_verify,
    )

    response = await client.get(
        "/auth/google/callback",
        params={
            "code": "authorization-code",
            "state": authorization_params["state"][0],
        },
        headers=cookie_headers(oauth_cookie),
    )

    assert_google_login_redirect(response)
    assert_authentication_cookie_was_issued(response)
    assert_oauth_cookie_was_cleared(response)


async def test_google_callback_returns_existing_local_user(
    client,
    db_session,
    monkeypatch,
):
    user = User(
        username="google-user",
        email="user@example.com",
        hashed_password=None,
    )
    identity = OAuthIdentity(
        user=user,
        provider="google",
        provider_user_id="google-subject-123",
    )
    db_session.add(identity)
    await db_session.flush()

    mock_verified_google_identity(
        monkeypatch,
        email="user@example.com",
        subject="google-subject-123",
    )
    _, authorization_params, oauth_cookie = await start_google_login(client)

    response = await complete_google_callback(
        client,
        oauth_cookie,
        authorization_params["state"][0],
    )

    assert_google_login_redirect(response)
    access_token = assert_authentication_cookie_was_issued(response)
    assert decode_access_token(access_token)["sub"] == str(user.id)
    assert_oauth_cookie_was_cleared(response)


async def test_google_callback_replaces_a_different_authentication_cookie(
    client,
    db_session,
    monkeypatch,
):
    current_user = User(
        username="password-user",
        email="password-user@example.com",
        hashed_password="password-hash",
    )
    google_user = User(
        username="google-user",
        email="google-user@example.com",
        hashed_password=None,
    )
    identity = OAuthIdentity(
        user=google_user,
        provider="google",
        provider_user_id="google-subject-456",
    )
    db_session.add_all([current_user, identity])
    await db_session.flush()

    mock_verified_google_identity(
        monkeypatch,
        email="google-user@example.com",
        subject="google-subject-456",
    )
    _, authorization_params, oauth_cookie = await start_google_login(client)

    response = await complete_google_callback(
        client,
        oauth_cookie,
        authorization_params["state"][0],
        authentication_cookie=create_access_token(current_user.id),
    )

    assert_google_login_redirect(response)
    access_token = assert_authentication_cookie_was_issued(response)
    assert decode_access_token(access_token)["sub"] == str(google_user.id)
    assert_oauth_cookie_was_cleared(response)


async def test_google_callback_creates_new_local_user(
    client,
    db_session,
    monkeypatch,
):
    mock_verified_google_identity(
        monkeypatch,
        email="new-user@example.com",
        subject="new-google-subject",
    )
    _, authorization_params, oauth_cookie = await start_google_login(client)

    response = await complete_google_callback(
        client,
        oauth_cookie,
        authorization_params["state"][0],
    )

    identity = await oauth_identity_crud.get_by_provider_and_provider_user_id(
        session=db_session,
        provider="google",
        provider_user_id="new-google-subject",
    )

    assert_google_login_redirect(response)
    access_token = assert_authentication_cookie_was_issued(response)
    assert identity is not None

    user = await user_crud.get_user_by_id(db_session, identity.user_id)
    assert user is not None
    assert user.email == "new-user@example.com"
    assert user.hashed_password is None
    assert decode_access_token(access_token)["sub"] == str(user.id)
    assert_oauth_cookie_was_cleared(response)


async def test_google_callback_rejects_existing_email_without_linking(
    client,
    db_session,
    monkeypatch,
):
    db_session.add(User(
        username="password-user",
        email="existing@example.com",
        hashed_password="password-hash",
    ))
    await db_session.flush()

    mock_verified_google_identity(
        monkeypatch,
        email="existing@example.com",
        subject="new-google-subject",
    )
    _, authorization_params, oauth_cookie = await start_google_login(client)

    response = await complete_google_callback(
        client,
        oauth_cookie,
        authorization_params["state"][0],
    )

    identity = await oauth_identity_crud.get_by_provider_and_provider_user_id(
        session=db_session,
        provider="google",
        provider_user_id="new-google-subject",
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "A local account already uses this email",
    }
    assert identity is None
    assert_oauth_cookie_was_cleared(response)
    assert_no_authentication_cookie(response)


async def test_google_callback_rolls_back_database_failures(
    client,
    monkeypatch,
):
    mock_verified_google_identity(
        monkeypatch,
        email="user@example.com",
        subject="google-subject-123",
    )

    async def failed_create(*args, **kwargs):
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(
        oauth_identity_crud,
        "create_user_with_identity",
        failed_create,
    )
    _, authorization_params, oauth_cookie = await start_google_login(client)

    response = await complete_google_callback(
        client,
        oauth_cookie,
        authorization_params["state"][0],
    )

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Unable to complete Google authentication",
    }
    assert_oauth_cookie_was_cleared(response)
    assert_no_authentication_cookie(response)


async def test_google_callback_clears_state_cookie_on_lookup_failure(
    client,
    monkeypatch,
):
    mock_verified_google_identity(
        monkeypatch,
        email="user@example.com",
        subject="google-subject-123",
    )

    async def failed_lookup(*args, **kwargs):
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(
        oauth_identity_crud,
        "get_by_provider_and_provider_user_id",
        failed_lookup,
    )
    _, authorization_params, oauth_cookie = await start_google_login(client)

    response = await complete_google_callback(
        client,
        oauth_cookie,
        authorization_params["state"][0],
    )

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Unable to complete Google authentication",
    }
    assert_oauth_cookie_was_cleared(response)
    assert_no_authentication_cookie(response)


async def test_google_callback_rejects_tampered_state_cookie(client):
    _, authorization_params, oauth_cookie = await start_google_login(client)

    response = await client.get(
        "/auth/google/callback",
        params={
            "code": "authorization-code",
            "state": authorization_params["state"][0],
        },
        headers=cookie_headers(oauth_cookie + "tampered"),
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Google authorization request is invalid",
    }
    assert_oauth_cookie_was_cleared(response)
    assert_no_authentication_cookie(response)


async def test_google_callback_rejects_expired_state_cookie(
    client,
    monkeypatch,
):
    _, authorization_params, oauth_cookie = await start_google_login(client)
    monkeypatch.setattr(settings, "GOOGLE_OAUTH_STATE_MAX_AGE_SECONDS", -1)

    response = await client.get(
        "/auth/google/callback",
        params={
            "code": "authorization-code",
            "state": authorization_params["state"][0],
        },
        headers=cookie_headers(oauth_cookie),
    )

    assert response.status_code == 400
    assert_oauth_cookie_was_cleared(response)
    assert_no_authentication_cookie(response)


async def test_google_callback_hides_token_exchange_failure(
    client,
    monkeypatch,
):
    _, authorization_params, oauth_cookie = await start_google_login(client)

    async def failed_exchange(*args, **kwargs):
        raise google_oauth.GoogleTokenExchangeError

    monkeypatch.setattr(
        google_oauth,
        "exchange_authorization_code",
        failed_exchange,
    )

    response = await client.get(
        "/auth/google/callback",
        params={
            "code": "authorization-code",
            "state": authorization_params["state"][0],
        },
        headers=cookie_headers(oauth_cookie),
    )

    assert response.status_code == 502
    assert response.json() == {
        "detail": "Google authentication is temporarily unavailable",
    }
    assert_oauth_cookie_was_cleared(response)
    assert_no_authentication_cookie(response)


async def test_verify_google_id_token_requires_expected_claims(
    monkeypatch,
):
    decode_arguments = {}

    def fake_get_signing_key_from_jwt(id_token: str):
        assert id_token == "mock-id-token"
        return SimpleNamespace(key="mock-public-key")

    def fake_decode(*args, **kwargs):
        decode_arguments.update(kwargs)
        return {
            "aud": "test-client-id",
            "email": "user@example.com",
            "email_verified": True,
            "exp": 4_000_000_000,
            "iss": "https://accounts.google.com",
            "nonce": "expected-nonce",
            "sub": "google-subject-123",
        }

    monkeypatch.setattr(
        google_oauth.google_jwk_client,
        "get_signing_key_from_jwt",
        fake_get_signing_key_from_jwt,
    )
    monkeypatch.setattr(google_oauth.jwt, "decode", fake_decode)
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", "test-client-id")

    identity = await google_oauth.verify_google_id_token(
        id_token="mock-id-token",
        expected_nonce="expected-nonce",
    )

    assert identity == google_oauth.VerifiedGoogleIdentity(
        subject="google-subject-123",
        email="user@example.com",
    )
    assert decode_arguments["algorithms"] == ["RS256"]
    assert decode_arguments["audience"] == "test-client-id"
    assert decode_arguments["issuer"] == google_oauth.GOOGLE_ISSUERS
    assert set(decode_arguments["options"]["require"]) >= {
        "aud",
        "email",
        "email_verified",
        "exp",
        "iss",
        "nonce",
        "sub",
    }
