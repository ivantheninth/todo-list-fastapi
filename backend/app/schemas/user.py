from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
)


Username = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=50,
    ),
]


class UserCreate(BaseModel):
    username: Username
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr

    model_config = ConfigDict(
        from_attributes=True,
    )


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str