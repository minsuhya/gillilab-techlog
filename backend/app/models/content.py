from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class CategoryBase(BaseModel):
    """카테고리 기본 모델"""
    id: str
    name: str
    path: str
    type: str = "directory"

class FileItem(BaseModel):
    """파일 아이템 모델"""
    id: str
    name: str
    path: str
    type: str = "file"
    title: Optional[str] = None
    description: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.now)

class CategoryItem(CategoryBase):
    """카테고리 아이템 모델 - 자식 요소를 포함"""
    children: List[Any] = []

# 재귀적 타입 정의를 위한 업데이트
CategoryItem.model_rebuild()

class PostBase(BaseModel):
    """게시물 기본 모델"""
    title: str
    content: str
    category: str
    description: Optional[str] = None

class PostCreate(PostBase):
    """게시물 생성 모델"""
    path: Optional[str] = None  # 직접 지정하지 않으면 자동 생성

class PostUpdate(BaseModel):
    """게시물 업데이트 모델"""
    title: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None

class Post(PostBase):
    """게시물 응답 모델"""
    id: str
    path: str
    created_at: datetime
    updated_at: datetime
    prev_post: Optional[Dict[str, str]] = None
    next_post: Optional[Dict[str, str]] = None 