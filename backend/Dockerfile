# Python 3.13 Alpine 이미지 사용
FROM python:3.13-alpine

# 작업 디렉토리 설정
WORKDIR /backend

# 시스템 의존성 설치
RUN apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev

# Python 패키지 경로 설정
ENV PATH="/usr/local/bin:${PATH}"

# pip 업그레이드 및 의존성 설치
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir wheel

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 