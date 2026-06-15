from __future__ import annotations

from app.features.ask_question.processors.validation.validation_context import ValidationContext
from app.features.ask_question.processors.validation.validators import (
    EncodingValidator,
    FileSizeValidator,
    LogFileExtensionValidator,
    QuestionRequiredValidator,
    RequiredParameterValidator,
    SolverLogFormatValidator,
    SolverLogRequiredValidator,
    Validator,
)


class ValidationChain:
    def __init__(self, validators: list[Validator]) -> None:
        self.validators = validators

    def validate(self, context: ValidationContext) -> None:
        for validator in self.validators:
            validator.validate(context)


def create_ask_question_validation_chain(max_file_size_mb: int = 5) -> ValidationChain:
    return ValidationChain(
        validators=[
            QuestionRequiredValidator(),
            SolverLogRequiredValidator(),
            LogFileExtensionValidator(".log"),
            FileSizeValidator(max_file_size_mb),
            EncodingValidator("utf-8"),
            SolverLogFormatValidator(),
            RequiredParameterValidator(),
        ]
    )
