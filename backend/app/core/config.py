import os
import secrets
from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    API_PREFIX: str = "/api"
    
    # 토큰 설정
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24시간
    
    # 디렉토리 설정
    CONTENT_DIR: str = os.path.join(BASE_DIR, "data")
    
    # 데이터 디렉토리 설정
    DATA_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    
    # CORS 설정
    CORS_ORIGINS: List[str] = ["*"]
    
    @field_validator('CONTENT_DIR')
    def content_dir_must_exist(cls, v):
        if not os.path.exists(v):
            os.makedirs(v, exist_ok=True)
        return v

settings = Settings()

# 데이터 디렉토리가 없으면 생성
if not os.path.exists(settings.DATA_DIR):
    os.makedirs(settings.DATA_DIR)
    print(f"데이터 디렉토리 생성: {settings.DATA_DIR}") 