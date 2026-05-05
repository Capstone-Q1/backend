# ask_question 라우터:
# HTTP 입력(Form/File)을 받아 서비스 레이어로 전달하는 진입점.
from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.features.ask_question.service import ask_question_service

router = APIRouter()


@router.post("/ask")
async def ask_question(
    # 사용자/세션/질의는 multipart form-data로 받는다.
    user_id: str = Form(...),
    session_id: int = Form(...),
    query_text: str = Form(...),
    # solver.log 원본 파일 업로드.
    solver_log: UploadFile = File(...),
    # 요청 단위 DB 세션 주입.
    db: Session = Depends(get_db),
):
    
    return await ask_question_service(
        db,
        user_id=user_id,
        session_id=session_id,
        query_text=query_text,
        solver_log=solver_log,
    )
