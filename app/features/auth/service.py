from app.core.security import create_access_token, verify_password
from app.features.auth.repository import AuthRepository
from app.features.auth.schemas.frontend import LoginRequest, LoginResponse, LoginResponseData


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

        return LoginResponse(
            data=LoginResponseData(
                access_token=access_token,
                user_id=user.user_id,
                name=user.name,
                role=user.role,
            )
        )
