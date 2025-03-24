from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class Post(BaseModel):
    """블로그 포스트 모델"""
    id: str
    title: str
    path: str
    category: str
    description: Optional[str] = None
    content: Optional[str] = None
    content_html: Optional[str] = None
    author: Optional[str] = "admin"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    tags: Optional[List[str]] = []

class PostList(BaseModel):
    """포스트 목록 모델"""
    items: List[Post] 