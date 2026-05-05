from fastapi import UploadFile, File

from parse_log import parse_solver_log_text


async def ask_question(solver_log: UploadFile = File(...)):
    raw_bytes = await solver_log.read()      # 파일 원본
    text = raw_bytes.decode("utf-8")         # 문자열 변환
    parsed = parse_solver_log_text(text)     # 네 파서 호출
    return {"ok": True, "keys": list(parsed.keys())}
