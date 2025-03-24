# GilliLab IT 기술 블로그

GilliLab IT 기술 블로그는 정보관리기술사 자료 기반의 IT 기술 토픽 블로그입니다. 디렉토리 구조를 카테고리로 변환하여 체계적인 카테고리 및 토픽 관리와 쉬운 접근성을 제공합니다.

## 기능

- 디렉토리 기반 카테고리 자동 관리
- 마크다운 파일의 제목(# 제목) 자동 추출 및 리스트 생성
- 실시간 디렉토리 스캔 및 리스트 갱신
- 삼단 레이아웃: 좌측(트리 리스트) / 중앙(본문) / 우측(카테고리)
- 사용자 인증 및 권한 관리

## 기술 스택

### 프론트엔드
- Vue 3
- Tailwind CSS
- Pinia (상태 관리)
- Vue Router
- Marked (마크다운 렌더링)

### 백엔드
- FastAPI
- JWT 인증
- 파일 시스템 기반 데이터 관리

## 시작하기

### 요구사항
- Python 3.8+
- Node.js 16+
- npm 또는 yarn

### 설치 및 실행

#### 백엔드 설정
```bash
# 백엔드 디렉토리로 이동
cd backend

# 가상환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt

# 백엔드 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 프론트엔드 설정
```bash
# 프론트엔드 디렉토리로 이동
cd frontend

# 의존성 설치
npm install
# 또는
yarn install

# 개발 서버 실행
npm run dev
# 또는
yarn dev
```

### 초기 계정
- 사용자명: admin
- 비밀번호: admin123

## 사용 방법

1. 마크다운 파일을 적절한 디렉토리에 추가하면 자동으로 카테고리와 포스트 목록에 반영됩니다.
2. 관리자 계정으로 로그인하여 웹 인터페이스에서 포스트를 추가, 수정, 삭제할 수 있습니다.
3. 마크다운 파일의 첫 번째 헤더(# 제목)가 포스트 제목으로 자동 추출됩니다.

## 디렉토리 구조

```
gillilab-blog/
├── backend/
│   ├── app/
│   │   ├── core/         # 핵심 설정 및 유틸리티
│   │   ├── models/       # 데이터 모델
│   │   ├── routers/      # API 라우터
│   │   ├── services/     # 비즈니스 로직
│   │   └── main.py       # 메인 애플리케이션
│   ├── data/             # 콘텐츠 저장소
│   └── requirements.txt  # 의존성 목록
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/       # 정적 자산
│   │   ├── components/   # Vue 컴포넌트
│   │   ├── router/       # 라우팅 설정
│   │   ├── store/        # Pinia 스토어
│   │   ├── views/        # 페이지 뷰
│   │   └── App.vue       # 루트 컴포넌트
│   └── package.json      # 의존성 목록
└── README.md
```

## 라이센스

이 프로젝트는 MIT 라이센스로 제공됩니다.
