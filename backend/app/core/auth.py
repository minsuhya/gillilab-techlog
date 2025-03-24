from datetime import datetime, timedelta
from typing import Optional, Union, Dict, Any
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import ValidationError

from app.core.config import settings
from app.models.user import User, UserInDB, TokenData

# 비밀번호 해싱 컨텍스트 설정 - bcrypt 대신 argon2 사용
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# OAuth2 설정
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """일반 텍스트 비밀번호와 해시된 비밀번호 비교"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """비밀번호 해싱"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """액세스 토큰 생성"""
    to_encode = data.copy()
    
    # 만료 시간 설정
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # JWT 토큰 생성
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """현재 인증된 사용자 가져오기"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="유효하지 않은 인증 정보",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 토큰 디코딩
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
        
        token_data = TokenData(username=username)
    except (JWTError, ValidationError):
        raise credentials_exception
    
    # 사용자 정보 조회 (예제 - 실제로는 DB에서 조회)
    # 이 부분은 실제 사용자 저장소에 맞게 수정해야 함
    from app.services.user_service import get_user_by_username
    user = get_user_by_username(username=token_data.username)
    
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """현재 활성 사용자 가져오기"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="비활성화된 사용자")
    return current_user

def is_admin(user: UserInDB) -> bool:
    """사용자가 관리자인지 확인"""
    return user.role == "admin"

async def get_current_admin_user(current_user: UserInDB = Depends(get_current_active_user)) -> UserInDB:
    """현재 관리자 사용자 가져오기"""
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 부족합니다. 관리자 권한이 필요합니다."
        )
    return current_user 