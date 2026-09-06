from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.core.security import verify_password, create_access_token
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

    if not verify_password(
        user_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",  # nosec B105
    }


@router.get(
    "/me",
    response_model=UserRead,
)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user