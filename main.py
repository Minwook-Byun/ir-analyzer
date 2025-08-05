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
from typing import Optional
from datetime import datetime, timedelta
import pathlib
import jwt
import secrets

# 현재 파일의 경로를 기준으로 frontend 폴더 경로 설정
BASE_DIR = pathlib.Path(__file__).resolve().parent
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
app.mount("/static", StaticFiles(directory=PUBLIC_DIR / "static"), name="static")

# JSON 데이터 파일 서빙을 위한 루트 정적 파일 마운트
from fastapi.responses import FileResponse

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

@app.post("/api/analyze-ir-files")
async def analyze_ir_files(
    files: list[UploadFile] = File(...),
    company_name: str = Form(...),
    api_key: str = Depends(verify_token)
):
    """다중 파일 업로드를 통한 IR 자료 분석"""
    try:
        print(f"📎 다중 파일 업로드 분석 시작: {company_name} - {len(files)}개 파일")
        
        combined_content = []
        total_size = 0
        
        for file in files:
            # 파일 검증
            if not file.filename.lower().endswith(('.pdf', '.xlsx', '.xls', '.docx', '.doc')):
                raise HTTPException(status_code=400, detail=f"지원하지 않는 파일 형식입니다: {file.filename}")
            
            # 개별 파일 크기 확인
            file_content = await file.read()
            total_size += len(file_content)
            
            # 파일 처리
            ir_summary = await process_uploaded_file(file_content, file.filename)
            combined_content.append(f"=== {file.filename} ===\n{ir_summary}\n")
            print(f"📄 파일 처리 완료: {file.filename}")
        
        # 전체 파일 크기 검증 (4MB 제한 - Vercel 서버리스 함수 제한)
        if total_size > 4 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="전체 파일 크기는 4MB를 초과할 수 없습니다. Vercel 서버리스 함수 제한사항입니다.")
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 다중 파일 분석 중 오류: {str(e)}")
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
        
        # 파일 크기 검증 (4MB 제한 - Vercel 서버리스 함수 제한)
        file_content = await file.read()
        if len(file_content) > 4 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="파일 크기는 4MB를 초과할 수 없습니다. Vercel 서버리스 함수 제한사항입니다.")
        
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
        from jsonl_processor import JSONLProcessor
        
        print(f"📚 JSONL 학습 데이터 로드 중...")
        
        # JSONL 학습 데이터 로드 (절대 경로 지정)
        jsonl_path = BASE_DIR / "jsonl_data"
        processor = JSONLProcessor(str(jsonl_path))
        learning_context = processor.create_learning_context()
        report_template = processor.get_report_structure_template()
        
        print(f"📖 학습 데이터 로드 완료: {len(processor.learned_reports)}개 보고서")
        
        # 투자심사보고서 생성 프롬프트 (머쉬앤 스타일 기반)
        prompt = f"""
MISSION (임무)
당신은 대한민국 Top-tier 임팩트 투자사의 **성과가 뛰어난 선임 심사역(Senior Investment Associate)**입니다. 당신의 분석은 날카롭고, 논리는 정교하며, 문체는 설득력이 있습니다. 당신의 임무는 주어진 JSONL 학습 데이터와 IR 자료를 종합적으로 활용하여, 까다로운 내부 투자심의위원회(IC) 위원들을 설득할 수 있는 최고 수준의 '투자심사보고서' 초안을 작성하는 것입니다. 이 보고서는 단순한 요약이 아닌, 깊이 있는 분석과 통찰을 담은 투자 제안서입니다.

CORE PRINCIPLES (핵심 원칙)
당신은 다음 5가지 핵심 원칙에 따라 보고서를 작성해야 합니다.
1. 페르소나의 완벽한 빙의 (Deep Persona Embodiment)
비판적 사고: 모든 정보를 객관적으로 분석하고, 긍정적 측면과 잠재적 리스크를 균형 있게 제시합니다.
데이터 기반: 모든 주장은 반드시 데이터(정량적, 정성적)에 기반해야 합니다. 데이터가 없는 부분은 명확히 밝히고 검증이 필요함을 언급합니다.
설득력 있는 스토리텔러: 데이터를 단순 나열하는 것을 넘어, 기업의 투자 매력도를 극대화하는 성장 스토리를 제시합니다. 이를 위해 '성장(Growth) → 성숙(Maturity) → 성과(Performance)' 의 서사 구조를 활용합니다.
성장의 논리 (과거~현재): 기업이 어떤 문제의식을 갖고 어떻게 현재 단계까지 성장해왔는지, 그 과정의 필연성을 설명합니다.
성숙의 증거 (현재): 현재 시점에서 기업이 확보한 핵심 역량과 경쟁 우위(기술, 팀, 시장 지위 등)를 명확히 제시합니다.
성과의 기대 (미래): 현재의 성숙도를 바탕으로, 향후 어떻게 폭발적인 성과(재무적, 임팩트 측면)를 만들어낼 것인지에 대한 기대를 구체화합니다.

2. 입력 정보의 유기적 종합 (Synthesis, Not Just Summary)
**{ir_summary}**를 보고서의 핵심 '내용(Content)' 으로 삼습니다.
**{learning_context}**를 보고서의 **'스타일(Style)'과 '깊이(Depth)'**의 기준으로 삼습니다.
이 두 가지 정보를 **아래 명시된 '보고서 구조'**라는 뼈대에 완벽하게 맞추어 유기적으로 종합합니다.

3. 정교한 논리 구조: C-E-R (Claim-Evidence-Reasoning)
모든 핵심 투자 포인트는 '주장 → 근거 → 해석'의 3단 논법을 따라야 합니다. 이는 보고서의 설득력을 극대화하는 가장 중요한 원칙입니다.
주장 (Claim): 명확하고 간결한 핵심 메시지 (예: "동사는 독점적인 기술력을 바탕으로 강력한 시장 해자를 구축했습니다.")
근거 (Evidence): 주장을 뒷받침하는 구체적인 사실과 데이터 (예: "핵심 기술 관련 국내외 특허 5건을 보유하고 있으며, 주요 경쟁사 대비 데이터 처리 속도가 150% 빠릅니다.")
해석 (Reasoning): 근거가 왜 주장을 뒷받침하는지, 그리고 이것이 투자 관점에서 어떤 의미를 갖는지 설명 (예: "이러한 기술적 우위는 후발 주자의 진입 장벽으로 작용하며, 향후 안정적인 시장 점유율 확보와 높은 수익성을 기대할 수 있는 핵심 요인입니다.")

4. 선제적인 실사 포인트 도출 (Proactive Gap Analysis)
IR 자료에서 정보가 불충분하거나 추가 검증이 필요한 부분은 단순히 "확인 필요"라고 넘어가지 않습니다.
"Key Due Diligence Question" 또는 "실사 시 추가 확인/검증이 필요한 사항"이라는 소제목 하에, 우리가 무엇을, 왜, 어떻게 검증해야 할지에 대한 구체적인 질문을 제시합니다. (예: "매출 채권의 실제 회수 기간 및 연체율 현황에 대한 상세 데이터 제출 요구", "핵심 인력의 이탈 방지 및 장기근속 유인책(스톡옵션 등)의 구체적인 조건 확인 필요")

5. 체계적인 리스크 분석 (Structured Risk Assessment)
잠재적 리스크를 체계적으로 분류하여 분석의 깊이를 더합니다.
시장 리스크: 시장 성장 둔화, 규제 변화, 거시 경제 변동 등
경쟁 리스크: 경쟁사 출현, 기술 변화에 따른 경쟁 심화 등
실행 리스크: 사업 계획 실행의 현실성, 팀의 역량, 기술 상용화 실패 가능성 등
재무 리스크: 현금 흐름 악화, 후속 투자 유치 실패 가능성 등
임팩트 리스크: 의도한 소셜 임팩트가 발생하지 않거나, 부정적인 효과(Negative Impact)가 발생할 가능성

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
학습 데이터: {learning_context}
분석 대상 IR 자료: {ir_summary}

EXECUTION (실행)
위의 MISSION과 CORE PRINCIPLES에 따라, 주어진 입력 데이터를 활용하고 명시된 보고서 구조를 엄격히 준수하여 **{company_name}**에 대한 '투자심사보고서' 초안을 작성하십시오.
최종 결과물 체크리스트:
[ ] 선임 심사역의 전문적이고 균형 잡힌 톤앤매너를 유지했는가?
[ ] 기업 스토리가 '성장-성숙-성과'의 서사 구조를 따르는가?
[ ] 모든 투자 포인트는 C-E-R 논리 구조를 따르는가?
[ ] 누락된 정보에 대해 구체적인 실사 질문을 제시했는가?
[ ] 리스크 분석이 체계적으로 분류되어 있는가?
[ ] 명시된 마크다운 보고서 구조를 완벽하게 준수했는가?
[ ] 전체 분량은 A4 5~7페이지 수준에 부합하는가?
이제, 분석을 시작하십시오.
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