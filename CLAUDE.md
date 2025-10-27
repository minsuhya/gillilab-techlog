# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

GilliLab IT 기술 블로그는 정보관리기술사 자료 기반의 IT 기술 토픽 블로그입니다. 디렉토리 구조를 카테고리로 변환하여 체계적인 콘텐츠 관리와 쉬운 접근성을 제공하는 풀스택 웹 애플리케이션입니다.

### 기술 스택
- **프론트엔드**: Vue 3 + Tailwind CSS + Pinia + Vite
- **백엔드**: FastAPI + Python 3.13 + JWT 인증
- **배포**: Docker Compose + Nginx
- **데이터**: 파일 시스템 기반 마크다운 콘텐츠

## 핵심 개발 명령어

### 로컬 개발 환경

#### 백엔드 서버 실행
```bash
cd backend

# uv 사용 (권장)
uv run fastapi dev main.py

# 또는 직접 실행
python main.py

# 또는 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 프론트엔드 개발 서버 실행
```bash
cd frontend

# 의존성 설치
pnpm install

# 개발 서버 시작 (http://localhost:5173)
pnpm run dev
```

#### 프론트엔드 프로덕션 빌드
```bash
cd frontend

# RSS 및 사이트맵 자동 생성과 함께 빌드
# 주의: 백엔드 서버가 실행 중이어야 함
pnpm run build

# 빌드 결과 미리보기
pnpm run serve
```

### Docker Compose 실행

```bash
# 전체 스택 시작 (백엔드 + 프론트엔드 Nginx)
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

**포트 설정**:
- 프론트엔드 (Nginx): http://localhost:8082
- 백엔드 API: http://localhost:3001

## 아키텍처 개요

### 전체 구조

```
gillilab-techlog/
├── backend/              # FastAPI 백엔드
│   ├── app/
│   │   ├── core/        # 인증, 보안, 설정
│   │   ├── models/      # Pydantic 모델
│   │   ├── routers/     # API 엔드포인트
│   │   ├── services/    # 비즈니스 로직 (핵심!)
│   │   └── main.py      # FastAPI 앱
│   ├── data/            # 마크다운 콘텐츠 저장소
│   ├── main.py          # 엔트리포인트
│   └── pyproject.toml   # uv 의존성 관리
├── frontend/            # Vue 3 프론트엔드
│   ├── src/
│   │   ├── components/  # Vue 컴포넌트
│   │   ├── views/       # 페이지 뷰
│   │   ├── store/       # Pinia 상태 관리
│   │   ├── router/      # Vue Router
│   │   └── utils/       # API 클라이언트
│   └── vite.config.js   # Vite 설정 (RSS 플러그인 포함)
└── docker-compose.yml   # 배포 설정
```

### 핵심 설계 원칙

1. **파일 시스템 기반 콘텐츠 관리**: 데이터베이스 없이 마크다운 파일을 직접 읽고 쓰는 방식
2. **메모리 캐싱**: `ContentService`가 디렉토리 트리와 포스트 메타데이터를 메모리에 캐싱
3. **자동 갱신**: `watchdog` 라이브러리로 파일 변경 감지 및 캐시 자동 업데이트 (2초 debounce)
4. **JWT 인증**: 토큰 기반 인증, Argon2 비밀번호 해싱

### 데이터 흐름

```
브라우저 → Vue Router → Pinia Store → Axios API 클라이언트
  ↓                                          ↓
FastAPI Router ← ContentService ← 파일 시스템 (data/*.md)
  ↓
JWT 검증 (app/core/auth.py)
```

## 백엔드 중요 사항

### ContentService (app/services/content_service.py)

**가장 중요한 컴포넌트**로, 모든 파일 시스템 작업을 담당합니다.

#### 주요 기능:
- **메모리 캐시**: `content_cache` 딕셔너리에 카테고리 트리와 포스트 메타데이터 저장
- **파일 해시 추적**: `file_hashes`로 파일 변경 여부 감지 (mtime 기반)
- **자동 갱신**: 파일 생성/수정/삭제 감지 시 2초 후 자동 갱신, 5분마다 강제 갱신
- **동시성 제어**: `asyncio.Lock`으로 캐시 갱신 중 경합 방지

#### 캐시 구조:
```python
content_cache = {
    "categories": [...]  # 재귀적 디렉토리 트리
    "posts": {           # post_id -> 메타데이터 매핑
        "category/post-name": {...}
    },
    "last_updated": "ISO 8601 timestamp"
}
```

### 인증 시스템

- **저장소**: `data/users.json` 파일
- **비밀번호**: Argon2 해싱
- **JWT 토큰**: OAuth2 Bearer 방식
- **기본 관리자**: username: `rupi`, password: `rupi@@1234`

### API 엔드포인트

- `GET /api/posts/recent`: 최근 포스트 목록
- `GET /api/posts/{post_path:path}`: 포스트 상세
- `GET /api/posts/category/{category_path:path}`: 카테고리별 포스트
- `GET /api/feed/rss`: RSS 피드
- `POST /api/admin/posts`: 포스트 생성 (관리자 전용)

## 프론트엔드 중요 사항

### 상태 관리 (Pinia)

- **auth.js**: JWT 토큰 관리, localStorage에 저장
- **posts.js**: 포스트 및 카테고리 CRUD

### 라우터 가드 (3단계)

1. **URL 디코딩**: 경로 파라미터 특수 문자 디코딩
2. **인증 확인**: `requiresAuth`, `requiresAdmin` 메타 필드
3. **애널리틱스**: Google Analytics 및 Naver Analytics 추적

### 빌드 시스템

- **RSS 플러그인**: 프로덕션 빌드 시 백엔드 API에서 RSS 피드와 사이트맵을 가져와 dist 폴더에 저장
- **청크 분할**: vendor 청크로 분리 (vue, vue-router, pinia)
- **최적화**: Terser로 console/debugger 제거

### 환경변수

`.env` 파일 필요:
```bash
VITE_API_URL=http://localhost:8000
VITE_GA_MEASUREMENT_ID=G-XXX
VITE_ADSENSE_PUBLISHER_ID=ca-pub-XXX
VITE_NAVER_SITE_ID=XXX
VITE_SITE_TITLE=사이트 제목
VITE_SITE_DESCRIPTION=사이트 설명
VITE_SITE_URL=https://example.com
VITE_SITE_IMAGE=https://example.com/logo.png
VITE_SITE_AUTHOR=작성자명
```

## 개발 시 주의사항

### 백엔드
1. **파일 시스템 작업**: `ContentService` 싱글톤을 통해서만 접근
2. **캐시 갱신**: 직접 파일 I/O 후 `await content_service.refresh_content_cache()` 호출 필수
3. **비동기 처리**: FastAPI 라우터는 `async def` 사용
4. **경로 규칙**: 항상 상대 경로 사용 (예: `"python/intro"`)

### 프론트엔드
1. **프로덕션 빌드**: 빌드 전 백엔드 서버 실행 필수 (RSS 플러그인 health check)
2. **API 통신**: axios 인터셉터가 자동으로 Authorization 헤더 추가
3. **인증 흐름**: 401 응답 시 자동 로그아웃 및 로그인 페이지 리다이렉트

### Docker
1. **볼륨 마운트**: `./backend/data`를 마운트하여 콘텐츠 영속성 보장
2. **로그 제한**: 각 서비스는 최대 20MB 로그 파일 1개로 제한
3. **프론트엔드**: `./frontend/dist`를 Nginx로 서빙

## 알려진 제약사항

1. **동시성**: 파일 쓰기 시 락이 없어 동시 수정 시 경합 가능
2. **확장성**: 메모리 캐시 방식으로 수천 개 이상 포스트 시 메모리 부족 가능
3. **검색**: 전문 검색 기능 없음
4. **사용자 관리**: JSON 파일 기반으로 대규모 사용자 관리 부적합
5. **트랜잭션**: ACID 보장 없음

## 추가 문서

- `backend/CLAUDE.md`: 백엔드 상세 가이드
- `frontend/CLAUDE.md`: 프론트엔드 상세 가이드
