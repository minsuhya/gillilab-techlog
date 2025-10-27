# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

GilliLab IT 기술 블로그의 프론트엔드 애플리케이션입니다. Vue 3 기반의 SPA로, 디렉토리 기반 카테고리 자동 관리와 마크다운 렌더링을 제공하는 기술 블로그입니다.

## 핵심 개발 명령어

```bash
# 개발 서버 시작 (http://localhost:5173)
pnpm run dev

# 프로덕션 빌드 (RSS 및 사이트맵 자동 생성)
pnpm run build

# 프로덕션 빌드 미리보기
pnpm run serve
```

## 아키텍처 개요

### 상태 관리 (Pinia Stores)

- **auth.js**: JWT 토큰 기반 인증 상태 관리. localStorage에 토큰 저장, 자동 로그인 체크
- **posts.js**: 포스트 및 카테고리 데이터 관리. CRUD 작업 처리

### 라우팅 구조

라우터는 3개의 가드를 순차적으로 실행합니다:
1. **URL 디코딩 가드** (index.js:55): 경로 파라미터의 특수 문자 자동 디코딩
2. **인증 가드** (index.js:64): `requiresAuth`, `requiresAdmin` 메타 필드 확인
3. **애널리틱스 가드** (index.js:88): Google Analytics 및 Naver Analytics 페이지뷰 추적

### API 통신

- **utils/api.js**: axios 인스턴스를 중앙에서 관리
  - 요청 인터셉터: localStorage에서 토큰을 읽어 Authorization 헤더에 자동 추가
  - 응답 인터셉터: 401 에러 시 토큰 삭제 및 로그인 페이지로 리다이렉트
- **config/index.js**: 환경변수 중앙 관리 및 유효성 검사

### 빌드 시스템 (vite.config.js)

프로덕션 빌드 시 커스텀 플러그인이 자동으로 실행됩니다:
- **rssPlugin** (vite.config.js:118): 백엔드 API에서 RSS 피드와 사이트맵을 가져와 dist 폴더에 저장
- 빌드 전 백엔드 서버 실행 필요 (health check 수행)
- 청크 분할: vendor 청크(vue, vue-router, pinia)로 분리
- Terser를 사용한 최적화: console 및 debugger 제거

### 전역 유틸리티 (main.js)

Vue 인스턴스에 전역 메서드로 등록:
- `$md(text)`: Marked + DOMPurify를 사용한 안전한 마크다운 렌더링
- `$formatDate(dateString)`: 한국어 날짜 포맷팅
- `$formatCategory(categoryPath)`: 카테고리 경로를 " > "로 조인

## 환경변수 설정

`.env` 파일 생성 필요 (`.env.example` 참고):

```bash
VITE_API_URL=http://localhost:8000          # 백엔드 API URL
VITE_GA_MEASUREMENT_ID=G-XXX                # Google Analytics ID
VITE_ADSENSE_PUBLISHER_ID=ca-pub-XXX        # Google AdSense ID
VITE_NAVER_SITE_ID=XXX                      # Naver Analytics ID
VITE_SITE_TITLE=사이트 제목
VITE_SITE_DESCRIPTION=사이트 설명
VITE_SITE_URL=https://example.com
VITE_SITE_IMAGE=https://example.com/logo.png
VITE_SITE_AUTHOR=작성자명
```

## 백엔드 연동

- 개발 모드: Vite 프록시가 `/api/*` 요청을 백엔드로 전달 (vite.config.js:162)
- 프로덕션: `VITE_API_URL`로 직접 요청
- 기본 포트: 백엔드 8000, 프론트엔드 5173

## 스타일링

- Tailwind CSS 사용
- `@tailwindcss/typography` 플러그인: 마크다운 콘텐츠 스타일링
- 커스텀 컬러 (tailwind.config.js:9):
  - primary: #3b82f6 (파란색)
  - secondary: #64748b (회색)
  - accent: #0ea5e9 (밝은 파란색)

## 인증 흐름

1. 로그인: LoginView → useAuthStore.login() → localStorage에 토큰 저장
2. 보호된 라우트 접근: 라우터 가드가 토큰 확인 → 없으면 로그인 페이지로 리다이렉트
3. API 요청: axios 인터셉터가 자동으로 Authorization 헤더 추가
4. 토큰 만료: 401 응답 시 자동 로그아웃 및 로그인 페이지로 리다이렉트

## 컴포넌트 구조

- **CategoryTree.vue / TreeItem.vue / CategoryNode.vue**: 재귀적 트리 구조로 카테고리 표시
- **CategoryList.vue**: 카테고리 목록 표시
- **AdDisplay.vue**: Google AdSense 광고 컴포넌트
- **Views**: HomeView, PostView, CategoryView, AdminView, LoginView
