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
    def __init__(self, message: str = "ai request failed", error_code: str = "AQ_006"):
        super().__init__(message, status.HTTP_502_BAD_GATEWAY, error_code)

class ChatSessionNotFoundException(AppException):
    def __init__(self, session_id: int):
        super().__init__(
            f"chat_session not found: session_id={session_id}",
            status.HTTP_404_NOT_FOUND,
            "AQ_007",
        )

class DuplicateRequestException(AppException):
    def __init__(self):
        super().__init__(
            "duplicate request detected",
            status.HTTP_409_CONFLICT,
            "AQ_008",
        )

class SimilarLogNotFoundException(AppException):
    def __init__(self, missing_log_files: list[str]):
        super().__init__(
            f"similar log data not found: {missing_log_files}",
            status.HTTP_404_NOT_FOUND,
            "AQ_009",
        )

class DatabaseOperationException(AppException):
    def __init__(self, message: str = "database operation failed"):
        super().__init__(
            message,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "AQ_010",
        )

class UploadInterruptedException(AppException):
    def __init__(self):
        super().__init__(
            "client disconnected during upload",
            status.HTTP_400_BAD_REQUEST,
            "AQ_011",
        )
