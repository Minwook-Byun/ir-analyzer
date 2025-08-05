# Force redeployment by adding a comment
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import requests
import google.generativeai as genai
import os
from dotenv import load_dotenv
import re
from typing import Optional, List
from datetime import datetime, timedelta
import pathlib
import jwt
import secrets
import asyncio
from fastapi import BackgroundTasks

# 현재 파일의 경로를 기준으로 프로젝트 루트 경로 설정
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent  # api 폴더의 상위 폴더
FRONTEND_DIR = BASE_DIR / "frontend"

# 환경변수 로드
load_dotenv()

app = FastAPI(title="IR Analyzer", version="1.0.0")

# JWT 설정
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_HOURS = 24

# Security scheme
security = HTTPBearer(auto_error=False)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 마운트 - public 폴더 사용
PUBLIC_DIR = BASE_DIR / "public"
try:
    if (PUBLIC_DIR / "static").exists():
        app.mount("/static", StaticFiles(directory=PUBLIC_DIR / "static"), name="static")
    else:
        print(f"⚠️ Static directory not found: {PUBLIC_DIR / 'static'}")
except Exception as e:
    print(f"⚠️ Failed to mount static files: {e}")

# JSON 데이터 파일 서빙을 위한 루트 정적 파일 마운트

@app.get("/")
async def get_homepage():
    """메인 홈페이지 반환"""
    try:
        index_path = PUBLIC_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path, media_type="text/html")
        else:
            return HTMLResponse(content="""
            <html><head><title>IR Analyzer</title></head>
            <body><h1>IR Analyzer</h1><p>Investment Report Analysis Platform</p></body>
            </html>
            """)
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error loading homepage: {str(e)}</h1>", status_code=500)

@app.get("/health")
async def health_check():
    """서버 상태 확인용 간단한 엔드포인트"""
    return {"status": "healthy", "message": "IR Analyzer is running"}

@app.get("/impact-report-data.json")
async def get_impact_report_data():
    """임팩트 리포트 데모 데이터 반환"""
    json_path = BASE_DIR / "impact-report-data.json"
    if json_path.exists():
        return FileResponse(json_path, media_type="application/json")
    else:
        raise HTTPException(status_code=404, detail="Demo data not found")


# Gemini API 설정
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 요청 모델
class IRAnalysisRequest(BaseModel):
    company_name: str
    ir_url: str
    analysis_type: Optional[str] = "investment_report"

class JandiWebhookRequest(BaseModel):
    text: str
    writer_name: Optional[str] = "Unknown"

class LoginRequest(BaseModel):
    api_key: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

# Vercel Blob 관련 모델들
class BlobUploadRequest(BaseModel):
    company_name: str
    analysis_type: Optional[str] = "investment_report"

class BlobUploadResponse(BaseModel):
    success: bool
    job_id: str
    message: str
    upload_url: Optional[str] = None
    
class BlobAnalysisStatus(BaseModel):
    job_id: str
    status: str  # 'pending', 'processing', 'completed', 'failed'
    progress: int
    message: str
    result: Optional[dict] = None
    error: Optional[str] = None

# JWT 토큰 생성 함수
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=JWT_ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

# JWT 토큰 검증 함수
def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="인증이 필요합니다. 로그인해주세요.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        api_key: str = payload.get("api_key")
        if api_key is None:
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
        return api_key
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="토큰이 만료되었습니다. 다시 로그인해주세요.")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

# Gemini API 키 검증 함수
def verify_gemini_api_key(api_key: str) -> bool:
    # 개발 모드에서는 테스트 키 허용
    if os.getenv("ENVIRONMENT") == "development" and api_key == "test_gemini_api_key_for_development":
        print("[DEV MODE] Using test API key")
        return True
    
    try:
        # 임시로 Gemini API 설정하여 유효성 검증
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        # 간단한 테스트 요청
        response = model.generate_content("Hello")
        return True
    except Exception as e:
        print(f"API 키 검증 실패: {str(e)}")
        return False

@app.get("/", response_class=HTMLResponse)
async def get_homepage():
    """메인 홈페이지 반환"""
    index_path = PUBLIC_DIR / "index.html"
    if not index_path.is_file():
        return HTMLResponse(content="<h1>Frontend file not found</h1>", status_code=404)
    return HTMLResponse(content=index_path.read_text(encoding="utf-8"))

@app.get("/login", response_class=HTMLResponse)
async def get_login_page():
    """로그인 페이지 반환"""
    html_path = PUBLIC_DIR / "login.html"
    if html_path.exists():
        return FileResponse(html_path, media_type="text/html")
    else:
        return HTMLResponse("<h1>Login</h1><p>Login page not found</p>")

@app.post("/api/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """API 키로 로그인하여 JWT 토큰 발급"""
    try:
        # Gemini API 키 유효성 검증
        if not verify_gemini_api_key(request.api_key):
            raise HTTPException(
                status_code=401, 
                detail="유효하지 않은 Gemini API 키입니다. API 키를 확인해주세요."
            )
        
        # JWT 토큰 생성
        access_token = create_access_token(
            data={"api_key": request.api_key, "sub": "user"}
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=JWT_ACCESS_TOKEN_EXPIRE_HOURS * 3600  # 초 단위
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"로그인 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="로그인 처리 중 오류가 발생했습니다.")

@app.post("/api/logout")
async def logout():
    """로그아웃 (클라이언트에서 토큰 삭제)"""
    return {"message": "로그아웃되었습니다. 토큰을 삭제해주세요."}

class TheoryOfChangeRequest(BaseModel):
    organization_name: str
    impact_focus: Optional[str] = None

@app.post("/api/generate-theory-of-change")
async def generate_theory_of_change(
    request: TheoryOfChangeRequest,
    api_key: str = Depends(verify_token)
):
    """변화이론(Theory of Change) 동적 생성 API"""
    try:
        print(f"🎯 변화이론 생성 요청: {request.organization_name}")
        
        # theory_of_change 모듈 import
        import sys
        sys.path.append(str(BASE_DIR))  # 프로젝트 루트를 Python 경로에 추가
        from theory_of_change import TheoryOfChangeOrchestrator
        
        # 오케스트레이터 초기화 및 실행
        orchestrator = TheoryOfChangeOrchestrator(api_key)
        theory_data = await orchestrator.generate_theory_of_change(
            organization_name=request.organization_name,
            impact_focus=request.impact_focus
        )
        
        print(f"✅ 변화이론 생성 완료: {request.organization_name}")
        
        return {
            "success": True,
            "organization_name": request.organization_name,
            "theory_data": theory_data,
            "generated_by": "multi-agent-system",
            "agents_used": [
                "context-analyzer", "user-insight", "strategy-designer", 
                "validator", "storyteller"
            ],
            "generated_at": datetime.now().isoformat(),
            "message": "변화이론이 성공적으로 생성되었습니다."
        }
        
    except Exception as e:
        print(f"❌ 변화이론 생성 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"변화이론 생성 중 오류 발생: {str(e)}")

# ===== VERCEL BLOB 통합 API 엔드포인트들 =====

# 글로벌 작업 상태 저장소 (실제 프로덕션에서는 Redis 등 사용)
job_storage = {}


# === TEST ENDPOINT FOR DEBUGGING ===
@app.post("/api/test/upload")
async def test_upload_endpoint(
    files: List[UploadFile] = File(...),
    company_name: str = Form(...),
    api_key: str = Depends(verify_token)
):
    """Simple test endpoint to isolate 500 error"""
    try:
        print(f"[TEST] Received {len(files)} files for {company_name}")
        
        file_info = []
        for file in files:
            file_info.append({
                "filename": file.filename,
                "content_type": file.content_type,
                "size": len(await file.read()) if hasattr(file, 'read') else 0
            })
            # Reset file pointer if we read it
            if hasattr(file, 'seek'):
                await file.seek(0)
        
        return {
            "success": True,
            "message": f"Test successful - received {len(files)} files",
            "files": file_info,
            "company_name": company_name
        }
        
    except Exception as e:
        print(f"[ERROR] Test endpoint failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Test endpoint error: {str(e)}")

@app.post("/api/debug/upload")
async def debug_upload_endpoint(
    files: List[UploadFile] = File(...),
    company_name: str = Form(...)
):
    """
    BRAND NEW ENDPOINT FOR DEBUGGING
    """
    print(f"[DEBUG] New debug endpoint called")
    print(f"[DEBUG] Company: {company_name}")
    print(f"[DEBUG] Files: {len(files)}")
    
    return {
        "success": True,
        "message": "New debug endpoint works!"
    }

@app.post("/api/blob/upload")
async def blob_upload_endpoint(
    files: List[UploadFile] = File(...),
    company_name: str = Form(...)
):
    """
    ULTRA SIMPLIFIED FOR DEBUGGING - No dependencies, no response model
    """
    try:
        print(f"[DEBUG] Ultra simplified endpoint called")
        print(f"[DEBUG] Company: {company_name}")
        print(f"[DEBUG] Files: {len(files)}")
        
        return {
            "success": True,
            "job_id": "test-job-id", 
            "message": "Ultra simplified test successful"
        }
        
    except Exception as e:
        print(f"[ERROR] Ultra simplified endpoint failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@app.get("/api/blob/status/{job_id}", response_model=BlobAnalysisStatus)
async def get_blob_job_status(job_id: str):
    """
    작업 상태 조회 엔드포인트
    
    실시간 진행률과 상태를 제공합니다.
    """
    if job_id not in job_storage:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다.")
    
    job_data = job_storage[job_id]
    
    return BlobAnalysisStatus(
        job_id=job_id,
        status=job_data["status"],
        progress=job_data["progress"],
        message=job_data["message"],
        result=job_data.get("result"),
        error=job_data.get("error")
    )

async def process_blob_files_background(
    job_id: str, 
    files: List[UploadFile], 
    company_name: str, 
    api_key: str
):
    """
    백그라운드에서 Blob 파일 처리
    
    진행률을 실시간으로 업데이트하며 사용자 친화적인 피드백 제공
    """
    try:
        import sys
        sys.path.append(str(BASE_DIR))
        from blob_processor import blob_processor
        
        def update_progress(stage: str, progress: int, message: str):
            """진행률 업데이트 콜백"""
            job_storage[job_id].update({
                "status": "processing",
                "progress": progress,
                "message": message,
                "stage": stage
            })
            print(f"[PROGRESS] [{job_id}] {stage}: {progress}% - {message}")
        
        # 1단계: 파일 검증 및 Blob 업로드
        update_progress("validation", 5, "파일 검증 중...")
        
        blob_urls = []
        total_files = len(files)
        
        for i, file in enumerate(files):
            file_progress_base = (i / total_files) * 40  # 업로드는 전체의 40%
            
            # 파일 데이터 읽기
            file_content = await file.read()
            
            update_progress(
                "blob-upload", 
                int(file_progress_base + 5), 
                f"파일 업로드 중... ({i+1}/{total_files}) {file.filename}"
            )
            
            # Vercel Blob에 업로드
            upload_result = await blob_processor.upload_to_blob(
                file_content, 
                file.filename,
                lambda stage, prog, msg: update_progress(
                    stage, 
                    int(file_progress_base + (prog * 0.35)), 
                    f"{msg} ({i+1}/{total_files})"
                )
            )
            
            if upload_result["success"]:
                blob_urls.append({
                    "blob_url": upload_result["blob_url"],
                    "filename": file.filename,
                    "metadata": upload_result["metadata"]
                })
                print(f"[SUCCESS] [{job_id}] Blob 업로드 성공: {file.filename}")
            else:
                raise Exception(f"파일 업로드 실패: {file.filename} - {upload_result['error']}")
        
        # 2단계: 파일 처리 및 텍스트 추출
        update_progress("file-processing", 45, "파일 내용 분석 중...")
        
        combined_content = []
        for i, blob_info in enumerate(blob_urls):
            file_progress_base = 45 + (i / total_files) * 30  # 처리는 30%
            
            update_progress(
                "file-processing",
                int(file_progress_base),
                f"파일 분석 중... ({i+1}/{total_files}) {blob_info['filename']}"
            )
            
            # Blob에서 파일 처리
            ir_summary = await blob_processor.process_blob_file(
                blob_info["blob_url"],
                blob_info["filename"],
                lambda stage, prog, msg: update_progress(
                    stage,
                    int(file_progress_base + (prog * 0.3)),
                    f"{msg} ({i+1}/{total_files})"
                )
            )
            
            combined_content.append(f"=== {blob_info['filename']} ===\n{ir_summary}\n")
        
        # 3단계: AI 분석 및 보고서 생성
        update_progress("ai-analysis", 75, "AI가 투자심사보고서를 생성하고 있습니다...")
        
        combined_ir_summary = "\n".join(combined_content)
        
        # 투자심사보고서 생성 (기존 함수 재사용)
        if os.getenv("ENVIRONMENT") == "development" and api_key == "test_gemini_api_key_for_development":
            # 개발 모드에서는 Mock 투자심사보고서 생성
            investment_report = f"""
# Mock 투자심사보고서 - {company_name}

## Executive Summary

**투자 논지**: {company_name}는 혁신적인 기술과 강력한 시장 포지션을 통해 지속 가능한 성장을 실현할 것으로 예상됩니다.

## 1. 투자 개요

### 1.1. 기업 개요
- **회사명**: {company_name}
- **사업 분야**: Mock IR 분석 기반
- **설립년도**: 2020년 (추정)

### 1.2. 투자 조건
- **투자 금액**: 10억원 (제안)
- **지분율**: 15%
- **투자 형태**: 시리즈 A

### 1.3. 손익 추정 및 수익성
- **예상 매출 (2025)**: 50억원
- **예상 EBITDA**: 10억원
- **IRR**: 25% (추정)

## 2. 기업 현황

Mock 데이터를 바탕으로 분석한 결과, 해당 기업은 안정적인 성장 궤도에 있습니다.

## 7. 종합 결론

**투자 권고**: 적극 검토 권장

위와 같은 분석을 바탕으로, {company_name}에 대한 투자를 긍정적으로 검토할 것을 제안합니다.

---
*이 보고서는 개발 모드에서 생성된 Mock 데이터를 포함합니다.*
"""
        else:
            investment_report = await generate_investment_report(
                ir_summary=combined_ir_summary,
                company_name=company_name,
                api_key=api_key
            )
        
        # 4단계: 완료
        update_progress("completed", 100, "투자심사보고서 생성 완료! 🎉")
        
        # 최종 결과 저장
        job_storage[job_id].update({
            "status": "completed",
            "progress": 100,
            "message": "분석이 완료되었습니다!",
            "result": {
                "company_name": company_name,
                "investment_report": investment_report,
                "source_files": [blob_info["filename"] for blob_info in blob_urls],
                "blob_info": blob_urls,
                "file_count": len(files),
                "report_type": "투자심사보고서 초안 (Vercel Blob)",
                "completed_at": datetime.now().isoformat()
            }
        })
        
        print(f"🎉 [{job_id}] Blob 파일 처리 완전 완료!")
        
        # 선택사항: Blob 정리 (24시간 후 자동 삭제 등)
        # 실제 프로덕션에서는 스케줄러 사용
        
    except Exception as e:
        print(f"[ERROR] [{job_id}] Blob 백그라운드 처리 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        
        job_storage[job_id].update({
            "status": "failed",
            "progress": 0,
            "message": f"처리 중 오류가 발생했습니다: {str(e)}",
            "error": str(e)
        })

@app.post("/api/analyze-ir-files")
async def analyze_ir_files(
    files: List[UploadFile] = File(...),
    company_name: str = Form(...),
    api_key: str = Depends(verify_token)
):
    """다중 파일 업로드를 통한 IR 자료 분석"""
    try:
        print(f"📎 다중 파일 업로드 분석 시작: {company_name} - {len(files)}개 파일")
        
        # 입력 데이터 검증 로깅
        print(f"🔍 Request validation - Company: {company_name}, Files count: {len(files)}")
        for i, file in enumerate(files):
            print(f"  File {i+1}: {file.filename}, Content-Type: {file.content_type}")
        
        # 빈 파일 리스트 검증
        if not files or len(files) == 0:
            raise HTTPException(status_code=400, detail="업로드할 파일을 선택해주세요.")
        
        # company_name 검증
        if not company_name or company_name.strip() == "":
            raise HTTPException(status_code=400, detail="회사명을 입력해주세요.")
        
        combined_content = []
        total_size = 0
        
        for file in files:
            # 파일명 존재 검증
            if not file.filename:
                raise HTTPException(status_code=400, detail="파일명이 없는 파일이 있습니다.")
            
            # 파일 형식 검증
            if not file.filename.lower().endswith(('.pdf', '.xlsx', '.xls', '.docx', '.doc')):
                print(f"[ERROR] 지원하지 않는 파일 형식: {file.filename}")
                raise HTTPException(status_code=400, detail=f"지원하지 않는 파일 형식입니다: {file.filename}. 지원 형식: PDF, Excel, Word")
            
            # 개별 파일 크기 확인
            file_content = await file.read()
            file_size = len(file_content)
            total_size += file_size
            
            print(f"📄 파일 읽기 완료: {file.filename} ({file_size:,} bytes)")
            
            # 빈 파일 검증
            if file_size == 0:
                raise HTTPException(status_code=400, detail=f"빈 파일입니다: {file.filename}")
            
            # 개별 파일 크기 제한 (4.5MB)
            if file_size > 4.5 * 1024 * 1024:
                raise HTTPException(status_code=400, detail=f"파일 크기가 너무 큽니다: {file.filename} ({file_size:,} bytes). 최대 4.5MB까지 허용됩니다.")
            
            # 파일 처리
            ir_summary = await process_uploaded_file(file_content, file.filename)
            combined_content.append(f"=== {file.filename} ===\n{ir_summary}\n")
            print(f"📄 파일 처리 완료: {file.filename}")
        
        # 전체 파일 크기 검증 (4.5MB 제한 - Vercel 서버리스 함수 최적화)
        print(f"[INFO] 전체 파일 크기: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")
        if total_size > 4.5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"전체 파일 크기가 제한을 초과했습니다: {total_size:,} bytes. 최대 4.5MB까지 허용됩니다.")
        
        # 모든 파일 내용을 결합
        combined_ir_summary = "\n".join(combined_content)
        
        # 투자심사보고서 생성
        investment_report = await generate_investment_report(
            ir_summary=combined_ir_summary,
            company_name=company_name,
            api_key=api_key
        )
        print(f"📋 투자심사보고서 생성 완료")
        
        return {
            "success": True,
            "company_name": company_name,
            "investment_report": investment_report,
            "source_files": [file.filename for file in files],
            "file_count": len(files),
            "report_type": "투자심사보고서 초안 (다중 파일)"
        }
        
    except HTTPException as he:
        print(f"[ERROR] HTTP 검증 오류 (400): {he.detail}")
        raise
    except Exception as e:
        print(f"[ERROR] 다중 파일 분석 중 예상치 못한 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"다중 파일 분석 중 오류 발생: {str(e)}")

@app.post("/api/analyze-ir-file")
async def analyze_ir_file(
    file: UploadFile = File(...),
    company_name: str = Form(...),
    api_key: str = Depends(verify_token)
):
    """파일 업로드를 통한 IR 자료 분석"""
    try:
        print(f"📎 파일 업로드 분석 시작: {company_name} - {file.filename}")
        
        # 파일 검증
        if not file.filename.lower().endswith(('.pdf', '.xlsx', '.xls', '.docx', '.doc')):
            raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식입니다.")
        
        # 파일 크기 검증 (4.5MB 제한 - Vercel 서버리스 함수 최적화)
        file_content = await file.read()
        if len(file_content) > 4.5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="파일 크기는 4.5MB를 초과할 수 없습니다. 안정적인 처리를 위한 제한사항입니다.")
        
        # 파일 처리
        ir_summary = await process_uploaded_file(file_content, file.filename)
        print(f"📄 파일 처리 완료: {file.filename}")
        
        # 투자심사보고서 생성
        investment_report = await generate_investment_report(
            ir_summary=ir_summary,
            company_name=company_name,
            api_key=api_key
        )
        print(f"📋 투자심사보고서 생성 완료")
        
        return {
            "success": True,
            "company_name": company_name,
            "investment_report": investment_report,
            "source_file": file.filename,
            "report_type": "투자심사보고서 초안"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 파일 분석 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"파일 분석 중 오류 발생: {str(e)}")

async def process_uploaded_file(file_content: bytes, filename: str) -> str:
    """업로드된 파일 처리"""
    try:
        import sys
        sys.path.append(str(BASE_DIR))  # 프로젝트 루트를 Python 경로에 추가
        from pdf_processor import PDFProcessor
        
        processor = PDFProcessor()
        
        # 파일 확장자에 따른 처리
        file_ext = filename.lower().split('.')[-1]
        
        if file_ext == 'pdf':
            # PDF 처리
            pdf_result = processor.extract_text_from_bytes(file_content)
            
            if pdf_result["success"]:
                # 가상의 URL로 summary 생성
                extracted_data = {
                    "success": True,
                    "url": f"uploaded_file://{filename}",
                    "file_size": len(file_content),
                    "extracted_text": pdf_result["text"],
                    "page_count": pdf_result["page_count"],
                    "company_info": processor.extract_company_info(pdf_result["text"])
                }
                return processor.create_ir_summary(extracted_data)
            else:
                raise Exception(f"PDF 처리 실패: {pdf_result.get('error', '알 수 없는 오류')}")
        
        elif file_ext in ['xlsx', 'xls']:
            # Excel 처리 (기본적인 텍스트 추출)
            return f"""
=== IR 자료 분석 원본 데이터 ===

📊 파일 정보:
- 파일명: {filename}
- 파일 크기: {len(file_content):,} bytes
- 파일 형식: Excel

📄 파일 내용:
Excel 파일이 업로드되었습니다. 
파일 처리 기능을 구현 중입니다.

=== 분석 요청 ===
위의 IR 자료를 바탕으로 투자심사보고서를 작성해주세요.
"""
        
        elif file_ext in ['docx', 'doc']:
            # Word 처리 (기본적인 텍스트 추출)
            return f"""
=== IR 자료 분석 원본 데이터 ===

📊 파일 정보:
- 파일명: {filename}
- 파일 크기: {len(file_content):,} bytes
- 파일 형식: Word

📄 파일 내용:
Word 파일이 업로드되었습니다.
파일 처리 기능을 구현 중입니다.

=== 분석 요청 ===
위의 IR 자료를 바탕으로 투자심사보고서를 작성해주세요.
"""
        
        else:
            raise Exception(f"지원하지 않는 파일 형식: {file_ext}")
            
    except Exception as e:
        raise Exception(f"파일 처리 실패: {str(e)}")


@app.post("/api/analyze-ir")
async def analyze_ir(request: IRAnalysisRequest, api_key: str = Depends(verify_token)):
    """IR 자료 분석 메인 엔드포인트"""
    try:
        print(f"📊 IR 분석 시작: {request.company_name}")
        
        # 1. IR 파일 다운로드 및 텍스트 추출
        ir_summary = await download_and_extract_ir(request.ir_url)
        print(f"📄 IR 파일 처리 완료")
        
        # 2. JSONL 학습 데이터와 함께 Gemini API로 투자심사보고서 생성
        investment_report = await generate_investment_report(
            ir_summary=ir_summary,
            company_name=request.company_name,
            api_key=api_key
        )
        print(f"📋 투자심사보고서 생성 완료")
        
        # 3. 결과를 여러 곳에 전달
        await distribute_results({
            "company_name": request.company_name,
            "investment_report": investment_report,
            "source_url": request.ir_url,
            "analysis_date": datetime.now().isoformat(),
            "requester": "API"
        })
        
        return {
            "success": True,
            "company_name": request.company_name,
            "investment_report": investment_report,
            "source_url": request.ir_url,
            "report_type": "투자심사보고서 초안",
            "message": "보고서가 생성되어 Airtable, 이메일 등으로 전달되었습니다."
        }
        
    except Exception as e:
        print(f"❌ 분석 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"분석 중 오류 발생: {str(e)}")

@app.post("/webhook/jandi")
async def jandi_webhook(request: JandiWebhookRequest):
    """잔디 웹훅 처리"""
    try:
        print(f"📞 잔디 웹훅 수신: {request.text}")
        
        # 메시지에서 URL과 회사명 추출
        url_pattern = r'https?://[^\s]+\.(?:pdf|xlsx?|docx?)'
        urls = re.findall(url_pattern, request.text, re.IGNORECASE)
        
        if not urls:
            return {"success": False, "message": "IR 자료 URL을 찾을 수 없습니다."}
        
        # 회사명 추출 (간단한 방식)
        company_name = extract_company_name(request.text)
        
        # IR 분석 실행
        analysis_request = IRAnalysisRequest(
            company_name=company_name,
            ir_url=urls[0]
        )
        
        result = await analyze_ir(analysis_request)
        
        return {
            "success": True,
            "message": f"{company_name} IR 분석이 완료되었습니다.",
            "result": result
        }
        
    except Exception as e:
        print(f"❌ 잔디 웹훅 처리 오류: {str(e)}")
        return {"success": False, "message": f"처리 중 오류: {str(e)}"}

async def download_and_extract_ir(url: str) -> str:
    """IR 파일 다운로드 및 텍스트 추출"""
    try:
        import sys
        sys.path.append(str(BASE_DIR))  # 프로젝트 루트를 Python 경로에 추가
        from pdf_processor import PDFProcessor
        
        print(f"📥 PDF 처리 시작: {url}")
        processor = PDFProcessor()
        result = processor.extract_text_from_url(url)
        
        if result["success"]:
            print(f"✅ PDF 처리 성공: {result['page_count']}페이지, {len(result['extracted_text'])}글자")
            return processor.create_ir_summary(result)
        else:
            raise Exception(result["error"])
            
    except Exception as e:
        raise Exception(f"파일 다운로드 실패: {str(e)}")

async def generate_investment_report(ir_summary: str, company_name: str, api_key: str) -> str:
    """JSONL 학습 데이터를 바탕으로 투자심사보고서 생성"""
    try:
        import sys
        sys.path.append(str(BASE_DIR))  # 프로젝트 루트를 Python 경로에 추가
        from jsonl_processor import JSONLProcessor
        
        print(f"📚 JSONL 학습 데이터 로드 중...")
        
        # JSONL 학습 데이터 로드 (api 폴더 내 경로 지정)
        jsonl_path = BASE_DIR / "jsonl_data"
        processor = JSONLProcessor(str(jsonl_path))
        learning_context = processor.create_learning_context()
        report_template = processor.get_report_structure_template()
        
        print(f"📖 학습 데이터 로드 완료: {len(processor.learned_reports)}개 보고서")
        
        # 투자심사보고서 생성 프롬프트 (머쉬앤 스타일 기반)
        prompt = f"""
MISSION (최종 임무)
당신은 한 명의 심사역이 아닌, **대한민국 최고의 임팩트 투자사를 이끄는 매니징 파트너(Managing Partner)**입니다. 당신의 한마디는 투자의 방향을 결정하고, 당신의 투자 메모는 단순한 보고서가 아닌, **하나의 산업을 정의하고 회사의 미래를 예측하는 '선언문(Manifesto)'**입니다. 당신의 임무는 날카로운 통찰력과 압도적인 논리로, 파트너 회의에서 반론의 여지 없이 투자를 관철시키는 **'Investment Thesis Memo'**를 작성하는 것입니다. 모든 문장은 당신의 확신을 증명해야 합니다.

THE PARTNER'S DECALOGUE (파트너의 10계명)
당신은 보고서 작성 시, 아래 10가지 원칙을 '신조'처럼 따라야 합니다.

1. 모든 것은 '투자 논지(Investment Thesis)'에서 시작된다.

보고서 서두에 이 투자 건을 한 문장으로 정의하는, 강력하고 명료한 '투자 논지'를 선언하십시오. (예: "동사는 폭발하는 대체식품 시장의 'Intel Inside'가 될 것이며, 모든 식품 대기업이 의존할 수밖에 없는 고부가가치 원천소재 공급망을 독점할 것입니다.")

보고서의 모든 내용(시장, 팀, 기술, 재무)은 이 핵심 논지를 증명하기 위한 근거로만 기능해야 합니다.

2. 모든 주장은 숫자로 말한다 (Quant-First Mandate).

"시장이 크다"가 아니라, "연평균 18.6%로 성장하여 2030년 162조원에 달하는 시장"으로 서술합니다.

"팀이 우수하다"가 아니라, "총합 20년 이상의 버섯 연구 경력과 KAIST MBA의 사업 전략을 결합한 팀"으로 계량화합니다.

3. '회사의 주장'과 '나의 관점'을 명확히 분리한다 (The Analyst's Edge).

재무 추정 등에서 회사 제시 자료(Company-provided)와 심사역 추정(Analyst's View)을 반드시 분리하여 제시하십시오.

나의 관점에서 보수적인 가정을 적용했다면(예: "회사 제시 매출의 50% 수준으로 할인 적용"), 그 논리적 근거(시장 경쟁 심화 가능성, 초기 시장의 불확실성 등)를 명확히 밝히십시오.

4. 스스로 투자를 기각시켜라 (Investment Killer Analysis).

리스크 분석을 넘어, '이 투자가 실패할 수밖에 없는 3가지 이유(Investment Killers)' 라는 별도 항목을 구성하십시오.

그리고 각 Killer 시나리오를 어떻게 방어하거나 완화할 수 있는지(Mitigation Plan) 논리적으로 반박하며, 그럼에도 투자가 유효함을 증명하십시오.

5. 가설은 '검증 가능한 질문'으로 전환된다.

"(정보 없음)"은 금지어입니다. 대신 "대표이사의 글로벌 사업개발 역량은 KOICA 사업 선정 이력으로 일부 증명되었으나, 북미/유럽 시장 진출을 위한 구체적인 네트워크와 실행력은 실사를 통해 'OO기업과의 파트너십 체결 경험', '해외 매출 발생 이력' 등을 통해 반드시 확인해야 함" 과 같이, 검증해야 할 구체적인 질문과 지표를 제시하십시오.

6. 임팩트는 비즈니스의 '해자(Moat)'가 된다 (Impact as a Moat).

"플라스틱을 줄여서 착하다"는 분석은 거부합니다. "동사의 친환경 리필 솔루션이 창출하는 '자원 절감' 및 '탄소 배출권'이라는 임팩트 자산은, 향후 탄소세 등 환경 규제 강화 시 경쟁사 대비 압도적인 비용 우위를 제공하는 핵심적인 경제적 해자로 작용할 것"처럼, 임팩트가 어떻게 지속가능한 경쟁우위와 재무적 성과로 직결되는지를 증명해야 합니다.

SDGs와 IRIS+는 이 '임팩트-재무 연결고리'를 증명하는 데이터 근거로만 활용하십시오.

7. 경쟁 분석은 '전장(Battlefield)'을 그리는 것이다.

경쟁사를 나열하는 것을 넘어, 경쟁 구도(Positioning Map)를 통해 **'우리가 싸워 이길 수 있는 전장'**을 명확히 정의하십시오. (예: "경쟁사들이 완제품 시장에서 높은 마케팅 비용으로 경쟁할 때, 우리는 마진율이 높은 '원천소재' 시장을 무혈입성하여 전장의 규칙 자체를 바꿀 것입니다.")

8. 성장 지원은 '100일 계획(100-Day Plan)'으로 제시한다.

'경영 자문', '네트워킹' 같은 추상적인 지원 전략을 지양합니다. 투자 직후 100일 안에 달성할 구체적인 목표 3~5가지를 제시하십시오. (예: "100일 내 목표: 1) 유한킴벌리, 아모레퍼시픽 등 전략적 파트너사와 최소 3회 이상 미팅 주선, 2) TIPS 추천을 위한 기술사업계획서(TIPS) 초안 완성, 3) 후속 투자 유치를 위한 VC 리스트업 및 IR 자료 고도화 완료")

9. 재무 분석은 '시나리오'와 '민감도'를 보여준다.

'점'이 아닌 '범위'로 미래를 예측하십시오. Base(기본), Best(최상), Worst(최악) 시나리오별 재무 추정과 예상 수익률을 제시하여, 투자의 잠재적 변동성을 명확히 보여줘야 합니다.

손익에 가장 큰 영향을 미치는 핵심 변수(Key Driver)가 무엇인지 밝히고, 해당 변수의 변동에 따라 IRR, Multiple이 어떻게 변하는지에 대한 '민감도 분석(Sensitivity Analysis)' 결과를 서술하십시오.

10. 종합 결론은 '투자 집행'을 명령하는 것이다.

"투자를 긍정적으로 검토함" 같은 미온적인 표현을 사용하지 않습니다. "위와 같은 논거에 기반하여, 본 조합은 농업회사법인 머쉬앤에 보통주 OOO원을 투자하는 안건을 '집행'할 것을 강력히 제안합니다." 와 같이, 확신에 찬 어조로 명확한 의사결정을 촉구하며 마무리합니다.

보고서 구조 (Report Structure)
아래의 마크다운 구조를 반드시 준수하여 보고서를 작성하십시오.

Markdown

# Executive Summary

## 1. 투자 개요
### 1.1. 기업 개요
### 1.2. 투자 조건
### 1.3. 손익 추정 및 수익성

## 2. 기업 현황
### 2.1. 일반 현황
### 2.2. 연혁 및 주주현황
### 2.3. 조직 및 핵심 구성원

## 3. 시장 분석
### 3.1. 시장 현황
### 3.2. 경쟁사 분석

## 4. 사업 분석
### 4.1. 사업 개요
### 4.2. 향후 전략 및 계획

## 5. 투자 적합성과 임팩트
### 5.1. 투자 적합성
### 5.2. 소셜임팩트
### 5.3. 투자사 성장지원 전략

## 6. 손익 추정 및 수익성 분석
### 6.1. 손익 추정
### 6.2. 기업가치평가 및 수익성 분석

## 7. 종합 결론
INPUT DATA (입력 데이터)
학습 데이터: {learning_context} (당신의 과거 성공 메모. 여기서 데이터 기반의 확신, 명료한 논지, 분석의 틀을 학습할 것)

분석 대상 IR 자료: {ir_summary} (새로운 딜 정보. 이 내용을 당신의 분석 틀에 넣어 재구성할 것)

EXECUTION (최종 명령)
위의 MISSION과 THE PARTNER'S DECALOGUE에 따라, 주어진 입력 데이터를 활용하고 명시된 보고서 구조를 엄격히 준수하여 **{company_name}**에 대한 **'Investment Thesis Memo'**를 작성하십시오. 당신의 날카로운 분석을 기대합니다. 시작하십시오.
"""
        
        print(f"🤖 Gemini API 호출 중...")
        
        # 사용자의 API 키로 Gemini API 설정
        genai.configure(api_key=api_key)
        
        # Gemini API 호출
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt)
        
        print(f"✅ Gemini API 응답 완료")
        
        return response.text
        
    except Exception as e:
        raise Exception(f"투자심사보고서 생성 실패: {str(e)}")

async def distribute_results(report_data: dict):
    """결과를 여러 채널로 전달"""
    try:
        print(f"📤 결과 배포 시작: {report_data['company_name']}")
        
        # 1. Airtable에 저장
        if os.getenv("AIRTABLE_API_KEY") and os.getenv("AIRTABLE_BASE_ID"):
            try:
                await save_to_airtable(report_data)
                print("✅ Airtable 저장 완료")
            except Exception as e:
                print(f"⚠️ Airtable 저장 실패: {e}")
        
        # 2. 이메일 발송
        if os.getenv("NOTIFICATION_EMAIL"):
            try:
                await send_email_report(report_data)
                print("✅ 이메일 발송 완료")
            except Exception as e:
                print(f"⚠️ 이메일 발송 실패: {e}")
        
        # 3. 잔디 알림
        if os.getenv("JANDI_WEBHOOK_URL"):
            try:
                await send_jandi_notification(report_data)
                print("✅ 잔디 알림 완료")
            except Exception as e:
                print(f"⚠️ 잔디 알림 실패: {e}")
        
        print(f"📤 결과 배포 완료")
        
    except Exception as e:
        print(f"❌ 결과 배포 중 오류: {e}")

async def save_to_airtable(report_data: dict):
    """Airtable에 결과 저장"""
    airtable_url = f"https://api.airtable.com/v0/{os.getenv('AIRTABLE_BASE_ID')}/{os.getenv('AIRTABLE_TABLE_NAME', 'IR분석결과')}"
    
    headers = {
        "Authorization": f"Bearer {os.getenv('AIRTABLE_API_KEY')}",
        "Content-Type": "application/json"
    }
    
    data = {
        "fields": {
            "회사명": report_data["company_name"],
            "투자심사보고서": report_data["investment_report"][:50000],  # Airtable 길이 제한
            "분석일시": report_data["analysis_date"],
            "IR_URL": report_data["source_url"],
            "요청자": report_data.get("requester", "Unknown")
        }
    }
    
    response = requests.post(airtable_url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

async def send_email_report(report_data: dict):
    """이메일로 보고서 발송"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    msg = MIMEMultipart()
    msg['From'] = os.getenv('SMTP_FROM_EMAIL')
    msg['To'] = os.getenv('NOTIFICATION_EMAIL')
    msg['Subject'] = f"📊 투자심사보고서: {report_data['company_name']}"
    
    # HTML 형태로 보고서 전송
    html_body = f"""
    <html>
    <body>
        <h2>🏢 투자심사보고서</h2>
        <h3>회사명: {report_data['company_name']}</h3>
        <p><strong>분석일시:</strong> {report_data['analysis_date']}</p>
        <p><strong>IR 자료:</strong> <a href="{report_data['source_url']}">{report_data['source_url']}</a></p>
        
        <hr>
        <div style="white-space: pre-wrap; font-family: Arial, sans-serif;">
        {report_data['investment_report'][:10000]}
        </div>
        
        {"<p><em>... 전체 보고서는 Airtable에서 확인하세요.</em></p>" if len(report_data['investment_report']) > 10000 else ""}
    </body>
    </html>
    """
    
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))
    
    # SMTP 서버 연결 및 발송
    server = smtplib.SMTP(os.getenv('SMTP_SERVER', 'smtp.gmail.com'), int(os.getenv('SMTP_PORT', '587')))
    server.starttls()
    server.login(os.getenv('SMTP_FROM_EMAIL'), os.getenv('SMTP_PASSWORD'))
    
    text = msg.as_string()
    server.sendmail(os.getenv('SMTP_FROM_EMAIL'), os.getenv('NOTIFICATION_EMAIL'), text)
    server.quit()

async def send_jandi_notification(report_data: dict):
    """잔디로 완료 알림"""
    webhook_url = os.getenv('JANDI_WEBHOOK_URL')
    
    payload = {
        "body": f"📊 투자심사보고서 생성 완료!\n\n"
                f"🏢 회사명: {report_data['company_name']}\n"
                f"📅 분석일시: {report_data['analysis_date']}\n"
                f"📎 IR 자료: {report_data['source_url']}\n\n"
                f"상세 보고서는 Airtable 또는 이메일에서 확인하세요.",
        "connectColor": "#00D2BF",
        "connectInfo": [{
            "title": "투자심사보고서 생성 완료",
            "description": f"{report_data['company_name']} 분석이 완료되었습니다."
        }]
    }
    
    response = requests.post(webhook_url, json=payload)
    response.raise_for_status()

def extract_company_name(text: str) -> str:
    """텍스트에서 회사명 추출"""
    # IR분석, 분석 등의 키워드 제거 후 첫 번째 단어를 회사명으로 사용
    clean_text = re.sub(r'IR분석|분석|요청|부탁', '', text).strip()
    words = clean_text.split()
    
    for word in words:
        # URL이 아닌 첫 번째 단어를 회사명으로 사용
        if not word.startswith('http'):
            return word
    
    return "분석대상기업"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)