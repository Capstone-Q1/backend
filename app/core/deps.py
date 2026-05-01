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