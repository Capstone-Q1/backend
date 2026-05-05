from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from jwt import InvalidTokenError
from passlib.context import CryptContext

from app.core.config import settings


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return password_context.verify(plain_password, password_hash)

#로그인 성공 시 액세스 토큰 생성
def create_access_token(
    *,
    user_id: str,
    login_id: str,
    role: str,
) -> str:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(
        minutes=settings.access_token_expire_minutes,
    )

    payload: dict[str, Any] = {
        "sub": user_id,
        "login_id": login_id,
        "role": role,
        "type": "access",
        "iat": now,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

#로그인 성공 시 리프레쉬 토큰 생성
def create_refresh_token(
    *,
    user_id: str,
) -> str:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(
        days=settings.refresh_token_expire_days,
    )

    payload: dict[str, Any] = {
        "sub": user_id,
        "type": "refresh",
        "iat": now,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

#액세스 토큰 검증, 유효하면 payload 반환하고 나중에 sub에서 user_id를 얻을 수 있음
#이때 sub은 이 API 요청을 보낸 사용자가 누구인지 확인할 때 사용
def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except InvalidTokenError:
        return None

    if payload.get("type") != "access":
        return None

    return payload

#리프레쉬 토큰 검증, 유효하면 payload를 반환하고 sub에서 user_id를 꺼냄
#이때 sub은 새 액세스 토큰을 누구 이름으로 만들어줄지 확인할 때 사용
def decode_refresh_token(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except InvalidTokenError:
        return None

    if payload.get("type") != "refresh":
        return None

    return payload