from dataclasses import dataclass, field
from typing import Any


# 검증 단계에서 공유되는 요청 컨텍스트.
# 입력 원본(query/file) + validator가 채워 넣는 파생값을 한곳에 모은다.
@dataclass(slots=True)
class ValidationContext:
    query_text: str | None
    filename: str | None
    file_bytes: bytes | None

    # validators가 채워 넣는 값
    solver_log_text: str | None = None
    parsed_meta: dict[str, Any] = field(default_factory=dict)
