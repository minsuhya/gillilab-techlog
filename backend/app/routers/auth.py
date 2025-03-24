from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Any

from app.core.auth import (
    create_access_token, 
    get_current_active_user, 
    get_current_admin_user
)
from app.core.config import settings
from app.models.user import User, UserCreate, Token, UserInDB
from app.services.user_service import authenticate_user, create_user, get_user_by_email

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """사용자 로그인 및 액세스 토큰 발급"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 사용자명 또는 비밀번호입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active
        }
    }

@router.post("/register", response_model=User)
async def register_user(user_data: UserCreate) -> Any:
    """새 사용자 등록 (관리자 승인 필요)"""
    # 이메일 중복 확인
    if get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다"
        )
    
    try:
        user = create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/me", response_model=User)
async def read_users_me(current_user: UserInDB = Depends(get_current_active_user)) -> Any:
    """자신의 사용자 정보 조회"""
    return current_user 