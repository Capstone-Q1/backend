# app/models/user.py
from sqlalchemy import Column, Text, text
from sqlalchemy.orm import relationship

from app.core.db import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Text, primary_key=True, nullable=False, comment="테이블 고유 id")
    login_id = Column(Text, nullable=False, comment="유저 로그인 id")
    password_hash = Column(Text, nullable=False, comment="유저 비밀번호")
    name = Column(Text, nullable=False, comment="이름")
    role = Column(Text, nullable=False, server_default=text("'USER'"), comment="관리자 권한")
    created_at = Column(Text, nullable=False, comment="계정 생성 시간")

    chat_sessions = relationship("ChatSession", back_populates="user")
    query_response_logs = relationship("QueryResponseLog", back_populates="user")
