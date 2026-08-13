from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.controllers.auth_controller import auth_controller
from app.schemas.auth_schema import TokenResponse, UserRegisterRequest, UserResponse
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# Dependency helper for protected routes
async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    return await auth_service.get_user_from_token(token)


@router.post("/register", response_model=UserResponse)
async def register(user_request: UserRegisterRequest):
    return await auth_controller.register(user_request)


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return await auth_controller.login(form_data)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return await auth_controller.get_me(current_user)