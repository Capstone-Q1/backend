# app/core/exceptions.py
# 공통 예외 클래스 정의. 공통 예외만 관리, 나머진 각 router나 service에서 직접 정의하는 방식으로 관리한다.

from fastapi import status


class AppException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        self.message = message
        self.status_code = status_code


class InvalidLogFileException(AppException):
    def __init__(self, message: str = "파일 내용이 올바른 solver.log 형식이 아닙니다."):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class FileSizeExceededException(AppException):
    def __init__(self, message: str = "파일 용량을 초과했습니다."):
        super().__init__(
            message=message,
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        )