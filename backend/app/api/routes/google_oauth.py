import asyncio
import base64
import hashlib
import logging
import secrets
from dataclasses import dataclass
from urllib.parse import urlencode

import httpx
import jwt
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse, Response
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    get_access_token_expiration,
    set_authentication_cookie,
)
from app.crud.oauth_identity import (
    OAuthEmailAlreadyExistsError,
    OAuthIdentityAlreadyExistsError,
    OAuthIdentityCreationConflictError,
    oauth_identity_crud,
)
from app.crud.user import user_crud
from app.db.database import get_db
from app.db.models.oauth_identity import OAuthIdentity
from app.db.models.user import User


GOOGLE_AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"
GOOGLE_ISSUERS = ("https://accounts.google.com", "accounts.google.com")
GOOGLE_OAUTH_COOKIE_NAME = "google_oauth"

logger = logging.getLogger(__name__)


class GoogleTokenExchangeError(Exception):
    pass


class GoogleIDTokenValidationError(Exception):
    pass


@dataclass(frozen=True)
class VerifiedGoogleIdentity:
    subject: str
    email: str


router = APIRouter(
    prefix="/auth/google",
    tags=["auth"],
)

oauth_serializer = URLSafeTimedSerializer(
    secret_key=settings.JWT_SECRET_KEY,
    salt="google-oauth-state",
)

google_jwk_client = jwt.PyJWKClient(
    GOOGLE_JWKS_URL,
    cache_keys=True,
    timeout=settings.GOOGLE_OAUTH_TIMEOUT_SECONDS,
)


def generate_pkce() -> tuple[str, str]:
    code_verifier = secrets.token_urlsafe(32)

    digest = hashlib.sha256(
        code_verifier.encode("ascii")
    ).digest()

    code_challenge = base64.urlsafe_b64encode(
        digest
    ).rstrip(b"=").decode("ascii")

    return code_verifier, code_challenge


def clear_oauth_cookie(response: Response) -> Response:
    response.delete_cookie(
        key=GOOGLE_OAUTH_COOKIE_NAME,
        path="/auth/google",
        secure=settings.GOOGLE_OAUTH_COOKIE_SECURE,
        httponly=True,
        samesite="lax",
    )
    return response


def oauth_error_response(status_code: int, detail: str) -> JSONResponse:
    return clear_oauth_cookie(
        JSONResponse(
            status_code=status_code,
            content={"detail": detail},
        )
    )


def oauth_success_response(user: User) -> RedirectResponse:
    expires_at = get_access_token_expiration()
    access_token = create_access_token(user.id, expires_at)
    response = RedirectResponse(
        url=settings.FRONTEND_ORIGIN,
        status_code=303,
    )
    set_authentication_cookie(response, access_token, expires_at)

    return clear_oauth_cookie(response)


async def exchange_authorization_code(
    code: str,
    code_verifier: str,
) -> str:
    try:
        async with httpx.AsyncClient(
            timeout=settings.GOOGLE_OAUTH_TIMEOUT_SECONDS,
        ) as client:
            response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "code_verifier": code_verifier,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                },
            )
            response.raise_for_status()
            token_data = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise GoogleTokenExchangeError from exc

    if not isinstance(token_data, dict):
        raise GoogleTokenExchangeError

    id_token = token_data.get("id_token")
    if not isinstance(id_token, str) or not id_token:
        raise GoogleTokenExchangeError

    return id_token


async def verify_google_id_token(
    id_token: str,
    expected_nonce: str,
) -> VerifiedGoogleIdentity:
    try:
        signing_key = await asyncio.to_thread(
            google_jwk_client.get_signing_key_from_jwt,
            id_token,
        )
        claims = jwt.decode(
            id_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.GOOGLE_CLIENT_ID,
            issuer=GOOGLE_ISSUERS,
            options={
                "require": [
                    "aud",
                    "email",
                    "email_verified",
                    "exp",
                    "iss",
                    "nonce",
                    "sub",
                ],
            },
        )
    except jwt.PyJWTError as exc:
        raise GoogleIDTokenValidationError from exc

    nonce = claims.get("nonce")
    email = claims.get("email")
    subject = claims.get("sub")

    if (
        not isinstance(nonce, str)
        or not secrets.compare_digest(nonce, expected_nonce)
        or claims.get("email_verified") is not True
        or not isinstance(email, str)
        or not email
        or not isinstance(subject, str)
        or not subject
    ):
        raise GoogleIDTokenValidationError

    return VerifiedGoogleIdentity(
        subject=subject,
        email=email,
    )


async def get_identity_user(
    session: AsyncSession,
    identity: OAuthIdentity,
) -> User | None:
    return await user_crud.get_user_by_id(
        session,
        identity.user_id,
    )


def google_username(email: str) -> str:
    return email.split("@", maxsplit=1)[0]


@router.get("/login")
async def google_login():
    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    code_verifier, code_challenge = generate_pkce()

    oauth_data = oauth_serializer.dumps({
        "state": state,
        "nonce": nonce,
        "code_verifier": code_verifier,
    })

    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "nonce": nonce,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }

    response = RedirectResponse(
        url=GOOGLE_AUTHORIZATION_URL + "?" + urlencode(params),
        status_code=302,
    )

    response.set_cookie(
        key=GOOGLE_OAUTH_COOKIE_NAME,
        value=oauth_data,
        httponly=True,
        secure=settings.GOOGLE_OAUTH_COOKIE_SECURE,
        samesite="lax",
        max_age=settings.GOOGLE_OAUTH_STATE_MAX_AGE_SECONDS,
        path="/auth/google",
    )

    return response


@router.get("/callback")
async def google_callback(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    if request.query_params.get("error"):
        return oauth_error_response(
            status_code=400,
            detail="Google authorization was not completed",
        )

    code = request.query_params.get("code")
    state = request.query_params.get("state")
    oauth_cookie = request.cookies.get(GOOGLE_OAUTH_COOKIE_NAME)

    if not code or not state or not oauth_cookie:
        return oauth_error_response(
            status_code=400,
            detail="Google authorization request is invalid",
        )

    try:
        oauth_data = oauth_serializer.loads(
            oauth_cookie,
            max_age=settings.GOOGLE_OAUTH_STATE_MAX_AGE_SECONDS,
        )
        expected_state = oauth_data["state"]
        code_verifier = oauth_data["code_verifier"]
        nonce = oauth_data["nonce"]
    except (BadSignature, SignatureExpired, KeyError, TypeError):
        return oauth_error_response(
            status_code=400,
            detail="Google authorization request is invalid",
        )

    if (
        not isinstance(expected_state, str)
        or not isinstance(code_verifier, str)
        or not isinstance(nonce, str)
        or not secrets.compare_digest(state, expected_state)
    ):
        return oauth_error_response(
            status_code=400,
            detail="Google authorization request is invalid",
        )

    try:
        id_token = await exchange_authorization_code(
            code=code,
            code_verifier=code_verifier,
        )
    except GoogleTokenExchangeError:
        return oauth_error_response(
            status_code=502,
            detail="Google authentication is temporarily unavailable",
        )

    try:
        verified_identity = await verify_google_id_token(
            id_token=id_token,
            expected_nonce=nonce,
        )
    except GoogleIDTokenValidationError:
        return oauth_error_response(
            status_code=401,
            detail="Google identity could not be verified",
        )

    try:
        existing_identity = (
            await oauth_identity_crud.get_by_provider_and_provider_user_id(
                session=db,
                provider="google",
                provider_user_id=verified_identity.subject,
            )
        )
    except Exception:
        await db.rollback()
        logger.error("Failed to look up Google OAuth identity")
        return oauth_error_response(
            status_code=500,
            detail="Unable to complete Google authentication",
        )

    if existing_identity is not None:
        try:
            local_user = await get_identity_user(db, existing_identity)
        except Exception:
            await db.rollback()
            logger.error("Failed to look up local Google OAuth user")
            return oauth_error_response(
                status_code=500,
                detail="Unable to complete Google authentication",
            )
        if local_user is None:
            logger.error("Google identity references a missing local user")
            return oauth_error_response(
                status_code=500,
                detail="Unable to complete Google authentication",
            )

        return oauth_success_response(local_user)

    try:
        new_identity = await oauth_identity_crud.create_user_with_identity(
            session=db,
            username=google_username(verified_identity.email),
            verified_email=verified_identity.email,
            provider="google",
            verified_provider_user_id=verified_identity.subject,
        )
        await db.commit()
        local_user = await get_identity_user(db, new_identity)
        if local_user is None:
            logger.error("New Google identity references a missing local user")
            return oauth_error_response(
                status_code=500,
                detail="Unable to complete Google authentication",
            )
    except OAuthEmailAlreadyExistsError:
        await db.rollback()
        return oauth_error_response(
            status_code=409,
            detail="A local account already uses this email",
        )
    except (
        OAuthIdentityAlreadyExistsError,
        OAuthIdentityCreationConflictError,
    ):
        await db.rollback()
        try:
            existing_identity = (
                await oauth_identity_crud.get_by_provider_and_provider_user_id(
                    session=db,
                    provider="google",
                    provider_user_id=verified_identity.subject,
                )
            )
            if existing_identity is not None:
                local_user = await get_identity_user(db, existing_identity)
                if local_user is not None:
                    return oauth_success_response(local_user)
        except Exception:
            await db.rollback()
            logger.error("Failed to resolve concurrent Google OAuth identity")
            return oauth_error_response(
                status_code=500,
                detail="Unable to complete Google authentication",
            )

        return oauth_error_response(
            status_code=409,
            detail="A local account already uses this email",
        )
    except Exception:
        await db.rollback()
        logger.error("Failed to persist Google OAuth identity")
        return oauth_error_response(
            status_code=500,
            detail="Unable to complete Google authentication",
        )

    return oauth_success_response(local_user)
