# app/auth.py
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from app.services.auth_service import auth_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    return await auth_service.get_user_from_token(token)
