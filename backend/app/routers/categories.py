from fastapi import APIRouter, HTTPException, Path
from typing import List, Optional

from app.models.category import Category, CategoryList
from app.services.content_service import content_service

router = APIRouter()

@router.get("/categories", response_model=List[Category])
async def get_categories():
    """모든 카테고리 목록 가져오기"""
    return content_service.get_categories()

@router.get("/categories/{category_path:path}", response_model=Category)
async def get_category(category_path: str = Path(..., description="카테고리 경로")):
    """특정 카테고리 정보 가져오기"""
    # 'undefined' 경로 처리 - 루트 카테고리로 간주
    if category_path == "undefined" or not category_path:
        return {
            "id": "root",
            "name": "루트",
            "path": "",
            "type": "directory",
            "children": content_service.get_categories()
        }
    
    category = content_service.get_category_by_path(category_path)
    
    if not category:
        raise HTTPException(status_code=404, detail=f"카테고리를 찾을 수 없습니다: {category_path}")
    
    return category 