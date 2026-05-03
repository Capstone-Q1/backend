# app/models/chat_session.py
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.core.db import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    session_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, comment="채팅방 PK")
    user_id = Column(Text, ForeignKey("users.user_id"), nullable=False, comment="테이블 고유 id")
    title = Column(Text, nullable=False, comment="채팅방 제목")
    created_at = Column(DateTime, nullable=False, comment="채팅방 생성 시각")
    updated_at = Column(DateTime, nullable=False, comment="마지막 대화 시각")

    user = relationship("User", back_populates="chat_sessions")
    query_response_logs = relationship("QueryResponseLog", back_populates="chat_session")
