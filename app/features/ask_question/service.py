# 질의가 들어오면
# 자연어 질의 저장 + log 파일에서 파라미터 파싱 -> 파싱한 데이터는 query_solver_log에 json 형태로 저장
# 파싱한 데이터는 converToJson으로 변환하여 ai에 전송

# ai에서 응답을 받으면 - 자연어 응답 저장 + 유사 로그 목록 저장
# 유사 로그 목록을 기준으로 solver_result에서 상세 데이터 조회 -> 프론트에 반환

# ask_question 서비스 레이어:
# 1) solver.log 파싱 + 질의 로그 저장
# 2) AI 질의/응답 처리
# 3) 유사 로그 상세 조회 후 프론트 응답 스키마로 변환
import json

from fastapi import UploadFile

from app.core.config import settings
from app.features.ask_question.processors.parsing.ask_query import request_ai_answer
from app.features.ask_question.processors.parsing.parse_log import parse_solver_log_text
from app.features.ask_question.processors.validation import (
    ValidationContext,
    create_ask_question_validation_chain,
)
from app.features.ask_question.processors.utils.convert_to_json import (
    to_ai_request_payload,
    to_frontend_success_payload,
    to_query_solver_log_json,
    parsed_to_similar_log_data,
    row_to_similar_log_data,
)
from app.features.ask_question.exceptions import ChatSessionNotFoundException
from app.features.ask_question.repository import (
    create_query_log,
    create_chat_session,
    update_query_response,
    update_chat_session_updated_at,
    find_chat_session_by_id,
    find_chat_sessions_by_user_id,
    find_query_logs_by_session_id,
    find_query_log_by_id,
    find_solver_results_by_log_file_names,
)
from app.features.ask_question.schemas.frontend import (
    ChatSessionListItem,
    ChatSessionListResponse,
    ChatSessionDetailMessage,
    ChatSessionDetailData,
    ChatSessionDetailResponse,
    AnalysisResponse,
    AnalysisData,
    ChatSessionCreateData,
    ChatSessionCreateResponse,
)

async def ask_question_service(
    db, 
    *, 
    user_id: str, 
    session_id: int | None, 
    query_text: str, 
    parameters: str | None,
    solver_log: UploadFile | None,
) -> dict:
    
    if session_id is None:
        chat_session = create_chat_session(
            db,
            user_id=user_id,
            title=query_text[:30],
        )
        session_id = chat_session.session_id
    else:
        chat_session = find_chat_session_by_id(
            db,
            session_id=session_id,
            user_id=user_id,
        )
        if chat_session is None:
            raise ChatSessionNotFoundException(session_id)

    # parameters는 multipart/form-data에서 JSON 문자열 배열로 전달된다.
    # 값이 없으면 AI에는 빈 리스트를 전달한다.
    selected_parameters = json.loads(parameters) if parameters else []

    # solver_log가 있는 요청만 기존 검증/파싱 체인을 태운다.
    # validation chain 자체는 일단 수정하지 않고 기능이 정상 작동하면 수정한다. (추후 수정 예정)
    parsed = {}
    has_solver_log = solver_log is not None and bool(solver_log.filename)

    if has_solver_log:
        file_bytes = await solver_log.read()

        context = ValidationContext(
            query_text=query_text,
            filename=solver_log.filename,
            file_bytes=file_bytes,
        )

        validation_chain = create_ask_question_validation_chain(
            max_file_size_mb=settings.max_log_file_size_mb
        )
        validation_chain.validate(context)

        parsed = parse_solver_log_text(context.solver_log_text or "")

    # 사용자 질의 + 파싱 결과를 query_log에 먼저 저장해 추적 가능하게 만든다.
    query_log = create_query_log(
        db,
        user_id=user_id,
        session_id=session_id,
        query_text=query_text,
        query_solver_log=to_query_solver_log_json(parsed),
    )

    # AI 요청 포맷으로 변환해 질의하고, 성공/실패 스키마로 응답을 받는다.
    ai_payload = to_ai_request_payload(
        query_text, 
        parsed,
        parameters=selected_parameters,
        include_data=has_solver_log,
    )
    ai_result = await request_ai_answer(ai_payload)                 # 수정 필요

    # AI 실패 시: 실패 메시지를 DB에 남기고 에러 응답을 즉시 반환한다.
    if ai_result.status == "error":
        update_query_response(
            db,
            log_id=query_log.log_id,
            response_text=ai_result.message,
            similar_log_files=[],
        )
        return {
            "status": "error",
            "error_code": ai_result.error_code,
            "error_message": ai_result.message,
        }

    # AI 성공 시: 유사 로그 파일명 목록으로 solver_result 상세 데이터를 조회한다.
    similar_logs = ai_result.data.similar_logs

    # AI 답변과 AI가 찾은 유사 로그 파일명 목록을 DB에 저장한다.
    # response_case_ids에 값이 있으면 나중에 분석 그래프 조회가 가능하다.
    updated_query_log = update_query_response(
        db,
        log_id=query_log.log_id,
        response_text=ai_result.data.chat_response, # 자연어 응답
        similar_log_files=similar_logs, # log 넘버 (000.log) 
    )

    # 채팅방의 마지막 대화 시간을 갱신한다.
    update_chat_session_updated_at(db, session_id=session_id)

    # 최종 프론트 응답 스키마로 직렬화해 반환한다.
    return to_frontend_success_payload(
        session_id=session_id,
        log_id=query_log.log_id,
        chat_response=ai_result.data.chat_response,
        # 채팅방 상세 조회와 같은 기준으로 분석 결과 존재 여부를 내려준다.
        # 프론트는 true일 때 "분석 그래프 보기" 버튼을 표시한다.
        has_analysis=_has_analysis(updated_query_log.response_case_ids),
    )


# 채팅방 목록 조회 서비스 레이어.
# 현재 로그인한 사용자의 채팅방 목록을 조회하고 프론트엔드 응답 스키마로 변환한다.
def get_chat_sessions_service(db, *, user_id: str) -> ChatSessionListResponse:
    rows = find_chat_sessions_by_user_id(db, user_id=user_id)

    return ChatSessionListResponse(
        data=[
            ChatSessionListItem(
                session_id=row.session_id,
                title=row.title,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]
    )


# 채팅방 상세 조회 서비스 레이어.
# 현재 로그인한 사용자가 소유한 채팅방인지 확인한 뒤, 해당 채팅방의 전체 질의응답 내역을 조회한다.
def get_chat_session_detail_service(db, *, user_id: str, session_id: int) -> ChatSessionDetailResponse:
    chat_session = find_chat_session_by_id(
        db,
        session_id=session_id,
        user_id=user_id,
    )

    if chat_session is None:
        raise ChatSessionNotFoundException(session_id)

    logs = find_query_logs_by_session_id(
        db,
        session_id=session_id,
        user_id=user_id,
    )

    return ChatSessionDetailResponse(
        data=ChatSessionDetailData(
            session_id=chat_session.session_id,
            title=chat_session.title,
            created_at=chat_session.created_at,
            messages=[
                ChatSessionDetailMessage(
                    log_id=log.log_id,
                    query_text=log.query_text,
                    chat_response=log.response_text,
                    has_analysis=_has_analysis(log.response_case_ids),
                    created_at=log.created_at,
                    response_at=log.response_at,
                )
                for log in logs
            ],
        )
    )


def get_analysis_data_service(db, *, user_id: str, log_id: int):
    # log_id가 현재 로그인한 사용자의 질의 기록인지 먼저 확인한다.
    # 이렇게 해야 다른 사용자의 분석 데이터를 log_id만으로 조회하는 문제를 막을 수 있다.
    query_log = find_query_log_by_id(
        db,
        log_id=log_id,
        user_id=user_id,
    )

    if query_log is None:
        # log_id 조회 실패 전용 예외로 분리 예정.
        # 지금은 시간상 기존 예외 흐름을 재사용해 요청을 차단한다.
        raise ChatSessionNotFoundException(log_id)

    # query_solver_log에는 사용자가 업로드한 solver.log를 파싱한 결과가 JSON 문자열로 저장되어 있다.
    # 프론트 분석 화면에서는 이 값을 AI가 찾은 유사 로그와 같은 DTO 구조로 비교해야 한다.
    input_log_dict = json.loads(query_log.query_solver_log)

    # response_case_ids에는 AI가 찾은 유사 로그 파일명 목록이 JSON 문자열로 저장되어 있다.
    # 예: ["003.log", "007.log", "045.log"]
    similar_log_file_names = json.loads(query_log.response_case_ids or "[]")

    similar_log_rows = find_solver_results_by_log_file_names(
        db,
        log_file_names=similar_log_file_names,
    )

    # DB 조회 결과는 순서가 보장되지 않을 수 있으므로,
    # AI가 반환한 파일명 순서대로 다시 정렬해서 프론트에 내려준다.
    row_by_file_name = {
        row.log_file_name: row
        for row in similar_log_rows
    }

    ordered_similar_log_rows = [
        row_by_file_name[file_name]
        for file_name in similar_log_file_names
        if file_name in row_by_file_name
    ]

    return AnalysisResponse(
        data=AnalysisData(
            log_id=query_log.log_id,
            input_log_data=parsed_to_similar_log_data(input_log_dict),
            similar_logs_data=[
                row_to_similar_log_data(row)
                for row in ordered_similar_log_rows
            ],
        )
    )


# 분석 그래프 데이터가 있는 질의응답인지 확인한다.
# response_case_ids에 AI가 찾은 유사 로그 목록이 저장되어 있으면 그래프 카드 표시 대상으로 본다.
def _has_analysis(response_case_ids: str | None) -> bool:
    return response_case_ids not in (None, "", "[]")


# 새 채팅방 생성 서비스.
# 이 단계에서는 빈 채팅방만 만들고, 질의 저장/solver.log 파싱/AI 호출은 하지 않는다.
# 실제 채팅방 제목은 첫 질의가 들어왔을 때 query_text를 기준으로 갱신할 예정이다.
def create_chat_session_service(db, *, user_id: str) -> ChatSessionCreateResponse:
    chat_session = create_chat_session(
        db,
        user_id=user_id,
        title="새 채팅",
    )

    return ChatSessionCreateResponse(
        data=ChatSessionCreateData(
            session_id=chat_session.session_id,
        )
    )
