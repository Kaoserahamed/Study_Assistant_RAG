from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.auth_schema import TokenResponse, UserRegisterRequest, UserResponse
from app.services.auth_service import auth_service


class AuthController:

    async def register(self, request: UserRegisterRequest) -> UserResponse:
        user = await auth_service.register_user(
            email=request.email, password=request.password, name=request.name
        )
        return UserResponse(email=user["email"], name=user["name"])

    async def login(
        self, form_data: OAuth2PasswordRequestForm = Depends()
    ) -> TokenResponse:
        token = await auth_service.authenticate_user(
            email=form_data.username, password=form_data.password
        )
        return TokenResponse(access_token=token, token_type="bearer")

    async def get_me(self, current_user: dict) -> UserResponse:
        return UserResponse(email=current_user["email"], name=current_user["name"])


auth_controller = AuthController()