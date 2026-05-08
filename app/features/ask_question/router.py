# ask_question 라우터:
# HTTP 입력(Form/File)을 받아 서비스 레이어로 전달하는 진입점.
from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.features.ask_question.service import ask_question_service, get_chat_sessions_service, get_chat_session_detail_service
from app.features.ask_question.schemas.frontend import ChatSessionListResponse, ChatSessionDetailResponse
from app.models.user import User

router = APIRouter()


@router.post("/search")
async def ask_question(
    # 사용자/세션/질의는 multipart form-data로 받는다.
    current_user: User = Depends(get_current_user),
    #기존 채팅방이면 프론트가 보내고, 새 채팅방이면 안 보낼 수 있게 optional로 둠.
    session_id: int | None = Form(default=None),
    query_text: str = Form(...),
    # solver.log 원본 파일 업로드.
    solver_log: UploadFile = File(...),
    # 요청 단위 DB 세션 주입.
    db: Session = Depends(get_db),
):
    
    return await ask_question_service(
        db,
        user_id=current_user.user_id,
        session_id=session_id,
        query_text=query_text,
        solver_log=solver_log,
    )

# 채팅방 목록 조회 API.
# Authorization 헤더의 Bearer 토큰에서 현재 사용자를 확인하고,
# 해당 사용자의 채팅방 목록을 마지막 대화 시각 기준 최신순으로 반환한다.
@router.get("/sessions", response_model=ChatSessionListResponse)
def get_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_chat_sessions_service(
        db,
        user_id=current_user.user_id,
    )

# 채팅방 상세 조회 API.
# Authorization 헤더의 Bearer 토큰에서 현재 사용자를 확인하고,
# 해당 사용자가 소유한 채팅방의 전체 질의응답 내역을 시간순으로 반환한다.
@router.get("/session/{session_id}", response_model=ChatSessionDetailResponse)
def get_chat_session_detail(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_chat_session_detail_service(
        db,
        user_id=current_user.user_id,
        session_id=session_id,
    )
