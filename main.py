from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import requests
import google.generativeai as genai
import os
from dotenv import load_dotenv
import re
from typing import Optional
from datetime import datetime

# 환경변수 로드
load_dotenv()

app = FastAPI(title="IR Analyzer", version="1.0.0")

# CORS 설정 (Google Sites에서 호출하기 위해)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/", response_class=HTMLResponse)
async def get_homepage():
    """메인 홈페이지 반환"""
    # HTML 파일을 읽어서 반환 (나중에 별도 파일로 분리 가능)
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>IR 투자심사보고서 분석기</title>
        <!-- 여기에 위의 HTML/CSS 내용을 넣으면 됩니다 -->
    </head>
    <body>
        <h1>IR 분석기 홈페이지</h1>
        <p>곧 업데이트 예정입니다!</p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/analyze-ir-file")
async def analyze_ir_file(
    file: UploadFile = File(...),
    company_name: str = Form(...)
):
    """파일 업로드를 통한 IR 자료 분석"""
    try:
        print(f"📎 파일 업로드 분석 시작: {company_name} - {file.filename}")
        
        # 파일 검증
        if not file.filename.lower().endswith(('.pdf', '.xlsx', '.xls', '.docx', '.doc')):
            raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식입니다.")
        
        # 파일 크기 검증 (100MB 제한)
        file_content = await file.read()
        if len(file_content) > 100 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="파일 크기는 100MB를 초과할 수 없습니다.")
        
        # 파일 처리
        ir_summary = await process_uploaded_file(file_content, file.filename)
        print(f"📄 파일 처리 완료: {file.filename}")
        
        # 투자심사보고서 생성
        investment_report = await generate_investment_report(
            ir_summary=ir_summary,
            company_name=company_name
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

@app.get("/", response_class=HTMLResponse)
async def root():
    """메인 홈페이지 - 위의 HTML 인터페이스 반환"""
    # 실제 HTML 파일을 읽어서 반환하거나, 위의 artifacts HTML을 사용
    return HTMLResponse(content="""
    <!-- 여기에 위의 web_interface HTML 내용을 복사해서 넣으면 됩니다 -->
    <h1>IR 분석기가 곧 업데이트됩니다!</h1>
    <p>API 문서는 <a href="/docs">/docs</a>에서 확인하세요.</p>
    """)

@app.post("/api/analyze-ir")
async def analyze_ir(request: IRAnalysisRequest):
    """IR 자료 분석 메인 엔드포인트"""
    try:
        print(f"📊 IR 분석 시작: {request.company_name}")
        
        # 1. IR 파일 다운로드 및 텍스트 추출
        ir_summary = await download_and_extract_ir(request.ir_url)
        print(f"📄 IR 파일 처리 완료")
        
        # 2. JSONL 학습 데이터와 함께 Gemini API로 투자심사보고서 생성
        investment_report = await generate_investment_report(
            ir_summary=ir_summary,
            company_name=request.company_name
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

async def generate_investment_report(ir_summary: str, company_name: str) -> str:
    """JSONL 학습 데이터를 바탕으로 투자심사보고서 생성"""
    try:
        from jsonl_processor import JSONLProcessor
        
        print(f"📚 JSONL 학습 데이터 로드 중...")
        
        # JSONL 학습 데이터 로드
        processor = JSONLProcessor()
        learning_context = processor.create_learning_context()
        report_template = processor.get_report_structure_template()
        
        print(f"📖 학습 데이터 로드 완료: {len(processor.learned_reports)}개 보고서")
        
        # 투자심사보고서 생성 프롬프트 (머쉬앤 스타일 기반)
        prompt = f"""
## 임무 (MISSION)

당신은 대한민국 최고의 임팩트 투자사에서 근무하는 선임 심사역입니다. 당신의 임무는 주어진 **JSONL 학습 데이터**와 **IR 자료**를 바탕으로, 내부투자심의위원회에 상정할 상세하고 설득력 있는 '투자심사보고서' 초안을 작성하는 것입니다.

## 핵심 지시사항

1. **보고서 구조 준수**: 아래 제시된 [보고서 구조]를 반드시 따르십시오.
2. **데이터 기반 서술**: 학습된 JSONL 데이터의 패턴을 참고하여 전문적인 비즈니스 톤앤매너로 서술하세요.
3. **논리 구조 구체화**: 투자 포인트는 '주장(Claim)', '근거(Evidence)', '해석(Reasoning)'의 논리 구조로 서술하세요.
4. **완전성**: 주어진 정보를 활용하여 보고서의 각 파트를 풍부하고 상세하게 작성하세요.

## 보고서 구조

### Executive Summary
### 1. 투자 개요
#### 1.1 기업 개요
#### 1.2 투자 조건 
#### 1.3 손익 추정 및 수익성
### 2. 기업 현황
#### 2.1 일반 현황
#### 2.2 연혁 및 주주현황
#### 2.3 조직 및 핵심 구성원
### 3. 시장 분석
#### 3.1 시장 현황
#### 3.2 경쟁사 분석
### 4. 사업 분석
#### 4.1 사업 개요
#### 4.2 향후 전략 및 계획
### 5. 투자 적합성과 임팩트
#### 5.1 투자 적합성
#### 5.2 소셜임팩트
#### 5.3 투자사 성장지원 전략
### 6. 손익 추정 및 수익성 분석
#### 6.1 손익 추정
#### 6.2 기업가치평가 및 수익성 분석  
### 7. 종합 결론

=== 학습 데이터 ===
{learning_context}

=== 보고서 구조 템플릿 ===
{report_template}

=== 분석 대상 IR 자료 ===
{ir_summary}

위의 학습 데이터 패턴을 참고하여, 제공된 IR 자료로 **{company_name}**에 대한 전문적인 투자심사보고서를 작성하세요.

**주의사항:**
- 학습 데이터의 구조와 톤앤매너를 따라 작성하되, 제공된 IR 자료의 내용에 맞게 적용하세요
- 구체적인 수치나 데이터가 없는 경우 "추후 실사를 통해 확인 필요"라고 명시하세요  
- 투자 의견은 긍정적이되 객관적인 리스크도 함께 제시하세요
- 전체 길이는 A4 5-7페이지 분량으로 작성하세요
"""
        
        print(f"🤖 Gemini API 호출 중...")
        
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