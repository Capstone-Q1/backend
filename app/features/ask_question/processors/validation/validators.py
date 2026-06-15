from __future__ import annotations

from abc import ABC, abstractmethod

from app.features.ask_question.exceptions import (
    FileSizeExceededException,
    InvalidLogFileExtensionException,
    InvalidSolverLogException,
    MissingQuestionException,
    MissingSolverLogException,
)
from app.features.ask_question.processors.validation.validation_context import ValidationContext


# 모든 validator의 공통 인터페이스.
# 실패 시 도메인 예외를 발생시키고, 성공 시 context를 필요하면 갱신한다.
class Validator(ABC):
    @abstractmethod
    def validate(self, context: ValidationContext) -> None:
        pass


# query_text 필수 검증.
class QuestionRequiredValidator(Validator):
    def validate(self, context: ValidationContext) -> None:
        if context.query_text is None or not context.query_text.strip():
            raise MissingQuestionException()


# solver.log 파일 존재 검증.
class SolverLogRequiredValidator(Validator):
    def validate(self, context: ValidationContext) -> None:
        if context.file_bytes is None or len(context.file_bytes) == 0:
            raise MissingSolverLogException()


# 파일 확장자 검증(.log 기본).
class LogFileExtensionValidator(Validator):
    def __init__(self, allowed_ext: str = ".log") -> None:
        self.allowed_ext = allowed_ext.lower()

    def validate(self, context: ValidationContext) -> None:
        filename = (context.filename or "").lower()
        if not filename.endswith(self.allowed_ext):
            raise InvalidLogFileExtensionException()


# 업로드 크기 제한 검증(기본 5MB).
class FileSizeValidator(Validator):
    def __init__(self, max_size_mb: int = 5) -> None:
        self.max_size_bytes = max_size_mb * 1024 * 1024

    def validate(self, context: ValidationContext) -> None:
        if context.file_bytes is None:
            return
        if len(context.file_bytes) > self.max_size_bytes:
            raise FileSizeExceededException()


# 인코딩 검증 + bytes -> 텍스트 디코딩.
# 성공 시 이후 validator가 쓰도록 solver_log_text를 context에 저장한다.
class EncodingValidator(Validator):
    def __init__(self, encoding: str = "utf-8") -> None:
        self.encoding = encoding

    def validate(self, context: ValidationContext) -> None:
        if context.file_bytes is None:
            return
        try:
            context.solver_log_text = context.file_bytes.decode(self.encoding)
        except UnicodeDecodeError as exc:
            raise InvalidSolverLogException("solver.log must be utf-8 text") from exc


# 로그 본문에 필수 섹션 키워드가 있는지 검증.
class SolverLogFormatValidator(Validator):
    def __init__(self, required_keywords: list[str] | None = None) -> None:
        self.required_keywords = required_keywords or [
            "SIMULATION OPTIONS",
            "CHAMBER GEOMETRY",
            "SOURCE POWER CONDITIONS",
        ]

    def validate(self, context: ValidationContext) -> None:
        text = context.solver_log_text or ""
        for keyword in self.required_keywords:
            if keyword not in text:
                raise InvalidSolverLogException(
                    f"required section not found: {keyword}"
                )


# 로그 본문에 필수 파라미터 문자열이 있는지 검증.
class RequiredParameterValidator(Validator):
    def __init__(self, required_params: list[str] | None = None) -> None:
        self.required_params = required_params or [
            "PowerH",
            "Pressure",
            "Electron Temp.",
        ]

    def validate(self, context: ValidationContext) -> None:
        text = context.solver_log_text or ""
        for param in self.required_params:
            if param not in text:
                raise InvalidSolverLogException(
                    f"required parameter not found: {param}"
                )
