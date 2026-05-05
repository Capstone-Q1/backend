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

## Docker 실행 가이드

### 1) 구성 파일

- `Dockerfile`: FastAPI 백엔드 이미지를 빌드합니다.
- `docker-compose.yml`: `backend`(FastAPI) + `postgres`(DB) 서비스를 함께 실행합니다.
- `.env`: 앱 설정 및 DB 연결 문자열을 관리합니다.

### 2) 컨테이너 역할

- `backend` 컨테이너:
  - FastAPI 서버(`uvicorn app.main:app`)를 실행합니다.
  - API 요청 처리, DB 연결, 비즈니스 로직 수행을 담당합니다.
- `postgres` 컨테이너:
  - PostgreSQL DB 서버입니다.
  - 백엔드 데이터 저장소 역할을 담당합니다.

중요:

- `backend`에서 DB 접속 시 `localhost`가 아니라 `postgres`(docker-compose 서비스명)를 사용해야 합니다.
- 예: `DATABASE_URL=postgresql+psycopg://q1_user:q1_password@postgres:5432/q1_backend`

### 3) 실행 순서

1. DB만 먼저 실행

```bash
docker compose up -d postgres
```

# DB에 solver_log 결과 삽입

tmp에 0~149.log 150개를 넣어두고 insert_log 실행하면 db에 삽입됨
