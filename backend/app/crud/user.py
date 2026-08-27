from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User

from app.core.security import hash_password
from app.mappers.user import user_mapper
from app.schemas.user import UserCreate, UserRead


class UserCrud:

    async def create_user(
        self,
        session: AsyncSession,
        user_data: UserCreate,
    ) -> UserRead:

        user_password = user_data.password

        hashed_user_password = hash_password(user_password)

        user = user_mapper.to_model(user_data, hashed_user_password)

        session.add(user)

        await session.flush()

        return user_mapper.to_read(user)

    async def get_user_by_email(
        self,
        session: AsyncSession,
        email: str,
    ) -> User | None:

        stmt = select(User).where(User.email == email)

        result = await session.execute(stmt)

        user = result.scalar_one_or_none()

        return user


user_crud = UserCrud()
