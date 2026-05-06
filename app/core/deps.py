# app/core/deps.py

# Generator 타입 힌트
# get_db() 함수가 yield를 사용하기 때문에 Generator로 타입을 표시한다.
from collections.abc import Generator

# SQLAlchemy DB 세션 타입
# router나 service에서 db: Session 형태로 사용할 수 있다.
from sqlalchemy.orm import Session

# db.py에서 만든 SessionLocal 가져오기
# SessionLocal은 요청마다 DB 세션을 만들어주는 세션 생성기다.
from app.core.db import SessionLocal


from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_access_token
from app.models.user import User

#Authorization: Bearer access_token 이 형태의 토큰을 받겠다는 뜻
security = HTTPBearer()

# FastAPI Depends()에서 사용할 DB 세션 의존성 함수
#
# 역할:
# 1. 요청이 들어오면 DB 세션 생성
# 2. API 처리 중 해당 세션 사용
# 3. 요청 처리가 끝나면 세션 종료
def get_db() -> Generator[Session, None, None]:
    # DB 세션 생성
    db = SessionLocal()

    try:
        # router/service/repository에서 사용할 DB 세션 전달
        yield db

    finally:
        # 요청 처리가 끝나면 DB 세션 닫기
        # 세션을 닫지 않으면 연결이 계속 남을 수 있다.
        db.close()


def get_current_user(
    #Authorization 헤더에서 Bearer 토큰을 꺼냄
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    #실제 문자열만 꺼냄
    token = credentials.credentials
    #만들어놓은 액세스 토큰 검증 메소드(sub에서 user_id를 빼낼 수 있음)
    payload = decode_access_token(token)

    #토큰이 만료됐거나, 위조됐거나, access token이 아닐 때
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="액세스 토큰이 올바르지 않습니다.",
        )

    user_id = payload.get("sub")

    #토큰 payload에 user_id(sub)가 없을 때
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="액세스 토큰에 사용자 정보가 없습니다.",
        )

    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    #토큰의 user_id에 해당하는 사용자가 DB에 없을 때
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다.",
        )

    return user