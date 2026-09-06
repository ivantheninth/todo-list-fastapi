from app.db.models.user import User
from app.schemas.user import (
    UserCreate,
    UserRead,
)


class UserMapper:

    def to_model(
        self,
        user_data: UserCreate,
        hashed_password: str,
    ) -> User:
        return User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
        )

    def to_read(self, user: User) -> UserRead:
        return UserRead.model_validate(user)


user_mapper = UserMapper()