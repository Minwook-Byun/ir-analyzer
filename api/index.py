"""
MYSC IR Platform - Single Route Handler
Hobby plan compatible version with Linear design
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
import pathlib

# 프로젝트 루트 경로 설정
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
PUBLIC_DIR = BASE_DIR / "public"

app = FastAPI(title="MYSC IR Platform", version="3.0.0")

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def handle_all_routes(request: Request, path: str = ""):
    """단일 핸들러로 모든 요청 처리"""
    method = request.method
    
    # CORS 처리
    if method == "OPTIONS":
        return JSONResponse(
            content={}, 
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )
    
    # 홈페이지
    if path == "" or path == "index.html":
        index_path = PUBLIC_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path, media_type="text/html")
        return HTMLResponse("""
        <html><head><title>MYSC IR Platform</title></head>
        <body><h1>MYSC IR Platform</h1><p>Professional Investment Analysis</p></body>
        </html>
        """)
    
    # 정적 파일
    if path.startswith("static/"):
        file_path = PUBLIC_DIR / path
        if file_path.exists():
            # MIME 타입 설정
            if path.endswith('.css'):
                return FileResponse(file_path, media_type="text/css")
            elif path.endswith('.js'):
                return FileResponse(file_path, media_type="application/javascript")
            else:
                return FileResponse(file_path)
    
    # API 엔드포인트들
    if path == "health":
        return {"status": "healthy", "platform": "MYSC IR Platform"}
    
    if path == "api/config":
        return {
            "platform": "MYSC IR Platform",
            "version": "3.0.0", 
            "features": ["50MB_Upload", "Linear_Design"],
            "ready": True
        }
    
    if path == "api/analyze" and method == "POST":
        return {
            "success": True,
            "message": "Analysis started", 
            "analysis_id": "demo_123"
        }
    
    # 404 처리
    return JSONResponse(
        {"error": "Not found", "path": path}, 
        status_code=404,
        headers={"Access-Control-Allow-Origin": "*"}
    )