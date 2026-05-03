# /Users/cheonjuhwan/Documents/GitHub/Q1_backend/app/main.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.db import Base, engine
from app.core.exceptions import AppException

# 중요: create_all 전에 모델이 import되어 있어야 metadata에 등록됨
# 모델을 app/models 패키지로 둘 경우
import app.models  # noqa: F401

# 만약 feature 내부에 models.py를 둘 경우 아래로 교체
# from app.features.ask_question import models  # noqa: F401


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)


@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
        },
    )


@app.get("/health")
def health_check():
    return {
        "success": True,
        "message": "server is running",
    }


# 라우터 생기면 등록
# from app.features.ask_question.router import router as ask_question_router
# app.include_router(
#     ask_question_router,
#     prefix="/api/v1/ask-question",
#     tags=["Ask Question"],
# )
