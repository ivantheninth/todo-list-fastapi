from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    email: str

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str