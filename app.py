import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import requests
from datetime import datetime
import tempfile
import re

# 환경변수 로드
load_dotenv()

# Gemini API 설정
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 페이지 설정
st.set_page_config(
    page_title="IR 투자심사보고서 분석기",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .upload-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 2px dashed #667eea;
        margin: 1rem 0;
    }
    .result-section {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        margin-top: 2rem;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# 헤더
st.markdown("""
<div class="main-header">
    <h1>📊 IR 투자심사보고서 분석기</h1>
    <p>AI 기반 투자심사보고서 자동 생성 시스템</p>
</div>
""", unsafe_allow_html=True)

# 사이드바 설정
with st.sidebar:
    st.header("⚙️ 설정")
    st.info("💡 **사용법**\n\n1. 회사명을 입력하세요\n2. IR 자료를 업로드하거나 URL을 입력하세요\n3. '분석하기' 버튼을 클릭하세요")
    
    # API 키 확인
    if os.getenv("GEMINI_API_KEY"):
        st.success("✅ Gemini API 연결됨")
    else:
        st.error("❌ Gemini API 키가 필요합니다")

# 메인 컨텐츠
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📋 분석 설정")
    
    # 회사명 입력
    company_name = st.text_input("🏢 회사명", placeholder="분석할 회사명을 입력하세요")
    
    # 파일 업로드 또는 URL 입력 선택
    input_method = st.radio("📁 입력 방식 선택", ["파일 업로드", "URL 입력"])
    
    uploaded_file = None
    ir_url = None
    
    if input_method == "파일 업로드":
        st.markdown("""
        <div class="upload-section">
            <h4>📎 IR 자료 업로드</h4>
            <p>PDF, Excel, Word 파일을 업로드하세요</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "파일 선택",
            type=['pdf', 'xlsx', 'xls', 'docx', 'doc'],
            help="PDF, Excel, Word 파일을 지원합니다"
        )
        
        if uploaded_file:
            st.success(f"✅ 파일 업로드됨: {uploaded_file.name} ({uploaded_file.size:,} bytes)")
    
    else:
        ir_url = st.text_input("🔗 IR 자료 URL", placeholder="https://example.com/ir-report.pdf")
        
        if ir_url:
            st.success(f"✅ URL 입력됨: {ir_url}")

with col2:
    st.header("📊 분석 상태")
    status_placeholder = st.empty()
    
    with status_placeholder.container():
        st.info("⏳ 분석 대기 중...")

# 분석 실행 버튼
if st.button("🚀 투자심사보고서 생성하기", type="primary"):
    if not company_name:
        st.error("❌ 회사명을 입력해주세요")
    elif not uploaded_file and not ir_url:
        st.error("❌ IR 자료를 업로드하거나 URL을 입력해주세요")
    elif not os.getenv("GEMINI_API_KEY"):
        st.error("❌ Gemini API 키가 설정되지 않았습니다")
    else:
        # 분석 실행
        with st.spinner("🤖 AI가 투자심사보고서를 생성하고 있습니다..."):
            try:
                # 상태 업데이트
                with status_placeholder.container():
                    st.warning("🔄 분석 진행 중...")
                
                # IR 자료 처리
                if uploaded_file:
                    # 파일 처리
                    ir_summary = process_uploaded_file(uploaded_file)
                    st.info("📄 파일 처리 완료")
                else:
                    # URL 처리
                    ir_summary = download_and_extract_ir(ir_url)
                    st.info("📥 URL 자료 다운로드 완료")
                
                # 투자심사보고서 생성
                investment_report = generate_investment_report(ir_summary, company_name)
                
                # 결과 표시
                with status_placeholder.container():
                    st.success("✅ 분석 완료!")
                
                st.markdown("""
                <div class="result-section">
                    <h3>📋 투자심사보고서 생성 완료</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # 결과 탭
                tab1, tab2 = st.tabs(["📊 투자심사보고서", "📁 원본 자료"])
                
                with tab1:
                    st.markdown(f"### 🏢 {company_name} 투자심사보고서")
                    st.markdown("---")
                    st.markdown(investment_report)
                    
                    # 다운로드 버튼
                    st.download_button(
                        label="💾 보고서 다운로드 (텍스트)",
                        data=investment_report,
                        file_name=f"{company_name}_투자심사보고서_{datetime.now().strftime('%Y%m%d')}.txt",
                        mime="text/plain"
                    )
                
                with tab2:
                    st.markdown("### 📄 원본 IR 자료 요약")
                    st.text_area("원본 자료", value=ir_summary[:2000] + "..." if len(ir_summary) > 2000 else ir_summary, height=300)
                
            except Exception as e:
                with status_placeholder.container():
                    st.error(f"❌ 분석 실패: {str(e)}")
                st.error(f"분석 중 오류가 발생했습니다: {str(e)}")

def process_uploaded_file(uploaded_file):
    """업로드된 파일 처리"""
    try:
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        # 파일 확장자에 따른 처리
        file_ext = uploaded_file.name.lower().split('.')[-1]
        
        if file_ext == 'pdf':
            # PDF 처리
            try:
                from pdf_processor import PDFProcessor
                processor = PDFProcessor()
                
                # 파일에서 텍스트 추출
                with open(tmp_file_path, 'rb') as f:
                    file_content = f.read()
                
                pdf_result = processor.extract_text_from_bytes(file_content)
                
                if pdf_result["success"]:
                    extracted_data = {
                        "success": True,
                        "url": f"uploaded_file://{uploaded_file.name}",
                        "file_size": len(file_content),
                        "extracted_text": pdf_result["text"],
                        "page_count": pdf_result["page_count"],
                        "company_info": processor.extract_company_info(pdf_result["text"])
                    }
                    return processor.create_ir_summary(extracted_data)
                else:
                    raise Exception(f"PDF 처리 실패: {pdf_result.get('error', '알 수 없는 오류')}")
            except ImportError:
                # pdf_processor가 없는 경우 기본 처리
                return f"""
=== IR 자료 분석 원본 데이터 ===

📊 파일 정보:
- 파일명: {uploaded_file.name}
- 파일 크기: {uploaded_file.size:,} bytes
- 파일 형식: PDF

📄 파일 내용:
PDF 파일이 업로드되었습니다.
PDF 처리 모듈을 설치해주세요: pip install PyPDF2

=== 분석 요청 ===
위의 IR 자료를 바탕으로 투자심사보고서를 작성해주세요.
"""
        
        elif file_ext in ['xlsx', 'xls']:
            return f"""
=== IR 자료 분석 원본 데이터 ===

📊 파일 정보:
- 파일명: {uploaded_file.name}
- 파일 크기: {uploaded_file.size:,} bytes
- 파일 형식: Excel

📄 파일 내용:
Excel 파일이 업로드되었습니다.
파일 처리 기능을 구현 중입니다.

=== 분석 요청 ===
위의 IR 자료를 바탕으로 투자심사보고서를 작성해주세요.
"""
        
        elif file_ext in ['docx', 'doc']:
            return f"""
=== IR 자료 분석 원본 데이터 ===

📊 파일 정보:
- 파일명: {uploaded_file.name}
- 파일 크기: {uploaded_file.size:,} bytes
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
    finally:
        # 임시 파일 정리
        try:
            os.unlink(tmp_file_path)
        except:
            pass

def download_and_extract_ir(url: str) -> str:
    """IR 파일 다운로드 및 텍스트 추출"""
    try:
        from pdf_processor import PDFProcessor
        
        processor = PDFProcessor()
        result = processor.extract_text_from_url(url)
        
        if result["success"]:
            return processor.create_ir_summary(result)
        else:
            raise Exception(result["error"])
            
    except ImportError:
        # pdf_processor가 없는 경우 기본 처리
        return f"""
=== IR 자료 분석 원본 데이터 ===

📊 자료 정보:
- URL: {url}
- 파일 형식: PDF (추정)

📄 파일 내용:
URL에서 IR 자료를 다운로드했습니다.
PDF 처리 모듈을 설치해주세요: pip install PyPDF2

=== 분석 요청 ===
위의 IR 자료를 바탕으로 투자심사보고서를 작성해주세요.
"""
    except Exception as e:
        raise Exception(f"파일 다운로드 실패: {str(e)}")

def generate_investment_report(ir_summary: str, company_name: str) -> str:
    """JSONL 학습 데이터를 바탕으로 투자심사보고서 생성"""
    try:
        # JSONL 학습 데이터 로드
        learning_context = ""
        report_template = ""
        
        try:
            from jsonl_processor import JSONLProcessor
            processor = JSONLProcessor()
            learning_context = processor.create_learning_context()
            report_template = processor.get_report_structure_template()
        except ImportError:
            learning_context = "학습 데이터를 로드할 수 없습니다. 기본 템플릿을 사용합니다."
            report_template = """
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
"""
        
        # 투자심사보고서 생성 프롬프트
        prompt = f"""
## 임무 (MISSION)

당신은 대한민국 최고의 임팩트 투자사에서 근무하는 선임 심사역입니다. 당신의 임무는 주어진 **JSONL 학습 데이터**와 **IR 자료**를 바탕으로, 내부투자심의위원회에 상정할 상세하고 설득력 있는 '투자심사보고서' 초안을 작성하는 것입니다.

## 핵심 지시사항

1. **보고서 구조 준수**: 아래 제시된 [보고서 구조]를 반드시 따르십시오.
2. **데이터 기반 서술**: 학습된 JSONL 데이터의 패턴을 참고하여 전문적인 비즈니스 톤앤매너로 서술하세요.
3. **논리 구조 구체화**: 투자 포인트는 '주장(Claim)', '근거(Evidence)', '해석(Reasoning)'의 논리 구조로 서술하세요.
4. **완전성**: 주어진 정보를 활용하여 보고서의 각 파트를 풍부하고 상세하게 작성하세요.

## 보고서 구조

{report_template}

=== 학습 데이터 ===
{learning_context}

=== 분석 대상 IR 자료 ===
{ir_summary}

위의 학습 데이터 패턴을 참고하여, 제공된 IR 자료로 **{company_name}**에 대한 전문적인 투자심사보고서를 작성하세요.

**주의사항:**
- 학습 데이터의 구조와 톤앤매너를 따라 작성하되, 제공된 IR 자료의 내용에 맞게 적용하세요
- 구체적인 수치나 데이터가 없는 경우 "추후 실사를 통해 확인 필요"라고 명시하세요  
- 투자 의견은 긍정적이되 객관적인 리스크도 함께 제시하세요
- 전체 길이는 A4 5-7페이지 분량으로 작성하세요
"""
        
        # Gemini API 호출
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt)
        
        return response.text
        
    except Exception as e:
        raise Exception(f"투자심사보고서 생성 실패: {str(e)}")

# 푸터
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🤖 AI 기반 IR 투자심사보고서 분석기 | Made with Streamlit</p>
    <p>📧 문의사항이 있으시면 언제든 연락주세요</p>
</div>
""", unsafe_allow_html=True)