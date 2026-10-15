import pytest

from app.crud.oauth_identity import (
    OAuthEmailAlreadyExistsError,
    OAuthIdentityAlreadyExistsError,
    oauth_identity_crud,
)
from app.crud.user import user_crud
from app.db.models.oauth_identity import OAuthIdentity
from app.db.models.user import User


async def test_get_by_provider_and_provider_user_id_returns_identity(
    db_session,
):
    user = User(
        username="google-user",
        email="google-user@example.com",
        hashed_password=None,
    )
    identity = OAuthIdentity(
        user=user,
        provider="google",
        provider_user_id="google-subject-123",
    )
    db_session.add(identity)
    await db_session.flush()

    result = await oauth_identity_crud.get_by_provider_and_provider_user_id(
        session=db_session,
        provider="google",
        provider_user_id="google-subject-123",
    )

    assert result is identity
    assert result.user_id == user.id


async def test_get_by_provider_and_provider_user_id_returns_none_when_missing(
    db_session,
):
    result = await oauth_identity_crud.get_by_provider_and_provider_user_id(
        session=db_session,
        provider="google",
        provider_user_id="missing-google-subject",
    )

    assert result is None


async def test_create_user_with_identity_creates_google_only_account(
    db_session,
):
    identity = await oauth_identity_crud.create_user_with_identity(
        session=db_session,
        username="google-user",
        verified_email="google-user@example.com",
        provider="google",
        verified_provider_user_id="google-subject-123",
    )

    assert identity.provider == "google"
    assert identity.provider_user_id == "google-subject-123"
    assert identity.user.email == "google-user@example.com"
    assert identity.user.hashed_password is None


async def test_create_user_with_identity_rejects_existing_email(
    db_session,
):
    existing_user = User(
        username="password-user",
        email="existing@example.com",
        hashed_password="existing-password-hash",
    )
    db_session.add(existing_user)
    await db_session.flush()

    with pytest.raises(OAuthEmailAlreadyExistsError):
        await oauth_identity_crud.create_user_with_identity(
            session=db_session,
            username="google-user",
            verified_email="existing@example.com",
            provider="google",
            verified_provider_user_id="google-subject-123",
        )

    assert await user_exists(db_session, "existing@example.com")


async def test_create_user_with_identity_rejects_duplicate_google_identity(
    db_session,
):
    existing_user = User(
        username="google-user",
        email="google-user@example.com",
        hashed_password=None,
    )
    existing_identity = OAuthIdentity(
        user=existing_user,
        provider="google",
        provider_user_id="google-subject-123",
    )
    db_session.add(existing_identity)
    await db_session.flush()

    with pytest.raises(OAuthIdentityAlreadyExistsError):
        await oauth_identity_crud.create_user_with_identity(
            session=db_session,
            username="another-google-user",
            verified_email="another-google-user@example.com",
            provider="google",
            verified_provider_user_id="google-subject-123",
        )

    assert not await user_exists(
        db_session,
        "another-google-user@example.com",
    )


async def user_exists(db_session, email: str) -> bool:
    user = await user_crud.get_user_by_email(
        db_session,
        email,
    )

    return user is not None
