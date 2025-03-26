from typing import List, Optional
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
from fastapi.responses import Response as FastAPIResponse
from feedgen.feed import FeedGenerator
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import status

from app.core.auth import (UserInDB, get_current_active_user,
                           get_current_admin_user)
from app.models.post import Post, PostList, PostCreate, PostUpdate
from app.services.content_service import content_service, ContentService
from app.core.config import settings
from app.core.security import verify_token
from app.core.auth import get_current_user
from app.models.user import User
from app.core.logger import logger
import json
import pytz

router = APIRouter()
security = HTTPBearer()


@router.get("/health")
async def health_check():
    """서버 상태 확인"""
    return JSONResponse(
        content={
            "status": "healthy",
            "timestamp": datetime.now(timezone(timedelta(hours=9))).isoformat(),
            "version": "v0.1"
        }
    )


@router.get("/posts", response_model=List[Post])
async def get_all_posts(
    content_service: ContentService = Depends()
):
    """
    모든 포스트의 기본 정보를 반환합니다.
    sitemap.xml 생성에 필요한 최소한의 데이터만 포함합니다.
    """
    try:
        # 먼저 캐시 갱신
        await content_service.refresh_content_cache()
        # 그 다음 포스트 목록 반환
        posts = content_service.get_all_posts()
        return JSONResponse(
            content=jsonable_encoder(posts),
            headers={
                "Cache-Control": "public, max-age=3600",  # 1시간 캐시
                "Content-Type": "application/json"
            }
        )
    except Exception as e:
        logger.error(f"포스트 목록 조회 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="포스트 목록을 가져오는 중 오류가 발생했습니다."
        )


@router.get("/posts/recent", response_model=List[Post])
async def get_recent_posts(
    limit: int = 5,
    content_service: ContentService = Depends()
):
    """
    최근 포스트 목록을 반환합니다.
    """
    try:
        posts = content_service.get_recent_posts(limit)
        return JSONResponse(
            content=jsonable_encoder(posts),
            headers={
                "Cache-Control": "public, max-age=300",
                "Content-Type": "application/json"
            }
        )
    except Exception as e:
        logger.error(f"최근 포스트 조회 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="최근 포스트를 가져오는 중 오류가 발생했습니다."
        )


@router.get("/posts/{category_path:path}/adjacent")
async def get_adjacent_posts(
    category_path: str = Path(..., description="카테고리 경로"),
    current: str = Query(..., description="현재 포스트 경로"),
    content_service: ContentService = Depends()
):
    """이전 및 다음 포스트 가져오기"""
    try:
        # URL 디코딩
        decoded_category = category_path.replace('%2F', '/')
        decoded_current = current.replace('%2F', '/')
        
        # 카테고리 경로가 현재 포스트의 상위 카테고리인지 확인
        if decoded_current.startswith(f"{decoded_category}/"):
            target_category = decoded_category
        else:
            # 현재 포스트의 카테고리 경로 추출
            target_category = decoded_current.rsplit('/', 1)[0]
        
        # 해당 카테고리의 모든 포스트 가져오기
        posts = content_service.get_posts_by_category(target_category)
        
        # 파일명의 4자리 숫자 prefix로 정렬
        posts.sort(key=lambda x: x.get("path", "").split("/")[-1][:4])
        
        # 현재 포스트 인덱스 찾기
        current_index = -1
        for i, post in enumerate(posts):
            if post.get("path") == decoded_current:
                current_index = i
                break
        
        result = {"previous": None, "next": None}
        
        # 이전 포스트 (더 최신 포스트)
        if current_index > 0:
            prev_post = posts[current_index - 1]
            result["previous"] = {
                "id": prev_post["id"],
                "path": prev_post["path"],
                "title": prev_post["title"],
                "category": prev_post["category"],
                "updated_at": prev_post["updated_at"]
            }
        
        # 다음 포스트 (더 이전 포스트)
        if current_index != -1 and current_index < len(posts) - 1:
            next_post = posts[current_index + 1]
            result["next"] = {
                "id": next_post["id"],
                "path": next_post["path"],
                "title": next_post["title"],
                "category": next_post["category"],
                "updated_at": next_post["updated_at"]
            }
        
        return JSONResponse(
            content=jsonable_encoder(result),
            headers={
                "Cache-Control": "public, max-age=300",
                "Content-Type": "application/json"
            }
        )
    except Exception as e:
        logger.error(f"이전/다음 포스트 조회 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="이전/다음 포스트를 가져오는 중 오류가 발생했습니다."
        )


@router.get("/posts/category/{category_path:path}", response_model=List[Post])
async def get_posts_by_category(
    category_path: str,
    content_service: ContentService = Depends()
):
    """
    특정 카테고리의 포스트 목록을 반환합니다.
    """
    try:
        posts = content_service.get_posts_by_category(category_path)
        return JSONResponse(
            content=jsonable_encoder(posts),
            headers={
                "Cache-Control": "public, max-age=300",
                "Content-Type": "application/json"
            }
        )
    except Exception as e:
        logger.error(f"카테고리별 포스트 조회 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="카테고리별 포스트를 가져오는 중 오류가 발생했습니다."
        )


@router.get("/posts/{post_path:path}", response_model=Post)
async def get_post_by_path(
    post_path: str,
    content_service: ContentService = Depends()
):
    """
    특정 포스트의 상세 정보를 반환합니다.
    """
    try:
        post = content_service.get_post_by_path(post_path)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="포스트를 찾을 수 없습니다."
            )
        return JSONResponse(
            content=jsonable_encoder(post),
            headers={
                "Cache-Control": "public, max-age=300",
                "Content-Type": "application/json"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"포스트 조회 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="포스트를 가져오는 중 오류가 발생했습니다."
        )


@router.get("/feed/rss")
async def get_rss_feed(
    content_service: ContentService = Depends()
):
    """
    RSS 피드를 생성합니다.
    """
    try:
        fg = FeedGenerator()
        fg.title('GilliLab Blog')
        fg.description('GilliLab Blog RSS Feed')
        fg.link(href='https://gillilab.com')
        fg.language('ko')
        
        # 최근 20개의 포스트 가져오기
        posts = content_service.get_recent_posts(20)
        
        for post in posts:
            fe = fg.add_entry()
            fe.title(post['title'])
            fe.link(href=f"https://gillilab.com/post/{post['id']}")
            fe.description(post.get('description', ''))
            fe.content(post.get('content', ''))
            
            # 파일 생성/수정 시간 가져오기
            file_path = content_service.get_post_file_path(post['id'])
            if file_path and file_path.exists():
                stat = os.stat(file_path)
                fe.published(datetime.fromtimestamp(stat.st_ctime, tz=pytz.timezone('Asia/Seoul')))
                fe.updated(datetime.fromtimestamp(stat.st_mtime, tz=pytz.timezone('Asia/Seoul')))
            else:
                now = datetime.now(pytz.timezone('Asia/Seoul'))
                fe.published(now)
                fe.updated(now)
            
            # 썸네일이 있는 경우 추가
            if post.get('thumbnail'):
                fe.enclosure(url=post['thumbnail'], type='image/jpeg')
        
        return FastAPIResponse(
            content=fg.rss_str(encoding='utf-8'),
            media_type='application/rss+xml; charset=utf-8',
            headers={
                'Content-Type': 'application/rss+xml; charset=utf-8'
            }
        )
    except Exception as e:
        logger.error(f"RSS 피드 생성 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RSS 피드 생성 중 오류 발생: {str(e)}"
        )


# 관리자 전용 엔드포인트 (인증 필요)
@router.post("/admin/posts", response_model=Post)
async def create_post(
    post: PostCreate,
    content_service: ContentService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """
    새로운 포스트를 생성합니다.
    """
    try:
        created_post = content_service.create_post(post)
        return JSONResponse(
            content=jsonable_encoder(created_post),
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        logger.error(f"포스트 생성 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="포스트 생성 중 오류가 발생했습니다."
        )


@router.put("/admin/posts/{post_id}", response_model=Post)
async def update_post(
    post_id: str,
    post: PostUpdate,
    content_service: ContentService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """
    기존 포스트를 수정합니다.
    """
    try:
        updated_post = content_service.update_post(post_id, post)
        if not updated_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="포스트를 찾을 수 없습니다."
            )
        return JSONResponse(content=jsonable_encoder(updated_post))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"포스트 수정 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="포스트 수정 중 오류가 발생했습니다."
        )


@router.delete("/admin/posts/{post_id}")
async def delete_post(
    post_id: str,
    content_service: ContentService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """
    포스트를 삭제합니다.
    """
    try:
        if not content_service.delete_post(post_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="포스트를 찾을 수 없습니다."
            )
        return {"message": "포스트가 삭제되었습니다."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"포스트 삭제 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="포스트 삭제 중 오류가 발생했습니다."
        )


@router.post("/admin/posts/refresh")
async def refresh_posts(
    content_service: ContentService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """
    포스트 캐시를 수동으로 갱신합니다.
    """
    try:
        await content_service.refresh_content_cache()
        return {"message": "포스트 캐시가 갱신되었습니다."}
    except Exception as e:
        logger.error(f"포스트 캐시 갱신 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="포스트 캐시 갱신 중 오류가 발생했습니다."
        )
