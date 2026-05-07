# app/features/ask_question/repository.py
from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.query_response_log import QueryResponseLog
from app.models.solver_result import SolverResult
from app.models.chat_session import ChatSession

def create_query_log(
    db: Session,
    *,
    user_id: str,
    session_id: int,
    query_text: str,
    query_solver_log: str,
) -> QueryResponseLog:
    """
    [역할]
    - 사용자의 질의 시작 시점에 query_response_log 1건을 생성한다.

    [왜 필요?]
    - 이후 AI 호출이 실패해도 최소한 '누가 어떤 질문/로그를 보냈는지' 이력은 남겨야 한다.
    """
    row = QueryResponseLog(
        user_id=user_id,
        session_id=session_id,
        query_text=query_text,
        query_solver_log=query_solver_log,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def find_solver_results_by_log_file_names(
    db: Session,
    *,
    log_file_names: list[str],
) -> list[SolverResult]:
    """
    [역할]
    - AI가 반환한 similar_logs(예: ['003.log','007.log'])를 기준으로
      solver_results에서 상세 데이터를 조회한다.

    [왜 필요?]
    - 프론트 응답의 similar_logs_data를 만들려면 file_name만이 아니라
      각 로그의 파라미터 값들을 DB에서 가져와야 한다.
    """
    if not log_file_names:
        return []

    return (
        db.query(SolverResult)
        .filter(SolverResult.log_file_name.in_(log_file_names))
        .all()
    )


def update_query_response(
    db: Session,
    *,
    log_id: int,
    response_text: str,
    similar_log_files: list[str],
) -> QueryResponseLog:
    """
    [역할]
    - 기존 query_response_log 행에 AI 응답 결과를 반영한다.
      1) response_text
      2) response_case_ids(JSON 문자열)
      3) response_at(응답 시각)

    [왜 필요?]
    - 질의 1건의 요청/응답 이력을 한 행에서 완결해 추적 가능하게 만든다.
    """
    row = (
        db.query(QueryResponseLog)
        .filter(QueryResponseLog.log_id == log_id)
        .first()
    )
    if row is None:
        raise ValueError(f"query_response_log not found: log_id={log_id}")

    row.response_text = response_text
    row.response_case_ids = json.dumps(similar_log_files, ensure_ascii=False)
    row.response_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(row)
    return row

#기존 채팅방에 추가 질문할 때 사용
def find_chat_session_by_id(db: Session, *, session_id: int, user_id: str) -> ChatSession | None:
    return (
        db.query(ChatSession)
        .filter(
            ChatSession.session_id == session_id,
            ChatSession.user_id == user_id,
        )
        .first()
    )

# 사용자의 채팅방 목록 조회
# 사이드바 대화 히스토리에 표시할 채팅방 목록을 마지막 대화 시각 기준 최신순으로 조회한다.
def find_chat_sessions_by_user_id(db: Session, *, user_id: str) -> list[ChatSession]:
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .order_by(
            ChatSession.updated_at.desc(),
            ChatSession.session_id.desc(),
        )
        .all()
    )

#새 채팅방 생성
def create_chat_session(db: Session, *, user_id: str, title: str) -> ChatSession:
    now = datetime.now(timezone.utc)
    row = ChatSession(
        user_id=user_id,
        title=title,
        created_at=now,
        updated_at=now,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

#마지막 채팅 시간 갱신
def update_chat_session_updated_at(db: Session, *, session_id: int) -> None:
    row = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if row is None:
        return
    row.updated_at = datetime.now(timezone.utc)
    db.commit()
