# /Users/cheonjuhwan/Documents/GitHub/Q1_backend/app/main.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.db import Base, engine
from app.core.exceptions import AppException
from app.features.auth.router import router as auth_router
from app.features.ask_question.router import router as ask_question_router

# 중요: create_all 전에 모델이 import되어 있어야 metadata에 등록됨
from app.models import *  # noqa: F401


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

# 프론트 주소를 명시적으로 허용
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # 쿠키 인증이면 True로 변경
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error_code": exc.error_code,
            "error_message": exc.message,
        },
    )


@app.get("/health")
def health_check():
    return {
        "success": True,
        "message": "server is running",
    }


app.include_router(
    ask_question_router,
    prefix="/api/v1/ask-question",
    tags=["Ask Question"],
)

app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Auth"],
)
