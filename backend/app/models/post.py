from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class PostBase(BaseModel):
    title: str
    content: str
    description: Optional[str] = None
    category: Optional[str] = None
    path: Optional[str] = None

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    path: Optional[str] = None

class Post(PostBase):
    id: str
    created_at: datetime
    updated_at: datetime
    prev_post: Optional[Dict] = None
    next_post: Optional[Dict] = None

    class Config:
        from_attributes = True

class PostList(BaseModel):
    posts: List[Post]
    total: int
    page: int
    size: int 