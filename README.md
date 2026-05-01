# backend

# 'capstone_Q1'이라는 이름으로 Python 3.10 환경 생성

conda create -n capstone_Q1 python=3.10

# 가상환경 활성화

conda activate capstone_Q1

# 특이사항

## DB 세션 주입 구조

이 프로젝트에서는 FastAPI와 SQLAlchemy를 사용하여 DB 작업을 처리한다.  
DB 작업은 요청마다 독립적인 `Session`을 생성하고, 요청 처리가 끝나면 해당 세션을 닫는 방식으로 관리한다.

여기서 말하는 세션은 로그인 세션이 아니라 **DB 세션**이다.

---

## DB 세션 주입이 필요한 이유

DB 세션 주입은 SQLite 때문에 필요한 것이 아니다.  
SQLite, MySQL, PostgreSQL 등 어떤 DB를 사용하더라도 SQLAlchemy 기반으로 DB 작업을 처리한다면 세션 관리가 필요하다.

DB 세션 주입의 목적은 다음과 같다.

1. API 요청마다 독립적인 DB 작업 단위를 만들기 위해
2. 요청 처리가 끝난 뒤 DB 세션을 안전하게 닫기 위해
3. router, service, repository 계층에서 같은 DB 세션을 공유하기 위해
4. DB 연결 누수와 불필요한 연결 유지를 방지하기 위해

---

## DB 세션 처리 흐름

```text
클라이언트 요청
    ↓
router.py
    ↓
Depends(get_db)로 DB 세션 주입
    ↓
service.py
    ↓
repository.py에서 DB 작업 수행
    ↓
응답 반환
    ↓
db.close()로 세션 종료
```
