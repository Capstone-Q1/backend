# app/core/exceptions.py
# 공통 예외 클래스 정의. 공통 예외만 관리, 나머진 각 router나 service에서 직접 정의하는 방식으로 관리한다.

from fastapi import status

class AppException(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST, error_code: str = "APP_000"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
