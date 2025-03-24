import json
import os
from typing import Optional, List, Dict
from datetime import datetime

from app.core.config import settings
from app.models.user import UserInDB, UserCreate
from app.core.auth import get_password_hash, verify_password

# 사용자 데이터 파일 경로
USER_DATA_FILE = os.path.join(settings.CONTENT_DIR, "users.json")

# 초기 사용자 데이터 (파일이 없는 경우 생성)
DEFAULT_USERS = [
    {
        "id": 1,
        "email": "rupi@gmail.com",
        "username": "rupi",
        "hashed_password": get_password_hash("rupi@@1234"),
        "is_active": True,
        "role": "admin"
    }
]

def _ensure_user_file_exists():
    """사용자 데이터 파일이 존재하는지 확인하고 없으면 생성"""
    if not os.path.exists(USER_DATA_FILE):
        os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)
        with open(USER_DATA_FILE, "w") as f:
            json.dump(DEFAULT_USERS, f, indent=2)

def _get_users() -> List[Dict]:
    """모든 사용자 데이터 가져오기"""
    _ensure_user_file_exists()
    with open(USER_DATA_FILE, "r") as f:
        return json.load(f)

def _save_users(users: List[Dict]):
    """사용자 데이터 저장"""
    with open(USER_DATA_FILE, "w") as f:
        json.dump(users, f, indent=2)

def get_user_by_username(username: str) -> Optional[UserInDB]:
    """사용자명으로 사용자 찾기"""
    users = _get_users()
    for user in users:
        if user["username"] == username:
            return UserInDB(**user)
    return None

def get_user_by_email(email: str) -> Optional[UserInDB]:
    """이메일로 사용자 찾기"""
    users = _get_users()
    for user in users:
        if user["email"] == email:
            return UserInDB(**user)
    return None

def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """사용자 인증"""
    user = get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_user(user_data: UserCreate) -> UserInDB:
    """새 사용자 생성"""
    users = _get_users()
    
    # 중복 확인
    if get_user_by_username(user_data.username) or get_user_by_email(user_data.email):
        raise ValueError("이미 존재하는 사용자명 또는 이메일입니다.")
    
    # 새 사용자 ID 생성 (단순히 가장 큰 ID + 1)
    new_id = max([user["id"] for user in users], default=0) + 1
    
    # 새 사용자 데이터 생성
    new_user = {
        "id": new_id,
        "email": user_data.email,
        "username": user_data.username,
        "hashed_password": get_password_hash(user_data.password),
        "is_active": True,
        "role": "user"  # 기본 역할은 일반 사용자
    }
    
    # 사용자 추가 및 저장
    users.append(new_user)
    _save_users(users)
    
    return UserInDB(**new_user) 