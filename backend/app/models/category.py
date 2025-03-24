from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Category(BaseModel):
    """카테고리 모델"""
    id: str
    name: str
    path: str
    type: str
    children: Optional[List['Category']] = []
    description: Optional[str] = None

# 순환 참조 해결
Category.model_rebuild()

class CategoryList(BaseModel):
    """카테고리 목록 모델"""
    items: List[Category] 