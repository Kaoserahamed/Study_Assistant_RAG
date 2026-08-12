from datetime import datetime, timedelta, timezone
from typing import Optional
import os
from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
from app.repositories.user_repository import user_repository

# Load environment variables
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-keep-it-secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    async def register_user(self, email: str, password: str, name: str) -> dict:
        existing_user = await user_repository.get_by_email(email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_pw = self.hash_password(password)
        return await user_repository.create_user(email, name, hashed_pw)

    async def authenticate_user(self, email: str, password: str) -> str:
        user = await user_repository.get_by_email(email)
        if not user or not self.verify_password(password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        return self.create_access_token(data={"sub": user["email"]})

    async def get_user_from_token(self, token: str) -> dict:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = await user_repository.get_by_email(email)
        if user is None:
            raise credentials_exception
        return user


auth_service = AuthService()