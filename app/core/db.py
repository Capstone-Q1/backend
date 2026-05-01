# app/core/db.py

# SQLAlchemy에서 DB 연결 엔진을 만드는 함수
from sqlalchemy import create_engine

# declarative_base:
#   ORM 모델들이 상속받을 Base 클래스 생성
#
# sessionmaker:
#   DB 세션을 만들어주는 세션 생성기
from sqlalchemy.orm import declarative_base, sessionmaker

# config.py에서 만든 settings 객체 가져오기
# 여기서 settings.database_url 값을 사용해서 DB에 연결한다.
from app.core.config import settings


# DB 연결 엔진 생성
# SQLite 기준으로 .env의 DATABASE_URL 값이 들어간다.
#
# 예:
# DATABASE_URL=sqlite:///./q1_backend.db
#
# 의미:
# sqlite:///        → SQLite 사용
# ./q1_backend.db  → 프로젝트 루트에 q1_backend.db 파일 생성
engine = create_engine(
    # .env에서 읽어온 DB 연결 주소
    settings.database_url,

    # SQLite는 기본적으로 같은 스레드에서만 DB 연결을 사용하려고 한다.
    # 그런데 FastAPI는 요청 처리 중 여러 스레드를 사용할 수 있으므로
    # SQLite + FastAPI 조합에서는 이 옵션을 넣어주는 것이 안전하다.
    connect_args={"check_same_thread": False},

    # True이면 SQLAlchemy가 실행하는 SQL 로그를 터미널에 출력한다.
    # 개발 중에는 True가 편하고, 운영 환경에서는 보통 False로 둔다.
    echo=settings.debug,
)


# DB 세션 생성기
# 실제 DB 세션 객체가 아니라, 요청마다 DB 세션을 만들어주는 공장 역할이다.
SessionLocal = sessionmaker(
    # 자동 커밋 비활성화
    # 데이터 저장/수정/삭제 후 직접 db.commit() 해야 한다.
    autocommit=False,

    # 자동 flush 비활성화
    # DB 반영 타이밍을 개발자가 명확하게 제어하기 위한 설정이다.
    autoflush=False,

    # 위에서 만든 engine에 연결된 세션을 생성한다.
    bind=engine,
)


# SQLAlchemy ORM 모델들이 상속받을 기본 클래스
#
# 나중에 models.py에서 이렇게 사용한다.
#
# class User(Base):
#     __tablename__ = "users"
#
# Base를 상속받은 클래스는 DB 테이블과 매핑된다.
Base = declarative_base()