# ask_question 라우터:
# HTTP 입력(Form/File)을 받아 서비스 레이어로 전달하는 진입점.
from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.features.ask_question.service import ask_question_service, get_chat_sessions_service, get_chat_session_detail_service, get_analysis_data_service
from app.features.ask_question.schemas.frontend import ChatSessionListResponse, ChatSessionDetailResponse, AnalysisResponse, AskQuestionResponse
from app.models.user import User

router = APIRouter()


@router.post("/search", response_model=AskQuestionResponse)
async def ask_question(
    # 사용자/세션/질의는 multipart form-data로 받는다.
    current_user: User = Depends(get_current_user),
    #기존 채팅방이면 프론트가 보내고, 새 채팅방이면 안 보낼 수 있게 optional로 둠.
    session_id: int | None = Form(default=None),
    query_text: str = Form(...),
    # parameters는 선택 입력이다. JSON 문자열 배열로 받으며, 없으면 빈 리스트로 처리한다.
    # 예: ["Pressure","Power1h","Ion Flux"]
    parameters: str | None = Form(default=None),
    # solver_log는 선택 입력이다. 파일이 없으면 서비스에서 로그 파싱/검증을 건너뛴다.
    solver_log: UploadFile | None = File(default=None),
    # 요청 단위 DB 세션 주입.
    db: Session = Depends(get_db),
):
    
    return await ask_question_service(
        db,
        user_id=current_user.user_id,
        session_id=session_id,
        query_text=query_text,
        parameters=parameters,
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


# 분석 그래프 조회 API.
# 질의응답 API에서는 has_analysis만 내려주고,
# 프론트가 분석 그래프 보기 버튼을 누르면 log_id 기준으로 입력 데이터와 AI 유사 로그 데이터를 조회한다.
@router.get("/logs/{log_id}/analysis", response_model=AnalysisResponse)
def get_analysis_data(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_analysis_data_service(
        db,
        user_id=current_user.user_id,
        log_id=log_id,
    )

