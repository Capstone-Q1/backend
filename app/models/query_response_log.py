# app/models/query_response_log.py
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, text
from sqlalchemy.orm import relationship

from app.core.db import Base


class QueryResponseLog(Base):
    __tablename__ = "query_response_log"

    log_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment="질의응답 로그 PK")
    user_id = Column(Text, ForeignKey("users.user_id"), nullable=False, comment="테이블 고유 id")
    session_id = Column(Integer, ForeignKey("chat_sessions.session_id"), nullable=False, comment="채팅방 PK")
    query_text = Column(Text, nullable=False, comment="사용자 자연어 질문")
    query_solver_log = Column(Text, nullable=False, comment="업로드된 solver.log 원본")
    query_parameters = Column(Text, nullable=True, comment="사용자가 선택한 파라미터 목록")
    response_text = Column(Text, nullable=True, comment="AI 자연어 응답")
    response_case_ids = Column(Text, nullable=True, comment="AI가 반환한 케이스 ID 목록")
    important_parameters = Column(Text, nullable=True, comment="AI가 판단한 중요 파라미터 목록")
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment="질의 시각")
    response_at = Column(DateTime, nullable=True, comment="AI 응답 시각")

    user = relationship("User", back_populates="query_response_logs")
    chat_session = relationship("ChatSession", back_populates="query_response_logs")
