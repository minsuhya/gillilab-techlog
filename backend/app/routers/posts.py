from typing import List, Optional
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi.responses import Response
from feedgen.feed import FeedGenerator
import os

from app.core.auth import (UserInDB, get_current_active_user,
                           get_current_admin_user)
from app.models.post import Post, PostList
from app.services.content_service import content_service
from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone(timedelta(hours=9))).isoformat()
    }


@router.get("/posts/recent", response_model=List[Post])
async def get_recent_posts(limit: int = Query(5, ge=1, le=20)):
    """최근 포스트 목록 가져오기"""
    return content_service.get_recent_posts(limit=limit)


@router.get("/posts/category/{category_path:path}", response_model=List[Post])
async def get_posts_by_category(
    category_path: str = Path(..., description="카테고리 경로")
):
    """특정 카테고리의 포스트 목록 가져오기"""
    posts = content_service.get_posts_by_category(category_path)

    if not posts:
        # 오류가 아닌 빈 목록 반환
        return []

    return posts


@router.get("/posts/{category_path:path}/adjacent", response_model=dict)
async def get_adjacent_posts(
    category_path: str = Path(..., description="카테고리 경로"),
    current: str = Query(..., description="현재 포스트 경로"),
):
    """이전 및 다음 포스트 가져오기"""
    print(f"이전/다음 포스트 요청: 카테고리={category_path}, 현재={current}")

    # 카테고리 경로가 현재 포스트의 상위 카테고리인지 확인
    if current.startswith(f"{category_path}/"):
        print(f"현재 포스트 {current}는 카테고리 {category_path}의 하위 경로입니다.")
    elif "/" in current:
        # 현재 포스트의 카테고리 경로 추출
        post_category = current.rsplit("/", 1)[0]
        print(f"현재 포스트의 실제 카테고리: {post_category}")
        if post_category != category_path:
            print(f"카테고리 불일치 감지: 요청={category_path}, 실제={post_category}")
            # 포스트의 실제 카테고리로 가져오기
            category_path = post_category

    # 해당 카테고리의 모든 포스트 가져오기
    posts = content_service.get_posts_by_category(category_path)
    print(f"카테고리 {category_path}에서 {len(posts)}개의 포스트를 찾았습니다.")

    # 시간순으로 정렬 (최신순)
    posts.sort(key=lambda x: x.get("updated_at", ""), reverse=True)

    # 현재 포스트 인덱스 찾기
    current_index = -1
    for i, post in enumerate(posts):
        if post.get("path") == current:
            current_index = i
            break

    print(f"현재 포스트 '{current}'의 인덱스: {current_index}")

    result = {"previous": None, "next": None}

    # 이전 포스트 (더 최신 포스트)
    if current_index > 0:
        prev_post = posts[current_index - 1]
        result["previous"] = {
            "path": prev_post["path"],
            "title": prev_post["title"],
            "category": prev_post["category"],
        }
        print(f"이전 포스트 설정: {prev_post['title']}")

    # 다음 포스트 (더 이전 포스트)
    if current_index != -1 and current_index < len(posts) - 1:
        next_post = posts[current_index + 1]
        result["next"] = {
            "path": next_post["path"],
            "title": next_post["title"],
            "category": next_post["category"],
        }
        print(f"다음 포스트 설정: {next_post['title']}")

    print("반환 결과:", result)
    return result


@router.get("/posts/{post_path:path}", response_model=Post)
async def get_post(post_path: str = Path(..., description="포스트 경로")):
    """특정 포스트 가져오기"""
    post = content_service.get_post_by_path(post_path)

    if not post:
        raise HTTPException(
            status_code=404, detail=f"포스트를 찾을 수 없습니다: {post_path}"
        )

    return post


# 관리자 전용 API
@router.post("/admin/posts/refresh", status_code=200)
async def refresh_posts_cache(current_user: UserInDB = Depends(get_current_admin_user)):
    """포스트 캐시 수동 갱신 (관리자용)"""
    await content_service.refresh_content_cache()
    return {"status": "success", "message": "콘텐츠 캐시가 갱신되었습니다."}


@router.get("/feed/rss")
async def get_rss_feed():
    """RSS 피드 생성"""
    try:
        fg = FeedGenerator()
        fg.title('Gillilab Blog')
        fg.description('Gillilab Tech Blog')
        fg.link(href='https://gillilab.com')
        fg.language('ko')
        
        # 한국 시간대 설정
        kst = timezone(timedelta(hours=9))
        fg.lastBuildDate(datetime.now(kst))
        
        # 최근 포스트 가져오기
        posts = content_service.get_recent_posts(limit=20)
        
        for post in posts:
            fe = fg.add_entry()
            fe.title(post['title'])
            fe.link(href=f"https://gillilab.com/post/{post['id']}")
            fe.description(post.get('description', post['title']))
            fe.content(post['content'])
            
            # 파일의 생성 및 수정 시간 사용
            file_path = content_service.get_post_file_path(post['id'])
            if file_path and os.path.exists(file_path):
                file_stat = os.stat(file_path)
                created_at = datetime.fromtimestamp(file_stat.st_ctime, tz=kst)
                updated_at = datetime.fromtimestamp(file_stat.st_mtime, tz=kst)
                fe.published(created_at)
                fe.updated(updated_at)
            else:
                # 파일 정보가 없는 경우 현재 시간 사용
                current_time = datetime.now(kst)
                fe.published(current_time)
                fe.updated(current_time)
            
            if post.get('thumbnail_url'):
                fe.enclosure(url=post['thumbnail_url'], type='image/jpeg')
        
        # RSS 피드 생성 시 인코딩 설정
        rss_content = fg.rss_str(pretty=True, encoding='utf-8')
        
        # Response 헤더에 인코딩 정보 추가
        return Response(
            content=rss_content,
            media_type='application/rss+xml; charset=utf-8',
            headers={
                'Content-Type': 'application/rss+xml; charset=utf-8'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RSS 피드 생성 중 오류 발생: {str(e)}")
