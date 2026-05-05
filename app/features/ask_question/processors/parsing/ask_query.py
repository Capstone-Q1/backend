from fastapi import UploadFile, File


import httpx
from app.core.config import settings
from app.features.ask_question.processors.parsing.parse_log import parse_solver_log_text
from app.features.ask_question.exceptions import AiRequestFailedException
from app.features.ask_question.schemas.ai import AiQuestionResponse, parse_ai_response


# AI 서버 `/ask` 엔드포인트를 비동기로 호출해 응답 스키마로 파싱한다.
# - HTTP 실패(4xx/5xx) 또는 네트워크 예외가 나면 AiRequestFailedException으로 래핑한다.
async def request_ai_answer(payload: dict) -> AiQuestionResponse: 
    # ai 서버는 langchain으로 구축되어 있어서 httpx로 직접 호출하는 게 아니라 langchain client로 호출해야 함. 
    # 암튼 이거 못씀
    try:
        # timeout은 설정값을 사용해 요청 지연을 제한한다.
        async with httpx.AsyncClient(timeout=settings.ai_request_timeout) as client:
            # payload를 JSON body로 전송한다.
            resp = await client.post(f"{settings.ai_server_url}/ask", json=payload)
            # 2xx가 아니면 예외 발생.
            resp.raise_for_status()
            # 응답 JSON을 성공/실패 유니온 스키마로 검증 파싱한다.
            return parse_ai_response(resp.json())
    except Exception as e:
        # 호출 계층에서는 단일 도메인 예외로 처리할 수 있게 변환한다.
        raise AiRequestFailedException(str(e))



async def log_parsing(solver_log: UploadFile = File(...)): #파일에서 파라미터 파싱할 때만 사용
    raw_bytes = await solver_log.read()      # 파일 원본
    text = raw_bytes.decode("utf-8")         # 문자열 변환
    parsed = parse_solver_log_text(text)     # 네 파서 호출
    return parsed
