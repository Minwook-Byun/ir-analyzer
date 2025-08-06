"""
MYSC IR Platform - Optimized Single Function
Linear-style design with Vercel Blob 50MB support
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import pathlib
import os
import hashlib
import secrets
from datetime import datetime

# 프로젝트 루트 경로 설정
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
PUBLIC_DIR = BASE_DIR / "public"

app = FastAPI(
    title="MYSC IR Platform", 
    version="3.0.0",
    description="Professional IR analysis with Linear-style design"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 마운트
if (PUBLIC_DIR / "static").exists():
    app.mount("/static", StaticFiles(directory=str(PUBLIC_DIR / "static")), name="static")

@app.get("/")
async def get_homepage():
    """메인 홈페이지"""
    index_path = PUBLIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path, media_type="text/html")
    return HTMLResponse(content="""
    <html><head><title>MYSC IR 분석 플랫폼</title></head>
    <body>
        <h1>🚀 MYSC IR 분석 플랫폼</h1>
        <p>✅ 50MB+ 파일 업로드 지원 (Vercel Blob)</p>
        <p>✅ 투자심사보고서 AI 분석</p>
        <p>✅ 엔터프라이즈급 보안</p>
    </body>
    </html>
    """)

@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {"status": "healthy", "platform": "MYSC IR Platform", "version": "3.0.0"}

# ========== 통합 분석 엔드포인트 ==========
@app.post("/api/analyze")
async def analyze_ir_files(
    company_name: str = Form(...),
    files: list[UploadFile] = File(None),
    blob_url: str = Form(None)
):
    """통합 IR 분석 - 서버 업로드 또는 Blob 업로드 지원"""
    if not company_name or len(company_name.strip()) < 2:
        raise HTTPException(status_code=400, detail="회사명을 입력해주세요")
    
    # Blob 업로드 방식
    if blob_url:
        return {
            "success": True,
            "message": f"{company_name} IR 분석 시작 (Blob)",
            "company_name": company_name,
            "upload_method": "blob",
            "analysis_id": secrets.token_hex(8)
        }
    
    # 서버 업로드 방식 (4.5MB 제한)
    if not files:
        raise HTTPException(status_code=400, detail="파일을 선택해주세요")
    
    total_size = sum(len(await file.read()) for file in files)
    if total_size > 4.5 * 1024 * 1024:
        return {
            "success": False,
            "error": "file_too_large",
            "redirect_to_blob": True,
            "message": "50MB 이상 파일은 Blob 업로드를 사용하세요"
        }
    
    return {
        "success": True,
        "message": f"{company_name} IR 분석 시작",
        "company_name": company_name,
        "upload_method": "server",
        "analysis_id": secrets.token_hex(8)
    }

# ========== Blob 지원 (통합) ==========
@app.post("/api/blob/token")
async def generate_upload_token(
    filename: str = Form(...),
    file_size: int = Form(...),
    company_name: str = Form(...)
):
    """50MB Blob 업로드 토큰 생성"""
    # 검증
    if file_size > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="파일이 50MB를 초과합니다")
    
    if not company_name.strip():
        raise HTTPException(status_code=400, detail="회사명을 입력해주세요")
    
    # 토큰 생성
    token = {
        "session_id": secrets.token_hex(8),
        "filename": filename,
        "file_size": file_size,
        "company_name": company_name,
        "timestamp": datetime.utcnow().isoformat(),
        "expires_in": 1800  # 30분
    }
    
    return {
        "success": True,
        "token": token,
        "upload_url": f"/api/blob/upload?token={token['session_id']}",
        "expires_in": 1800
    }

@app.get("/api/config")
async def get_platform_config():
    """플랫폼 설정 및 상태"""
    return {
        "platform": "MYSC IR Platform",
        "version": "3.0.0",
        "design": "Linear-style",
        "blob_support": True,
        "max_file_size": "50MB",
        "features": ["50MB_Upload", "Linear_Design", "Dark_Mode"],
        "ready": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)