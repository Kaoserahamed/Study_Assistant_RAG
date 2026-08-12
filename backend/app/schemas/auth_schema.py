from pydantic import BaseModel, EmailStr


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class UserResponse(BaseModel):
    email: EmailStr
    name: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str