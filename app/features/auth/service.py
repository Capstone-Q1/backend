from app.core.security import create_access_token, create_refresh_token, decode_refresh_token, hash_token, verify_password, verify_token
from app.features.auth.repository import AuthRepository
from app.features.auth.schemas.frontend import LoginRequest, LoginResponse, LoginResponseData, RefreshTokenResponseData, RefreshTokenRequest, RefreshTokenResponse


class AuthService:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    def login(self, request: LoginRequest) -> LoginResponse | None:
        user = self.repository.find_by_login_id(request.login_id)

        if user is None:
            return None

        if not verify_password(request.password, user.password_hash):
            return None

        access_token = create_access_token(
            user_id=user.user_id,
            login_id=user.login_id,
            role=user.role,
        )

        refresh_token = create_refresh_token(
            user_id=user.user_id,
        )

        self.repository.update_refresh_token_hash(
            user_id=user.user_id,
            refresh_token_hash=hash_token(refresh_token),
        )

        return LoginResponse(
            data=LoginResponseData(
                access_token=access_token,
                refresh_token=refresh_token,
                user_id=user.user_id,
                name=user.name,
                role=user.role,
            )
        )
    
    def refresh_access_token(
        self,
        request: RefreshTokenRequest,
    ) -> RefreshTokenResponse | None:
        payload = decode_refresh_token(request.refresh_token)

        if payload is None:
            return None

        user_id = payload.get("sub")

        if user_id is None:
            return None

        user = self.repository.find_by_user_id(user_id)

        if user is None:
            return None

        if not verify_token(request.refresh_token, user.refresh_token_hash):
            return None

        access_token = create_access_token(
            user_id=user.user_id,
            login_id=user.login_id,
            role=user.role,
        )

        return RefreshTokenResponse(
            data=RefreshTokenResponseData(
                access_token=access_token,
            )
        )
    
    def logout(self, user_id: str) -> None:
        self.repository.clear_refresh_token_hash(user_id)



    
