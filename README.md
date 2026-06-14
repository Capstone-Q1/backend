# Q1 Backend

FastAPI 기반 백엔드 서버입니다.

사용자의 자연어 질문과 `solver.log` 파일을 받아 AI 서버에 질의하고, 응답 결과와 유사 로그 분석 데이터를 PostgreSQL에 저장 및 조회합니다.

## 1. 프로젝트 개요 및 아키텍처

### 핵심 목적

이 프로젝트는 플라즈마 시뮬레이션 로그 파일인 `solver.log`를 기반으로 사용자의 질문에 답변하고, AI가 판단한 유사 로그 데이터를 함께 제공하는 백엔드 API 서버입니다.

주요 기능은 다음과 같습니다.

- JWT 기반 로그인/인증
- 채팅 세션 관리
- `solver.log` 업로드 및 검증
- 로그 파일 파싱
- AI 서버 질의 요청
- 질의/응답 이력 저장
- 유사 로그 분석 데이터 조회
- 대시보드 데이터 제공

### 전체 아키텍처

```text
Frontend
   |
   | HTTP Request
   v
FastAPI app/main.py
   |
   +-- Auth Router
   |     |
   |     +-- Auth Service
   |           |
   |           +-- Auth Repository
   |                 |
   |                 +-- users table
   |
   +-- Ask Question Router
         |
         +-- Ask Question Service
               |
               +-- Validation Chain
               +-- solver.log Parser
               +-- AI Request Client
               +-- Ask Question Repository
                     |
                     +-- chat_sessions table
                     +-- query_response_log table
                     +-- solver_results table
```

### Entry Point

프로그램의 진입점은 다음 파일입니다.

```text
app/main.py
```

실행 명령은 다음과 같습니다.

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

`app/main.py`는 FastAPI 앱을 생성하고, DB 테이블 생성, 예외 핸들러 등록, 라우터 연결을 수행합니다.

## 2. 파일 및 모듈별 상세 동작

### 루트 디렉토리

```text
Q1_backend/
├── app/
├── alembic/
├── scripts/
├── tmp/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── alembic.ini
└── README.md
```

### `app/main.py`

FastAPI 애플리케이션의 시작 파일입니다.

주요 역할:

- `FastAPI` 객체 생성
- CORS 설정
- 앱 시작 시 DB 테이블 생성
- 공통 예외 핸들러 등록
- `/health` API 제공
- 인증 라우터 등록
- 질문 처리 라우터 등록

등록되는 라우터:

```text
/api/v1/auth
/api/v1/ask-question
```

### `app/core/config.py`

환경변수를 관리합니다.

`.env` 파일에서 다음 설정을 읽습니다.

- `APP_NAME`
- `APP_ENV`
- `DEBUG`
- `DATABASE_URL`
- `AI_SERVER_URL`
- `AI_REQUEST_TIMEOUT`
- `MAX_LOG_FILE_SIZE_MB`
- `JWT_SECRET_KEY`
- `JWT_ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `REFRESH_TOKEN_EXPIRE_DAYS`

### `app/core/db.py`

SQLAlchemy DB 연결 설정을 담당합니다.

주요 객체:

```python
engine
SessionLocal
Base
```

역할:

- `DATABASE_URL`을 사용해 DB 엔진 생성
- 요청마다 사용할 DB 세션 생성기 정의
- 모든 모델이 상속받는 `Base` 생성

### `app/core/deps.py`

FastAPI 의존성 함수를 제공합니다.

주요 함수:

```python
get_db()
get_current_user()
```

`get_db()`는 요청마다 DB 세션을 생성하고, 요청이 끝나면 세션을 닫습니다.

`get_current_user()`는 `Authorization: Bearer <token>` 헤더에서 access token을 꺼내 검증하고, 현재 로그인한 사용자를 DB에서 조회합니다.

### `app/core/security.py`

인증과 보안 관련 기능을 담당합니다.

주요 함수:

```python
hash_password()
verify_password()
hash_token()
verify_token()
create_access_token()
create_refresh_token()
decode_access_token()
decode_refresh_token()
```

역할:

- 비밀번호 bcrypt 해싱
- 비밀번호 검증
- refresh token SHA-256 해싱
- JWT access token 생성
- JWT refresh token 생성
- JWT 검증 및 payload 파싱

### `app/core/exceptions.py`

공통 예외 클래스인 `AppException`을 정의합니다.

`AppException`은 다음 정보를 가집니다.

```text
message
status_code
error_code
```

`app/main.py`의 예외 핸들러가 이 예외를 JSON 응답으로 변환합니다.

## 3. 데이터 모델

### `User`

파일:

```text
app/models/user.py
```

테이블:

```text
users
```

역할:

- 사용자 계정 정보 저장
- 로그인 ID, 비밀번호 해시, 이름, 권한, refresh token hash 관리

주요 컬럼:

```text
user_id
login_id
password_hash
name
role
created_at
refresh_token_hash
```

### `ChatSession`

파일:

```text
app/models/chat_session.py
```

테이블:

```text
chat_sessions
```

역할:

- 사용자별 채팅방 정보 저장

주요 컬럼:

```text
session_id
user_id
title
created_at
updated_at
```

### `QueryResponseLog`

파일:

```text
app/models/query_response_log.py
```

테이블:

```text
query_response_log
```

역할:

- 사용자의 질문
- 업로드한 로그 파싱 결과
- AI 응답
- 유사 로그 파일명 목록
- 중요 파라미터 목록 저장

주요 컬럼:

```text
log_id
user_id
session_id
query_text
query_solver_log
query_parameters
response_text
response_case_ids
important_parameters
created_at
response_at
```

### `SolverResult`

파일:

```text
app/models/solver_result.py
```

테이블:

```text
solver_results
```

역할:

- 사전에 적재된 solver 로그의 상세 파라미터 저장
- AI가 반환한 유사 로그 파일명을 기준으로 상세 데이터 조회

## 4. 인증 기능

인증 관련 코드는 다음 디렉토리에 있습니다.

```text
app/features/auth/
```

### API 목록

| Method | URL | 설명 |
| --- | --- | --- |
| `POST` | `/api/v1/auth/login` | 로그인 |
| `POST` | `/api/v1/auth/refresh` | access token 재발급 |
| `GET` | `/api/v1/auth/me` | 현재 사용자 정보 조회 |
| `POST` | `/api/v1/auth/logout` | 로그아웃 |

### 실행 흐름

```text
Client
  |
  v
auth/router.py
  |
  v
auth/service.py
  |
  v
auth/repository.py
  |
  v
users table
```

### 로그인 흐름

1. 사용자가 `login_id`, `password`를 전송합니다.
2. `AuthRepository.find_by_login_id()`가 사용자를 조회합니다.
3. `verify_password()`가 비밀번호를 검증합니다.
4. access token과 refresh token을 생성합니다.
5. refresh token은 해시 처리 후 DB에 저장합니다.
6. 토큰과 사용자 정보를 응답합니다.

## 5. 질문 처리 기능

질문 처리 관련 코드는 다음 디렉토리에 있습니다.

```text
app/features/ask_question/
```

### API 목록

| Method | URL | 설명 |
| --- | --- | --- |
| `POST` | `/api/v1/ask-question/search` | 질문 전송 및 AI 응답 요청 |
| `GET` | `/api/v1/ask-question/sessions` | 채팅방 목록 조회 |
| `GET` | `/api/v1/ask-question/session/{session_id}` | 채팅방 상세 조회 |
| `DELETE` | `/api/v1/ask-question/session/{session_id}` | 채팅방 삭제 |
| `PATCH` | `/api/v1/ask-question/session/{session_id}/title` | 채팅방 제목 수정 |
| `GET` | `/api/v1/ask-question/dashboard/{session_id}` | 대시보드 데이터 조회 |
| `GET` | `/api/v1/ask-question/logs/{log_id}/analysis` | 분석 그래프 데이터 조회 |

### 질문 처리 흐름

```text
Client
  |
  v
ask_question/router.py
  |
  v
ask_question/service.py
  |
  +-- validation chain
  +-- parse_solver_log_text()
  +-- create_query_log()
  +-- request_ai_answer()
  +-- update_query_response()
  +-- update_chat_session_updated_at()
  |
  v
Response
```

### `ask_question_service()` 동작

1. `session_id`가 없으면 새 채팅방을 생성합니다.
2. `session_id`가 있으면 현재 사용자의 채팅방인지 확인합니다.
3. `parameters` 값을 JSON 배열 또는 콤마 문자열로 파싱합니다.
4. `solver_log`가 있으면 파일 검증을 수행합니다.
5. `solver.log` 내용을 파싱합니다.
6. 질문 로그를 `query_response_log`에 먼저 저장합니다.
7. AI 서버 요청 payload를 생성합니다.
8. AI 서버 `/api/v1/search`로 요청을 보냅니다.
9. AI 응답이 실패이면 실패 내용을 DB에 저장하고 예외를 발생시킵니다.
10. AI 응답이 성공이면 답변, 유사 로그, 중요 파라미터를 DB에 저장합니다.
11. 채팅방의 `updated_at`을 갱신합니다.
12. 프론트엔드 응답 형식으로 반환합니다.

## 6. solver.log 처리

### 검증 모듈

위치:

```text
app/features/ask_question/processors/validation/
```

검증 체인:

```text
QuestionRequiredValidator
SolverLogRequiredValidator
LogFileExtensionValidator
FileSizeValidator
EncodingValidator
SolverLogFormatValidator
RequiredParameterValidator
```

검증 항목:

- 질문 존재 여부
- 파일 존재 여부
- `.log` 확장자 여부
- 파일 크기 제한
- UTF-8 인코딩 여부
- 필수 섹션 존재 여부
- 필수 파라미터 존재 여부

### 파싱 모듈

위치:

```text
app/features/ask_question/processors/parsing/parse_log.py
```

주요 함수:

```python
parse_solver_log_text()
```

파싱 대상 섹션:

```text
[SIMULATION OPTIONS]
[CHAMBER GEOMETRY]
[SOURCE POWER CONDITIONS]
[PREASURE & INLET CONDITIONS]
[CONSIDERED SPECIES]
[TEMPERATURE PARAMETERS]
[HEATING PARAMETERS]
[SHEATH PARAMETERS]
[NUMBER DENSITY]
[ION FLUX AT THE SHEATH EDGE]
[RADICAL FLUX AT THE SHEATH EDGE]
[AVERAGE ION ENERGY AT THE SUBSTRATE]
```

### 변환 모듈

위치:

```text
app/features/ask_question/processors/utils/convert_to_json.py
```

주요 역할:

- 파싱 결과를 AI 요청 payload로 변환
- 파싱 결과를 DB 저장용 JSON 문자열로 변환
- DB row를 프론트엔드 응답 DTO로 변환
- 분석 그래프용 데이터 구조 생성

## 7. 실행 흐름

### 서버 시작 흐름

```text
1. uvicorn app.main:app 실행
2. .env 설정 로드
3. SQLAlchemy engine 생성
4. 모델 import
5. Base.metadata.create_all() 실행
6. FastAPI 라우터 등록
7. 요청 대기
```

### 로그인 요청 흐름

```text
1. POST /api/v1/auth/login
2. login_id로 사용자 조회
3. 비밀번호 검증
4. access token 생성
5. refresh token 생성
6. refresh token hash 저장
7. 로그인 응답 반환
```

### 질문 요청 흐름

```text
1. POST /api/v1/ask-question/search
2. Bearer token 검증
3. 채팅방 생성 또는 조회
4. solver.log 검증
5. solver.log 파싱
6. 질문 이력 DB 저장
7. AI 서버 요청
8. AI 응답 DB 저장
9. 채팅방 updated_at 갱신
10. 응답 반환
```

## 8. 환경 구축

### Python 환경

```bash
conda create -n capstone_Q1 python=3.10
conda activate capstone_Q1
pip install -r requirements.txt
```

### 필수 패키지

`requirements.txt` 기준 주요 패키지는 다음과 같습니다.

```text
fastapi
uvicorn
sqlalchemy
pydantic-settings
python-dotenv
python-multipart
httpx
psycopg[binary]
alembic
PyJWT
passlib[bcrypt]
bcrypt
```

## 9. 환경 변수 예시

`.env` 예시는 다음과 같습니다.

```env
APP_NAME=Q1 Backend
APP_ENV=local
DEBUG=true

POSTGRES_DB=q1_backend
POSTGRES_USER=q1_user
POSTGRES_PASSWORD=q1_password
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

DATABASE_URL=postgresql+psycopg://q1_user:q1_password@postgres:5432/q1_backend

AI_SERVER_URL=http://ai-server:8001
AI_REQUEST_TIMEOUT=30
MAX_LOG_FILE_SIZE_MB=5

JWT_SECRET_KEY=change-me
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=14
```

## 10. 로컬 실행

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

헬스 체크:

```bash
curl http://localhost:8000/health
```

응답 예시:

```json
{
  "success": true,
  "message": "server is running"
}
```

## 11. Docker Compose 실행

### PostgreSQL만 먼저 실행

```bash
docker compose up -d postgres
```

### 백엔드 빌드 및 실행

```bash
docker compose up --build backend
```

### 전체 서비스 실행

```bash
docker compose up -d --build
```

### 컨테이너 상태 확인

```bash
docker compose ps
```

### PostgreSQL 접속

```bash
docker exec -it q1_postgres psql -U q1_user -d q1_backend
```

## 12. 초기 데이터 적재

### 테스트 유저 생성

```bash
python scripts/seed_users.py
```

Docker 환경:

```bash
docker compose exec backend python scripts/seed_users.py
```

### solver_results 데이터 적재

`tmp/000.log`부터 `tmp/149.log`까지 로그 파일을 DB에 적재합니다.

```bash
python -m app.features.ask_question.processors.utils.insert_log \
  --data-dir tmp \
  --start 0 \
  --end 149 \
  --truncate
```

Docker 환경:

```bash
docker compose exec backend python -m app.features.ask_question.processors.utils.insert_log \
  --data-dir tmp \
  --start 0 \
  --end 149 \
  --truncate
```

## 13. Alembic

Alembic은 DB 스키마 변경 이력을 관리합니다.

설정 파일:

```text
alembic.ini
alembic/env.py
```

마이그레이션 생성:

```bash
alembic revision --autogenerate -m "message"
```

마이그레이션 적용:

```bash
alembic upgrade head
```

마이그레이션 롤백:

```bash
alembic downgrade -1
```

현재 프로젝트는 앱 시작 시 `Base.metadata.create_all()`을 실행하므로, 초기 테이블 생성은 FastAPI 서버 시작 과정에서도 수행됩니다.

## 14. Git 사용 예시

```bash
git status
git checkout -b feature/example
git add .
git commit -m "feat: add example feature"
git push origin feature/example
```

## 15. 참고 사항

- 인증은 쿠키가 아니라 `Authorization: Bearer <access_token>` 방식입니다.
- refresh token은 원본이 아니라 SHA-256 hash로 DB에 저장됩니다.
- AI 서버 주소는 `AI_SERVER_URL` 환경변수로 설정합니다.
- AI 요청 엔드포인트는 `{AI_SERVER_URL}/api/v1/search`입니다.
- CORS는 기본적으로 `http://localhost:3000`을 허용합니다.
- `tmp/` 디렉토리는 solver 로그 샘플 데이터 저장용입니다.
- `.env` 파일은 민감 정보를 포함하므로 Git에 커밋하지 않습니다.
