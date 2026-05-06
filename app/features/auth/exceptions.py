from fastapi import status

from app.core.exceptions import AppException


class InvalidLoginException(AppException):
    def __init__(self, message: str = "Invalid login credentials."):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
