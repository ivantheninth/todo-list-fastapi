import jwt

from fastapi import Depends, HTTPException, Request
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import decode_access_token
from app.crud.user import user_crud
from app.db.database import get_db
from app.db.models.user import User


security = HTTPBearer(auto_error=False)


def invalid_credentials() -> HTTPException:
    return HTTPException(
        status_code=401,
        detail="Could not validate credentials",
    )


def get_user_id_from_token(token: str) -> int:
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if user_id is None:
            raise invalid_credentials()

        return int(user_id)
    except (jwt.InvalidTokenError, ValueError):
        raise invalid_credentials()


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> User:
    bearer_token = credentials.credentials if credentials else None
    cookie_token = request.cookies.get(settings.AUTH_COOKIE_NAME)

    if request.headers.get("Authorization") and bearer_token is None:
        raise invalid_credentials()

    if bearer_token is None and cookie_token is None:
        raise invalid_credentials()

    bearer_user_id = (
        get_user_id_from_token(bearer_token)
        if bearer_token is not None
        else None
    )
    cookie_user_id = (
        get_user_id_from_token(cookie_token)
        if cookie_token is not None
        else None
    )

    if (
        bearer_user_id is not None
        and cookie_user_id is not None
        and bearer_user_id != cookie_user_id
    ):
        raise invalid_credentials()

    user_id = bearer_user_id or cookie_user_id

    user = await user_crud.get_user_by_id(
        db,
        user_id,
    )

    if user is None:
        raise invalid_credentials()

    return user
