# app/main.py

# FastAPI 앱 생성을 위한 클래스
# Request는 예외 핸들러에서 요청 정보를 받을 때 사용한다.
from fastapi import FastAPI, Request

# JSON 형태로 직접 응답을 만들기 위해 사용한다.
from fastapi.responses import JSONResponse

# config.py에서 만든 settings 가져오기
# 앱 이름, debug 설정 등을 사용한다.
from app.core.config import settings

# exceptions.py에서 만든 프로젝트 공통 예외 가져오기
from app.core.exceptions import AppException


# FastAPI 앱 객체 생성
#
# title:
#   /docs 화면에 표시될 API 이름
#
# debug:
#   개발 중 디버그 모드 여부
app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)


# AppException 계열 예외를 전역에서 처리하는 핸들러
#
# service, repository, processor 등에서 AppException을 raise하면
# 여기서 잡아서 JSON 응답으로 변환한다.
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
        },
    )


# 서버 상태 확인용 API
#
# 브라우저나 Postman에서 서버가 정상 실행 중인지 확인할 때 사용한다.
@app.get("/health")
def health_check():
    return {
        "success": True,
        "message": "server is running",
    }


# 나중에 router가 생기면 여기에 등록한다.
#
# 예:
# from app.features.ask_question.router import router as ask_question_router
# app.include_router(ask_question_router, prefix="/api/v1/ask-question", tags=["Ask Question"])