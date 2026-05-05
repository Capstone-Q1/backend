# app/core/config.py

# pydantic-settings에서 제공하는 설정 관리 클래스
# .env 파일에 있는 환경변수를 Python 객체처럼 사용할 수 있게 해준다.
from pydantic_settings import BaseSettings, SettingsConfigDict


# 프로젝트 전체 설정값을 관리하는 클래스
# .env에 있는 APP_NAME, DATABASE_URL 같은 값을 읽어서 저장한다.
class Settings(BaseSettings):
    # FastAPI 앱 이름
    # 나중에 /docs 화면 제목에도 사용할 수 있다.
    app_name: str = "Q1 Backend"

    # 현재 실행 환경
    # local, dev, prod 같은 값으로 구분할 수 있다.
    app_env: str = "local"

    # 디버그 모드 여부
    # True이면 개발 중 로그를 자세히 볼 수 있다.
    debug: bool = True

    # DB 연결 주소
    # SQLite 기준 예시:
    # DATABASE_URL=sqlite:///./q1_backend.db
    #
    # 기본값을 주지 않았기 때문에 .env에 반드시 작성해야 한다.
    database_url: str

    # AI 서버 주소
    # 백엔드에서 AI 서버로 요청 보낼 때 사용한다.
    ai_server_url: str = "http://localhost:8001"

    # AI 서버 응답 대기 시간
    # 30초 안에 응답이 없으면 timeout 처리할 수 있다.
    ai_request_timeout: int = 30

    # solver.log 파일 최대 업로드 크기
    # 나중에 파일 업로드 검증에서 사용한다.
    max_log_file_size_mb: int = 5

    # JWT 서명에 사용할 비밀키
    # 스프링의 jwt.secret 같은 설정값이다.
    jwt_secret_key: str

    # JWT 서명 알고리즘
    jwt_algorithm: str = "HS256"

    # access token 만료 시간(분)
    access_token_expire_minutes: int = 60

    # Settings 클래스가 .env 파일을 읽는 방식 설정
    model_config = SettingsConfigDict(
        # 프로젝트 루트에 있는 .env 파일을 읽는다.
        env_file=".env",

        # .env 파일 인코딩 방식
        env_file_encoding="utf-8",

        # Settings 클래스에 정의되지 않은 환경변수가 .env에 있어도 무시한다.
        # 예: SOME_UNUSED_VALUE=123 같은 값이 있어도 에러 안 남.
        extra="ignore",
    )


# Settings 객체 생성
# 이 시점에 .env 파일을 읽고 settings에 값이 들어간다.
#
# 다른 파일에서는 아래처럼 사용한다.
# from app.core.config import settings
# settings.database_url
settings = Settings()
