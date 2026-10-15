from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.core.config import settings
from app.core.security import (
    create_access_token,
    get_access_token_expiration,
    set_authentication_cookie,
    verify_password,
)
from app.crud.user import user_crud
from app.db.database import get_db
from app.db.models.user import User
from app.schemas.user import UserCreate, UserRead, UserLogin, TokenResponse


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/register",
    response_model=UserRead,
    status_code=201,
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    existing_user = await user_crud.get_user_by_email(
        db,
        user_data.email,
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

    try:
        user = await user_crud.create_user(
            db,
            user_data,
        )

        await db.commit()

        return user

    except Exception:
        await db.rollback()
        raise


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    user_data: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    user = await user_crud.get_user_by_email(
        db,
        user_data.email,
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
        )

    if user.hashed_password is None or not verify_password(
        user_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
        )

    expires_at = get_access_token_expiration()
    access_token = create_access_token(user.id, expires_at)
    set_authentication_cookie(response, access_token, expires_at)

    return {
        "access_token": access_token,
        "token_type": "bearer",  # nosec B105
    }


@router.post(
    "/logout",
    status_code=204,
)
async def logout(response: Response):
    response.delete_cookie(
        key=settings.AUTH_COOKIE_NAME,
        path=settings.AUTH_COOKIE_PATH,
        secure=settings.AUTH_COOKIE_SECURE,
        httponly=settings.AUTH_COOKIE_HTTPONLY,
        samesite=settings.AUTH_COOKIE_SAMESITE,
    )


@router.get(
    "/me",
    response_model=UserRead,
)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user
