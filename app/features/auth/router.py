from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.features.auth.repository import AuthRepository
from app.features.auth.schemas.frontend import LoginRequest, LoginResponse, RefreshTokenRequest, RefreshTokenResponse, MeResponse, MeResponseData
from app.features.auth.service import AuthService
from app.core.deps import get_db, get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    repository = AuthRepository(db)
    service = AuthService(repository)

    response = service.login(request)

    if response is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 올바르지 않습니다.",
        )

    return response

@router.post("/refresh", response_model=RefreshTokenResponse)
def refresh_access_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    repository = AuthRepository(db)
    service = AuthService(repository)

    response = service.refresh_access_token(request)

    if response is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="리프레시 토큰이 올바르지 않습니다.",
        )

    return response


@router.get("/me", response_model=MeResponse)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return MeResponse(
        data=MeResponseData(
            user_id=current_user.user_id,
            login_id=current_user.login_id,
            name=current_user.name,
            role=current_user.role,
        )
    )
