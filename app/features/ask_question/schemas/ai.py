from typing import Any, Literal


from pydantic import BaseModel, ConfigDict, Field, TypeAdapter


# 역할: AI 서버로 전달할 공정 로그 입력값 스키마.
# 사용 시점: ask_question에서 AI 질의를 만들 때 입력 데이터 검증에 사용.
class AiRequestData(BaseModel):
    # 내부 상세 키는 convert_to_json에서 만들어주므로 dict로 받는다.
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    settings: dict[str, Any] = Field(alias="SETTINGS")
    output_list: dict[str, Any] = Field(alias="OUTPUT LIST")



# 역할: AI 질의 요청 본문 스키마(query_text + data).
# 사용 시점: 내부에서 AI 엔드포인트 호출 payload를 구성/검증할 때 사용.
class AiQuestionRequest(BaseModel):
    query_text: str = Field(min_length=1)
    data: AiRequestData


# 역할: AI 성공 응답의 data 본문 스키마.
# 사용 시점: AI가 정상 응답했을 때 답변/유사 로그 목록을 담아 파싱할 때 사용.
class AiSuccessData(BaseModel):
    chat_response: str
    similar_logs: list[str]


# 역할: AI 성공 응답의 최상위 스키마.
# 사용 시점: AI 응답 status가 success인 경우 전체 구조 검증에 사용.
class AiSuccessResponse(BaseModel):
    status: Literal["success"]
    data: AiSuccessData


# 역할: AI 실패 응답의 최상위 스키마.
# 사용 시점: AI 응답 status가 error인 경우 에러 정보 파싱에 사용.
class AiErrorResponse(BaseModel):
    status: Literal["error"]
    error_code: str
    message: str


# 역할: AI 응답 유니온 타입(성공/실패 공통 표현).
# 사용 시점: AI 응답을 단일 타입으로 다루기 위한 반환 타입 정의에 사용.
AiQuestionResponse = AiSuccessResponse | AiErrorResponse

# 역할: 유니온 응답 파싱 어댑터.
# 사용 시점: dict payload를 성공/실패 스키마 중 올바른 타입으로 검증 변환할 때 사용.
ai_response_adapter = TypeAdapter(AiQuestionResponse)


# 역할: AI 원본 payload를 타입 안전한 응답 객체로 변환하는 헬퍼.
# 사용 시점: AI 호출 직후 dict 응답을 스키마 기반으로 검증/파싱할 때 사용.
def parse_ai_response(payload: dict) -> AiQuestionResponse:
    return ai_response_adapter.validate_python(payload)
