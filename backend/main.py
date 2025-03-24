from app.main import app

# FastAPI 앱을 가져와서 재내보냅니다.
# 이렇게 하면 'uv run fastapi dev' 명령이 이 파일을 찾아서 app 객체를 인식할 수 있습니다.

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
