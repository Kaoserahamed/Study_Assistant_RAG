from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=255)


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
