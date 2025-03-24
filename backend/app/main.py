from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import uvicorn

from app.routers import categories, posts, auth
from app.core.config import settings
from app.services.content_service import initialize_content_service, shutdown_content_service

app = FastAPI(title="GilliLab IT Blog API")

# CORS 설정 (개발 환경용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 구체적인 출처 지정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(categories.router, prefix="/api", tags=["categories"])
app.include_router(posts.router, prefix="/api", tags=["posts"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

# 시작 이벤트 핸들러 - 애플리케이션 시작 시 실행
@app.on_event("startup")
async def startup_event():
    # 콘텐츠 서비스 초기화 및 파일 변경 감지 시작
    await initialize_content_service()

# 종료 이벤트 핸들러 - 애플리케이션 종료 시 실행
@app.on_event("shutdown")
async def shutdown_event():
    # 콘텐츠 서비스와 파일 변경 감지 종료
    await shutdown_content_service()

# 정적 파일 설정 (선택)
if os.path.exists("../frontend/dist"):
    app.mount("/", StaticFiles(directory="../frontend/dist", html=True), name="static")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 