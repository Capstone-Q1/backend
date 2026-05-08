from fastapi import UploadFile, File


import httpx
from app.core.config import settings
from app.features.ask_question.processors.parsing.parse_log import parse_solver_log_text
from app.features.ask_question.exceptions import AiRequestFailedException
from app.features.ask_question.schemas.ai import AiQuestionResponse, parse_ai_response


# AI 서버 `/api/v1/search` 엔드포인트를 비동기로 호출해 응답 스키마로 파싱한다.
# HTTP 실패(4xx/5xx) 또는 네트워크 예외가 나면 AiRequestFailedException으로 래핑한다.
# OOD 데이터는 422로 오기 때문에 200,422는 정상 응답으로 처리
async def request_ai_answer(payload: dict) -> AiQuestionResponse: 
    try:        
        # timeout은 설정값을 사용해 요청 지연을 제한한다.
        async with httpx.AsyncClient(timeout=settings.ai_request_timeout) as client:
            resp = await client.post(
                # Ai 서버에 payload를 JSON body로 전송한다.
                f"{settings.ai_server_url}/api/v1/search",  # endpoint도 스펙에 맞춤
                json=payload,
            )
    except httpx.RequestError as e:
        # 요청 전송/수신 과정의 통신 예외 (서버가 4xx/5xx를 정상 응답한 경우는 여기 대상이 아님)
        raise AiRequestFailedException(f"AI network error: {e}") from e

    # AI 비즈니스 실패(422)도 정상 파싱 경로로 보낸다.
    if resp.status_code in (200, 422):
        try:
            return parse_ai_response(resp.json())
        except Exception as e:
            #응답은 받았는데, 응답 본문을 우리 스키마로 해석하지 못한 경우 -> 커스텀 예외 통일이 아니라 각각 만들어줘야함
            raise AiRequestFailedException(
                f"AI response parse error (status={resp.status_code})"
            ) from e

    # 그 외 HTTP 오류는 게이트웨이 실패로 처리 
    # 4xx/5xx HTTP 응답 중 422 제외
    raise AiRequestFailedException(
        f"AI request failed: status={resp.status_code}, body={resp.text}"
    )



async def log_parsing(solver_log: UploadFile ): #파일에서 파라미터 파싱할 때만 사용
    raw_bytes = await solver_log.read()      # 파일 원본
    text = raw_bytes.decode("utf-8")         # 문자열 변환
    parsed = parse_solver_log_text(text)     # 네 파서 호출
    return parsed
