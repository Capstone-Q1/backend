# /Users/cheonjuhwan/Documents/GitHub/Q1_backend/app/features/ask_question/exceptions.py
from fastapi import status
from app.core.exceptions import AppException

class MissingQuestionException(AppException):
    def __init__(self):
        super().__init__("question is required", status.HTTP_400_BAD_REQUEST, "AQ_001")

class MissingSolverLogException(AppException):
    def __init__(self):
        super().__init__("solver.log is required", status.HTTP_400_BAD_REQUEST, "AQ_002")

class InvalidLogFileExtensionException(AppException):
    def __init__(self):
        super().__init__("only .log is allowed", status.HTTP_400_BAD_REQUEST, "AQ_003")

class FileSizeExceededException(AppException):
    def __init__(self):
        super().__init__("file size exceeded", status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "AQ_004")

class InvalidSolverLogException(AppException):
    def __init__(self, message: str = "invalid solver.log"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, "AQ_005")

class AiRequestFailedException(AppException):
    def __init__(self, message: str = "ai request failed"):
        super().__init__(message, status.HTTP_502_BAD_GATEWAY, "AQ_006")
