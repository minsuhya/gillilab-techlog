# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

GilliLab IT Blog의 백엔드 API 서버입니다. FastAPI 기반으로 마크다운 파일 기반 블로그 시스템을 제공합니다.

## 개발 환경

- **Python 버전**: 3.13 이상
- **패키지 관리**: uv (pyproject.toml)
- **웹 프레임워크**: FastAPI
- **인증**: JWT (python-jose) + Argon2 해싱

## 주요 명령어

### 개발 서버 실행
```bash
# FastAPI 개발 서버 (hot reload 활성화)
uv run fastapi dev main.py

# 또는 직접 실행
python main.py

# 또는 uvicorn 직접 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 의존성 관리
```bash
# 의존성 설치
uv sync

# 의존성 추가
uv add <package-name>

# requirements.txt 생성 (Docker 빌드용)
uv pip compile pyproject.toml -o requirements.txt
```

### Docker
```bash
# Docker 이미지 빌드
docker build -t gillilab-backend .

# Docker 컨테이너 실행
docker run -p 8000:8000 -v ./data:/backend/data gillilab-backend
```

## 아키텍처

### 핵심 구조

이 프로젝트는 **파일 시스템 기반 콘텐츠 관리 시스템**입니다. 데이터베이스 대신 마크다운 파일을 직접 읽고 쓰며, 메타데이터는 메모리 캐시에 저장합니다.

#### 계층 구조
```
main.py (엔트리포인트)
  └─> app/main.py (FastAPI 앱)
       ├─> app/routers/* (API 엔드포인트)
       ├─> app/services/content_service.py (콘텐츠 관리 핵심)
       ├─> app/services/user_service.py (사용자 관리)
       └─> app/core/* (인증, 보안, 설정)
```

### ContentService (app/services/content_service.py)

**가장 중요한 컴포넌트**입니다. 파일 시스템과의 모든 상호작용을 담당합니다.

#### 주요 특징:
- **메모리 캐시**: `content_cache` 딕셔너리에 카테고리 트리와 포스트 메타데이터 저장
- **파일 해시 추적**: `file_hashes`로 파일 변경 여부 감지 (mtime 기반)
- **자동 갱신**: `watchdog` 라이브러리로 파일 시스템 변경 감지
  - 마크다운 파일 생성/수정/삭제/이동 시 2초 debounce 후 자동 갱신
  - 5분마다 강제 갱신 (`_refresh_interval`)
- **동시성 제어**: `asyncio.Lock`으로 캐시 갱신 중 경합 방지

#### 캐시 구조:
```python
content_cache = {
    "categories": [...]  # 재귀적 디렉토리 트리
    "posts": {           # post_id -> 메타데이터 매핑
        "category/post-name": {
            "id", "title", "path", "category",
            "description", "content", "content_html",
            "updated_at"
        }
    },
    "last_updated": "ISO 8601 timestamp"
}
```

#### 중요 메서드:
- `refresh_content_cache()`: 전체 캐시 재구축 (비동기, 락 사용)
- `_scan_directory()`: 재귀적으로 디렉토리 스캔하여 카테고리/포스트 수집
- `_get_post_metadata()`: 마크다운 파일 파싱 (제목, 설명, HTML 변환)
- `get_post_by_path()`: 캐시에서 포스트 조회

### 인증 시스템 (app/core/auth.py, app/services/user_service.py)

- **사용자 저장소**: `data/users.json` 파일 (간단한 JSON 기반)
- **비밀번호**: Argon2 해싱 (bcrypt 대신 사용)
- **JWT 토큰**: OAuth2 Bearer 방식
- **역할**: "admin" 또는 "user"

#### 기본 사용자:
```
username: rupi
password: rupi@@1234
role: admin
```

### 데이터 디렉토리 (data/)

- **위치**: `settings.DATA_DIR` (프로젝트 루트 상대 경로)
- **구조**:
  - 마크다운 파일(`.md`): 블로그 포스트
  - 디렉토리: 카테고리 (중첩 가능)
  - `users.json`: 사용자 데이터
  - `meta_cache.json`: 메타데이터 캐시 (사용되지 않음, 레거시)

#### 예시:
```
data/
├── python/
│   ├── intro.md
│   └── advanced/
│       └── asyncio.md
├── javascript/
│   └── basics.md
└── users.json
```

### 라우터 (app/routers/)

- **posts.py**: 포스트 CRUD, RSS 피드, 인접 포스트 조회
- **categories.py**: 카테고리 트리 조회
- **auth.py**: 로그인, 회원가입

#### 주요 엔드포인트:
- `GET /api/posts/recent`: 최근 포스트 목록
- `GET /api/posts/{post_path:path}`: 특정 포스트 상세
- `GET /api/posts/category/{category_path:path}`: 카테고리별 포스트
- `GET /api/feed/rss`: RSS 피드 생성
- `POST /api/admin/posts`: 포스트 생성 (관리자 전용)

## 코드 작성 시 유의사항

### 1. 파일 시스템 작업
- `ContentService` 싱글톤 인스턴스(`content_service`)를 통해서만 접근
- 직접 파일 I/O 수행 시 반드시 캐시 갱신 호출: `await content_service.refresh_content_cache()`
- 경로는 항상 상대 경로로 저장 (예: `"python/intro"`, `"python/advanced/asyncio"`)

### 2. 비동기 처리
- FastAPI 라우터는 `async def` 사용
- `ContentService.refresh_content_cache()`는 비동기 메서드
- 파일 변경 감지 핸들러에서 `asyncio.create_task()` 사용

### 3. 메타데이터 파싱
- 마크다운 제목: 첫 번째 `# ` 라인
- 설명: `<!-- mtoc-end -->` 주석 이후 첫 번째 단락 (최대 200자)
- HTML 변환: `markdown.markdown()` with `['fenced_code', 'tables', 'toc']` extensions

### 4. 캐싱 전략
- 포스트는 mtime 변경 시에만 재파싱
- `file_hashes` 딕셔너리로 파일별 mtime 추적
- 5분 이내 중복 갱신 요청은 무시

### 5. 인증 패턴
```python
from app.core.auth import get_current_user, get_current_admin_user

# 일반 사용자 인증 필요
@router.post("/example")
async def example(current_user: User = Depends(get_current_user)):
    ...

# 관리자 권한 필요
@router.post("/admin/example")
async def admin_example(current_user: User = Depends(get_current_admin_user)):
    ...
```

## 알려진 제약사항

1. **동시성**: 파일 쓰기 시 락이 없음 (여러 요청이 동시에 파일 수정 시 경합 가능)
2. **확장성**: 메모리 캐시 방식이므로 수천 개 이상의 포스트 시 메모리 부족 가능
3. **검색**: 전문 검색 기능 없음 (클라이언트 측에서 처리 필요)
4. **사용자 관리**: JSON 파일 기반이므로 대규모 사용자 관리 부적합
5. **트랜잭션**: 파일 시스템 기반이므로 ACID 보장 없음

## 프론트엔드 통합

- `app/main.py:40-41`에서 `../frontend/dist` 정적 파일 서빙
- CORS 모든 출처 허용 (`allow_origins=["*"]`) - 프로덕션에서 수정 필요
- 프론트엔드는 Vue/React 등 SPA 가정
