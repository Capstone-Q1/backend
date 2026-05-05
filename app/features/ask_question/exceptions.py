from fastapi import status
from app.core.exceptions import AppException

class MissingQuestionException(AppException):
    def __init__(self):
        super().__init__(
            message="question is required",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="AQ_001",
        )

class InvalidSolverLogException(AppException):
    def __init__(self):
        super().__init__(
            message="invalid solver.log",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="AQ_002",
        )

class AiRequestFailedException(AppException):
    def __init__(self):
        super().__init__(
            message="ai request failed",
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code="AQ_003",
        )


class AppException(Exception):
    def __init__(self, message: str, status_code: int, error_code: str = "APP_000"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code