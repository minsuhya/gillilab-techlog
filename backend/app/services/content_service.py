import os
import re
import json
import hashlib
import uuid
import time
import asyncio
from typing import List, Dict, Optional, Any, Tuple, Set
from datetime import datetime
import markdown
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from app.core.config import settings
from app.models.content import CategoryItem, FileItem, Post, PostCreate, PostUpdate

# 메타데이터 캐시 파일
META_CACHE_FILE = os.path.join(settings.CONTENT_DIR, "meta_cache.json")

# 캐시된 컨텐츠 데이터
content_cache = {
    "categories": [],
    "posts": {},
    "last_updated": None
}

# 파일 변경 여부 추적
file_hashes: Dict[str, float] = {}

class ContentChangeHandler(FileSystemEventHandler):
    """파일 시스템 변경 이벤트 처리 핸들러"""
    
    def __init__(self, content_service):
        self.content_service = content_service
        self._pending_refresh = False
        self._last_event_time = 0
        self._refresh_delay = 2.0  # 2초 내 여러 변경사항 일괄 처리
    
    def _schedule_refresh(self):
        """변경 이벤트 발생 시 일정 시간 후 갱신 스케줄링"""
        current_time = time.time()
        
        # 마지막 이벤트로부터 충분한 시간이 지났는지 확인
        if current_time - self._last_event_time > self._refresh_delay:
            asyncio.create_task(self.content_service.refresh_content_cache())
            self._pending_refresh = False
        else:
            # 이미 대기 중인 갱신이 없으면 새로 예약
            if not self._pending_refresh:
                self._pending_refresh = True
                asyncio.create_task(self._delayed_refresh())
        
        self._last_event_time = current_time
    
    async def _delayed_refresh(self):
        """일정 시간 대기 후 컨텐츠 갱신"""
        await asyncio.sleep(self._refresh_delay)
        
        # 마지막 이벤트 이후 충분한 시간이 지났으면 갱신 실행
        if time.time() - self._last_event_time >= self._refresh_delay:
            await self.content_service.refresh_content_cache()
            self._pending_refresh = False
    
    def on_modified(self, event):
        """파일 수정 이벤트 처리"""
        if event.is_directory:
            return
            
        # 마크다운 파일에 대해서만 처리
        if event.src_path.endswith('.md'):
            self._schedule_refresh()
    
    def on_created(self, event):
        """파일 생성 이벤트 처리"""
        if event.is_directory:
            return
            
        # 마크다운 파일에 대해서만 처리
        if event.src_path.endswith('.md'):
            self._schedule_refresh()
    
    def on_deleted(self, event):
        """파일 삭제 이벤트 처리"""
        if event.is_directory:
            return
            
        # 마크다운 파일에 대해서만 처리
        if event.src_path.endswith('.md'):
            self._schedule_refresh()
    
    def on_moved(self, event):
        """파일 이동 이벤트 처리"""
        if event.is_directory:
            return
            
        # 마크다운 파일에 대해서만 처리
        if event.src_path.endswith('.md') or event.dest_path.endswith('.md'):
            self._schedule_refresh()


class ContentService:
    """콘텐츠 서비스: 파일 시스템에서 카테고리 및 포스트 관리"""
    
    def __init__(self):
        self.data_dir = Path(settings.DATA_DIR)
        self.observer = None
        self.event_handler = None
        self._cache_lock = asyncio.Lock()  # 캐시 동시성 제어를 위한 락 추가
        self._last_refresh = 0  # 마지막 갱신 시간
        self._refresh_interval = 300  # 5분마다 갱신
        
    async def start_file_watcher(self):
        """파일 시스템 변경 감지 시작"""
        if self.observer is None:
            self.event_handler = ContentChangeHandler(self)
            self.observer = Observer()
            self.observer.schedule(self.event_handler, str(self.data_dir), recursive=True)
            self.observer.start()
            print(f"파일 변경 감지 시작: {self.data_dir}")
    
    async def stop_file_watcher(self):
        """파일 시스템 변경 감지 중지"""
        if self.observer is not None:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            print("파일 변경 감지 중지")
    
    def _get_post_metadata(self, file_path: Path) -> dict:
        """마크다운 파일에서 메타데이터 추출 (최적화된 버전)"""
        metadata = {
            "id": str(file_path).replace(str(self.data_dir), "").lstrip("/").replace(".md", ""),
            "title": file_path.stem,
            "path": str(file_path).replace(str(self.data_dir), "").lstrip("/").replace(".md", ""),
            "category": str(file_path.parent).replace(str(self.data_dir), "").lstrip("/"),
            "updated_at": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 제목 추출 최적화
                title_match = re.search(r'^\s*#\s+(.+)$', content, re.MULTILINE)
                if title_match:
                    metadata["title"] = title_match.group(1).strip()
                
                # 설명 추출 최적화
                description = ""
                content_started = False
                mtoc_end_found = False
                
                for line in content.split('\n'):
                    line = line.strip()
                    
                    if line.startswith('<!-- mtoc-end -->'):
                        mtoc_end_found = True
                        continue
                    
                    if not mtoc_end_found:
                        continue
                    
                    if not content_started and line and not line.startswith('#') and not line.startswith('<!--'):
                        content_started = True
                    
                    if content_started:
                        if line:
                            description += line + " "
                        elif description:
                            break
                
                if description:
                    description = description.strip()
                    if len(description) > 200:
                        description = description[:197] + "..."
                
                metadata["description"] = description
                metadata["content"] = content
                metadata["content_html"] = markdown.markdown(
                    content, 
                    extensions=['fenced_code', 'tables', 'toc']
                )
                
        except Exception as e:
            print(f"메타데이터 파싱 오류 ({file_path}): {e}")
        
        return metadata
    
    def _scan_directory(self, directory: Path) -> List[dict]:
        """디렉토리 스캔하여 카테고리와 파일 목록 생성"""
        result = []
        
        try:
            for item in directory.iterdir():
                relative_path = str(item).replace(str(self.data_dir), "").lstrip("/")
                
                if item.is_dir():
                    # 디렉토리인 경우 (카테고리)
                    category_data = {
                        "id": relative_path,
                        "name": item.name,
                        "path": relative_path,
                        "type": "directory",
                        "children": self._scan_directory(item)
                    }
                    result.append(category_data)
                elif item.suffix == '.md':
                    # 마크다운 파일인 경우 (포스트)
                    file_data = {
                        "id": relative_path.replace(".md", ""),
                        "name": item.stem,
                        "path": relative_path.replace(".md", ""),
                        "type": "file"
                    }
                    result.append(file_data)
                    
                    # 포스트 메타데이터 캐싱
                    post_id = relative_path.replace(".md", "")
                    file_mtime = item.stat().st_mtime
                    
                    # 파일이 변경되었거나 캐시에 없는 경우만 처리
                    if post_id not in file_hashes or file_hashes[post_id] != file_mtime:
                        content_cache["posts"][post_id] = self._get_post_metadata(item)
                        file_hashes[post_id] = file_mtime
        except Exception as e:
            print(f"디렉토리 스캔 오류 ({directory}): {e}")
        
        return result
    
    async def refresh_content_cache(self):
        """콘텐츠 캐시 갱신 (최적화된 버전)"""
        current_time = time.time()
        
        # 캐시 락 획득
        async with self._cache_lock:
            # 마지막 갱신으로부터 충분한 시간이 지나지 않았다면 스킵
            if current_time - self._last_refresh < self._refresh_interval:
                return
            
            print("콘텐츠 캐시 갱신 시작...")
            
            try:
                # 카테고리 구조 스캔
                content_cache["categories"] = self._scan_directory(self.data_dir)
                
                # 캐시에 있는 포스트 중 파일이 삭제된 경우 제거
                existing_paths = set()
                for item in Path(self.data_dir).glob("**/*.md"):
                    relative_path = str(item).replace(str(self.data_dir), "").lstrip("/")
                    post_id = relative_path.replace(".md", "")
                    existing_paths.add(post_id)
                
                # 존재하지 않는 포스트 제거
                for post_id in list(content_cache["posts"].keys()):
                    if post_id not in existing_paths:
                        del content_cache["posts"][post_id]
                        if post_id in file_hashes:
                            del file_hashes[post_id]
                
                # 마지막 갱신 시간 업데이트
                content_cache["last_updated"] = datetime.now().isoformat()
                self._last_refresh = current_time
                
                print(f"콘텐츠 캐시 갱신 완료 (카테고리: {len(content_cache['categories'])}, 포스트: {len(content_cache['posts'])})")
            except Exception as e:
                print(f"콘텐츠 캐시 갱신 오류: {e}")
                raise
    
    def get_categories(self) -> List[dict]:
        """모든 카테고리 목록 반환"""
        return content_cache["categories"]
    
    def get_category_by_path(self, path: str) -> Optional[dict]:
        """경로로 카테고리 찾기"""
        def find_category(categories, target_path):
            for category in categories:
                if category["type"] == "directory" and category["path"] == target_path:
                    return category
                elif category["type"] == "directory" and "children" in category:
                    result = find_category(category["children"], target_path)
                    if result:
                        return result
            return None
        
        return find_category(content_cache["categories"], path)
    
    def get_posts_by_category(self, category_path: str) -> List[dict]:
        """카테고리 경로로 포스트 목록 찾기"""
        result = []
        
        for post_id, post in content_cache["posts"].items():
            if post["category"] == category_path or post["category"].startswith(f"{category_path}/"):
                result.append(post)
        
        return result
    
    def get_post_by_path(self, post_path: str) -> Optional[dict]:
        """경로로 포스트 찾기 (최적화된 버전)"""
        if post_path in content_cache["posts"]:
            return content_cache["posts"][post_path]
        
        normalized_path = post_path.lstrip("/")
        return content_cache["posts"].get(normalized_path)
    
    def get_recent_posts(self, limit: int = 5) -> List[dict]:
        """최근 포스트 목록 반환 (최적화된 버전)"""
        posts = list(content_cache["posts"].values())
        return sorted(posts, key=lambda x: x.get("updated_at", ""), reverse=True)[:limit]

    def get_post_file_path(self, post_id: str) -> Optional[Path]:
        """포스트 ID로 파일 경로 반환"""
        try:
            # post_id가 이미 전체 경로인 경우
            if post_id in content_cache["posts"]:
                post = content_cache["posts"][post_id]
                return self.data_dir / f"{post['path']}.md"
            
            # post_id가 파일명만인 경우
            for post in content_cache["posts"].values():
                if post["id"] == post_id:
                    return self.data_dir / f"{post['path']}.md"
            
            return None
        except Exception as e:
            print(f"포스트 파일 경로 조회 중 오류 발생: {e}")
            return None

    def get_all_posts(self) -> List[Dict]:
        """
        모든 포스트의 기본 정보를 반환합니다.
        sitemap.xml 생성에 필요한 최소한의 데이터만 포함합니다.
        """
        try:
            # 캐시된 포스트 목록에서 필요한 필드만 추출
            posts = []
            for post in content_cache["posts"].values():
                posts.append({
                    "id": post["id"],
                    "path": post["path"],
                    "updated_at": post["updated_at"],
                    "created_at": post.get("created_at", post["updated_at"])
                })
            return posts
        except Exception as e:
            logger.error(f"포스트 목록 조회 중 오류 발생: {str(e)}")
            raise


# 싱글톤 인스턴스
content_service = ContentService()

# 비동기 초기화 함수
async def initialize_content_service():
    """콘텐츠 서비스 초기화 및 시작"""
    # 콘텐츠 캐시 초기 로드
    await content_service.refresh_content_cache()
    
    # 파일 변경 감지 시작
    await content_service.start_file_watcher()

# 종료 함수
async def shutdown_content_service():
    """콘텐츠 서비스 종료"""
    await content_service.stop_file_watcher()

def get_file_hash(content: str) -> str:
    """파일 내용의 해시값 계산"""
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def extract_markdown_title(content: str) -> Tuple[str, str]:
    """마크다운 파일에서 제목과 설명 추출"""
    title = "Untitled"
    description = ""
    
    # 제목 추출 (# 제목 형식)
    title_match = re.search(r'^\s*#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
    
    # 설명 추출 (제목 다음 첫 단락)
    desc_match = re.search(r'^\s*#\s+.+\n+(.+?)(\n\n|\n#|$)', content, re.DOTALL | re.MULTILINE)
    if desc_match:
        description = desc_match.group(1).strip()
    
    return title, description

def scan_directory(directory: str, base_path: str = "", include_content: bool = False) -> List[Any]:
    """디렉토리를 스캔하여 카테고리 및 파일 트리 생성"""
    result = []
    full_path = os.path.join(settings.CONTENT_DIR, directory)
    
    try:
        items = sorted(os.listdir(full_path))
        
        for item in items:
            item_path = os.path.join(directory, item)
            full_item_path = os.path.join(settings.CONTENT_DIR, item_path)
            rel_path = os.path.join(base_path, item) if base_path else item
            
            # 숨김 파일 무시
            if item.startswith('.'):
                continue
                
            if os.path.isdir(full_item_path):
                # 디렉토리인 경우
                category_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, item_path))
                category = CategoryItem(
                    id=category_id,
                    name=item,
                    path=rel_path.replace('\\', '/'),
                    children=scan_directory(item_path, rel_path, include_content)
                )
                result.append(category)
            elif item.endswith('.md'):
                # 마크다운 파일인 경우
                file_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, item_path))
                
                # 파일 정보
                file_info = {
                    "id": file_id,
                    "name": item[:-3],  # .md 제거
                    "path": rel_path.replace('\\', '/')[:-3],  # 경로에서 .md 제거
                    "type": "file",
                    "updated_at": datetime.fromtimestamp(os.path.getmtime(full_item_path))
                }
                
                # 제목과 설명 추출 (파일 내용이 필요한 경우)
                if include_content:
                    with open(full_item_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        title, description = extract_markdown_title(content)
                        file_info["title"] = title
                        file_info["description"] = description
                        
                        if include_content:
                            file_info["content"] = content
                
                result.append(FileItem(**file_info))
    except Exception as e:
        print(f"디렉토리 스캔 중 오류 발생: {str(e)}")
        
    return result

def build_category_tree(rebuild: bool = False) -> List[CategoryItem]:
    """카테고리 트리 구축 (캐시에서 로드 또는 재구축)"""
    if not rebuild and os.path.exists(META_CACHE_FILE):
        try:
            with open(META_CACHE_FILE, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                return [CategoryItem.model_validate(item) for item in cache_data]
        except Exception as e:
            print(f"캐시 로드 중 오류 발생: {str(e)}")
    
    # 캐시가 없거나 재구축이 필요한 경우
    categories = scan_directory("", "", include_content=True)
    
    # 캐시 저장
    try:
        os.makedirs(os.path.dirname(META_CACHE_FILE), exist_ok=True)
        with open(META_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump([category.model_dump() for category in categories], f, indent=2, default=str)
    except Exception as e:
        print(f"캐시 저장 중 오류 발생: {str(e)}")
    
    return categories

def get_posts_in_category(category_path: str) -> List[Dict]:
    """특정 카테고리의 모든 포스트 가져오기"""
    categories = build_category_tree()
    
    # 카테고리 찾기
    target_category = None
    parts = category_path.split('/')
    current_categories = categories
    
    for part in parts:
        if not part:
            continue
            
        found = False
        for category in current_categories:
            if category.type == "directory" and category.name == part:
                current_categories = category.children
                target_category = category
                found = True
                break
        
        if not found:
            return []
    
    # 파일만 필터링
    if target_category:
        files = [item for item in current_categories if item.type == "file"]
    else:
        # 루트 카테고리인 경우
        files = [item for item in categories if item.type == "file"]
    
    # 결과 변환
    result = []
    for file in files:
        post_data = {
            "id": file.id,
            "path": file.path,
            "title": getattr(file, "title", file.name),
            "description": getattr(file, "description", ""),
            "updated_at": file.updated_at
        }
        result.append(post_data)
    
    # 업데이트 날짜 기준 내림차순 정렬
    return sorted(result, key=lambda x: x["updated_at"], reverse=True)

def get_recent_posts(limit: int = 5) -> List[Dict]:
    """최근 업데이트된 포스트 가져오기"""
    categories = build_category_tree()
    
    # 모든 파일 추출
    all_files = []
    
    def collect_files(items):
        for item in items:
            if item.type == "file":
                all_files.append(item)
            elif item.type == "directory" and hasattr(item, "children"):
                collect_files(item.children)
    
    collect_files(categories)
    
    # 날짜순 정렬 및 제한
    sorted_files = sorted(all_files, key=lambda x: x.updated_at, reverse=True)[:limit]
    
    # 결과 변환
    result = []
    for file in sorted_files:
        post_data = {
            "id": file.id,
            "path": file.path,
            "title": getattr(file, "title", file.name),
            "description": getattr(file, "description", ""),
            "updated_at": file.updated_at
        }
        result.append(post_data)
    
    return result

def get_post_by_path(post_path: str) -> Optional[Post]:
    """경로로 포스트 가져오기"""
    # 파일 경로 구성
    full_path = os.path.join(settings.CONTENT_DIR, f"{post_path}.md")
    
    if not os.path.exists(full_path):
        return None
    
    # 파일 읽기
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 제목, 설명 추출
    title, description = extract_markdown_title(content)
    
    # 카테고리 경로 추출
    category_path = os.path.dirname(post_path).replace('\\', '/')
    
    # 포스트 데이터 구성
    post_data = {
        "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, post_path)),
        "path": post_path,
        "title": title,
        "content": content,
        "description": description,
        "category": category_path,
        "created_at": datetime.fromtimestamp(os.path.getctime(full_path)),
        "updated_at": datetime.fromtimestamp(os.path.getmtime(full_path))
    }
    
    # 이전/다음 포스트 정보 추가
    prev_post, next_post = get_adjacent_posts(post_path)
    if prev_post:
        post_data["prev_post"] = prev_post
    if next_post:
        post_data["next_post"] = next_post
    
    return Post(**post_data)

def get_adjacent_posts(post_path: str) -> Tuple[Optional[Dict], Optional[Dict]]:
    """이전/다음 포스트 가져오기"""
    category_path = os.path.dirname(post_path)
    posts = get_posts_in_category(category_path)
    
    # 날짜순 정렬 (최신순)
    posts = sorted(posts, key=lambda x: x["updated_at"], reverse=True)
    
    # 현재 포스트 인덱스 찾기
    current_index = -1
    for i, post in enumerate(posts):
        if post["path"] == post_path:
            current_index = i
            break
    
    if current_index == -1:
        return None, None
    
    # 이전/다음 포스트
    prev_post = None
    next_post = None
    
    if current_index > 0:
        prev_post = {
            "path": posts[current_index - 1]["path"],
            "title": posts[current_index - 1]["title"]
        }
    
    if current_index < len(posts) - 1:
        next_post = {
            "path": posts[current_index + 1]["path"],
            "title": posts[current_index + 1]["title"]
        }
    
    return prev_post, next_post

def create_post(post_data: PostCreate, author: str) -> Post:
    """새 포스트 생성"""
    # 경로 생성
    if post_data.path:
        post_path = post_data.path
    else:
        # 파일명 생성 (제목 기반)
        slug = re.sub(r'[^\w\s-]', '', post_data.title.lower())
        slug = re.sub(r'[\s_-]+', '-', slug).strip('-')
        category_dir = post_data.category if post_data.category else ""
        post_path = os.path.join(category_dir, slug).replace('\\', '/')
    
    # 파일 경로 구성
    full_path = os.path.join(settings.CONTENT_DIR, f"{post_path}.md")
    
    # 디렉토리 생성
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    # 기존 파일 체크
    if os.path.exists(full_path):
        raise ValueError("이미 존재하는 경로입니다.")
    
    # 파일 작성
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(post_data.content)
    
    # 캐시 재구축
    build_category_tree(rebuild=True)
    
    # 생성된 포스트 반환
    return get_post_by_path(post_path)

def update_post(post_path: str, post_data: PostUpdate) -> Optional[Post]:
    """포스트 업데이트"""
    post = get_post_by_path(post_path)
    if not post:
        return None
    
    # 기존 파일 경로
    full_path = os.path.join(settings.CONTENT_DIR, f"{post_path}.md")
    
    # 카테고리 변경 시
    new_path = post_path
    if post_data.category is not None and post_data.category != post.category:
        # 새 경로 계산
        file_name = os.path.basename(post_path)
        new_path = os.path.join(post_data.category, file_name).replace('\\', '/')
        new_full_path = os.path.join(settings.CONTENT_DIR, f"{new_path}.md")
        
        # 디렉토리 생성
        os.makedirs(os.path.dirname(new_full_path), exist_ok=True)
    else:
        new_full_path = full_path
    
    # 내용 업데이트
    content = post.content
    if post_data.content is not None:
        content = post_data.content
    
    # 제목 업데이트 (내용의 첫 줄 "#" 부분)
    if post_data.title is not None:
        lines = content.split('\n')
        title_found = False
        
        for i, line in enumerate(lines):
            if line.strip().startswith('#'):
                lines[i] = f"# {post_data.title}"
                title_found = True
                break
        
        if not title_found:
            # 제목이 없으면 맨 위에 추가
            lines.insert(0, f"# {post_data.title}")
        
        content = '\n'.join(lines)
    
    # 파일 쓰기
    with open(new_full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 파일 경로가 변경되었으면 기존 파일 삭제
    if new_full_path != full_path:
        os.remove(full_path)
    
    # 캐시 재구축
    build_category_tree(rebuild=True)
    
    # 업데이트된 포스트 반환
    return get_post_by_path(new_path)

def delete_post(post_path: str) -> bool:
    """포스트 삭제"""
    full_path = os.path.join(settings.CONTENT_DIR, f"{post_path}.md")
    
    if not os.path.exists(full_path):
        return False
    
    # 파일 삭제
    os.remove(full_path)
    
    # 캐시 재구축
    build_category_tree(rebuild=True)
    
    return True 