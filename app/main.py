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

# 프론트 Origin 허용 (현재 구조: localhost:3000 + Authorization 헤더)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=False,  # 쿠키 미사용 구조
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
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
