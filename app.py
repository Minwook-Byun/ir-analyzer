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

# Session state 초기화
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'investment_report' not in st.session_state:
    st.session_state.investment_report = ""
if 'ir_summary' not in st.session_state:
    st.session_state.ir_summary = ""
if 'company_name' not in st.session_state:
    st.session_state.company_name = ""

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

# 로그인 함수
def login_page():
    st.markdown("""
    <div class="main-header">
        <h1>🔐 IR 투자심사보고서 분석기</h1>
        <p>Gemini API 키로 로그인하세요</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown("### 🔑 API 키 입력")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            api_key_input = st.text_input(
                "Gemini API 키를 입력하세요",
                type="password",
                placeholder="AIzaSy...",
                help="Google AI Studio에서 발급받은 Gemini API 키를 입력하세요"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # 버튼 정렬을 위한 공간
            login_btn = st.button("🚀 로그인", type="primary")
        
        if login_btn and api_key_input:
            # API 키 유효성 검사
            if validate_api_key(api_key_input):
                st.session_state.logged_in = True
                st.session_state.api_key = api_key_input
                genai.configure(api_key=api_key_input)
                st.success("✅ 로그인 성공!")
                st.rerun()
            else:
                st.error("❌ 유효하지 않은 API 키입니다. 다시 확인해주세요.")
        elif login_btn and not api_key_input:
            st.error("❌ API 키를 입력해주세요.")
        
        # API 키 발급 안내
        st.markdown("---")
        st.markdown("""
        ### 📝 API 키 발급 방법
        
        1. **Google AI Studio** 접속: https://aistudio.google.com/
        2. **Get API Key** 클릭
        3. **Create API Key** 선택
        4. 생성된 키를 복사하여 위에 입력
        
        **💡 팁**: API 키는 안전하게 보관하시고, 다른 사람과 공유하지 마세요!
        """)

def validate_api_key(api_key):
    """API 키 유효성 검사"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        # 간단한 테스트 요청
        response = model.generate_content("Hello")
        return True
    except Exception as e:
        print(f"API 키 검증 실패: {e}")
        return False

# 로그아웃 함수
def logout():
    st.session_state.logged_in = False
    st.session_state.api_key = ""
    st.rerun()

# 파일 처리 함수들
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

def generate_investment_report(ir_summary: str, company_name: str, api_key: str) -> str:
    """JSONL 학습 데이터를 바탕으로 투자심사보고서 생성"""
    try:
        # 로그 함수 정의 (세션 상태에 추가)
        def add_log(message):
            timestamp = datetime.now().strftime("%H:%M:%S")
            if 'logs' not in st.session_state:
                st.session_state.logs = []
            st.session_state.logs.append(f"[{timestamp}] {message}")
        
        # JSONL 학습 데이터 로드
        add_log("📚 학습 데이터 로드를 시작합니다...")
        learning_context = ""
        report_template = ""
        
        try:
            from jsonl_processor import JSONLProcessor
            processor = JSONLProcessor()
            learning_context = processor.create_learning_context()
            report_template = processor.get_report_structure_template()
            add_log(f"✅ JSONL 학습 데이터 로드 완료 ({len(processor.learned_reports)}개 보고서 학습)")
        except ImportError:
            add_log("⚠️ JSONL 프로세서를 찾을 수 없어 기본 템플릿을 사용합니다.")
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
        add_log("📝 투자심사보고서 생성 프롬프트를 준비합니다...")
        
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
        
        add_log(f"📊 프롬프트 길이: {len(prompt):,} 글자")
        add_log("🔑 사용자 API 키로 Gemini AI를 설정합니다...")
        
        # 사용자 API 키로 Gemini 설정
        genai.configure(api_key=api_key)
        
        add_log("🤖 Gemini 2.0 Flash 모델로 보고서 생성을 요청합니다...")
        add_log("⏳ AI가 보고서를 생성하는 동안 잠시 기다려주세요...")
        
        # Gemini API 호출
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt)
        
        add_log("✅ Gemini AI로부터 응답을 받았습니다!")
        add_log(f"📄 생성된 보고서 길이: {len(response.text):,} 글자")
        
        return response.text
        
    except Exception as e:
        raise Exception(f"투자심사보고서 생성 실패: {str(e)}")

# 메인 앱
def main_app():
    # 헤더
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown("""
        <div class="main-header">
            <h1>📊 IR 투자심사보고서 분석기</h1>
            <p>AI 기반 투자심사보고서 자동 생성 시스템</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)  # 정렬을 위한 공간
        if st.button("🚪 로그아웃", type="secondary"):
            logout()

# 로그인 여부에 따른 페이지 분기
if not st.session_state.logged_in:
    login_page()
else:
    main_app()
    
    # 사이드바 설정
    with st.sidebar:
        st.header("⚙️ 설정")
        st.success(f"✅ 로그인됨 ({st.session_state.api_key[:8]}...)")
        st.info("💡 **사용법**\n\n1. 회사명을 입력하세요\n2. IR 자료를 업로드하거나 URL을 입력하세요\n3. '분석하기' 버튼을 클릭하세요")

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
        progress_placeholder = st.empty()
        log_placeholder = st.empty()
        
        with status_placeholder.container():
            st.info("⏳ 분석 대기 중...")
        
        # 로그 표시 함수
        def update_log(message, level="info"):
            timestamp = datetime.now().strftime("%H:%M:%S")
            if 'logs' not in st.session_state:
                st.session_state.logs = []
            
            st.session_state.logs.append(f"[{timestamp}] {message}")
            
            # 최근 10개 로그만 유지
            if len(st.session_state.logs) > 10:
                st.session_state.logs = st.session_state.logs[-10:]
            
            with log_placeholder.container():
                st.markdown("### 📋 진행 로그")
                for log in st.session_state.logs:
                    if "✅" in log or "완료" in log:
                        st.success(log)
                    elif "⚠️" in log or "진행" in log:
                        st.warning(log)
                    elif "❌" in log or "실패" in log:
                        st.error(log)
                    else:
                        st.info(log)
        
        def update_progress(current_step, total_steps, step_name):
            progress = current_step / total_steps
            with progress_placeholder.container():
                st.progress(progress)
                st.write(f"**단계 {current_step}/{total_steps}**: {step_name}")
        
        # 세션 상태 초기화
        if 'logs' not in st.session_state:
            st.session_state.logs = []

    # 분석 실행 버튼
    if st.button("🚀 투자심사보고서 생성하기", type="primary"):
        if not company_name:
            st.error("❌ 회사명을 입력해주세요")
        elif not uploaded_file and not ir_url:
            st.error("❌ IR 자료를 업로드하거나 URL을 입력해주세요")
        else:
            # 로그 초기화
            st.session_state.logs = []
            
            # 분석 실행
            try:
                # 1단계: 초기화
                update_progress(1, 5, "분석 초기화")
                update_log("🚀 투자심사보고서 생성을 시작합니다.")
                update_log(f"📊 분석 대상: {company_name}")
                
                with status_placeholder.container():
                    st.warning("🔄 분석 진행 중...")
                
                # 2단계: IR 자료 처리
                update_progress(2, 5, "IR 자료 처리 중")
                
                if uploaded_file:
                    update_log(f"📎 파일 업로드 확인: {uploaded_file.name} ({uploaded_file.size:,} bytes)")
                    update_log("⚙️ 파일 처리를 시작합니다...")
                    ir_summary = process_uploaded_file(uploaded_file)
                    update_log("✅ 파일 처리가 완료되었습니다.")
                else:
                    update_log(f"🔗 URL 자료 다운로드: {ir_url}")
                    update_log("⚙️ URL에서 데이터를 다운로드하고 있습니다...")
                    ir_summary = download_and_extract_ir(ir_url)
                    update_log("✅ URL 자료 다운로드가 완료되었습니다.")
                
                # 3단계: 학습 데이터 로드
                update_progress(3, 5, "학습 데이터 로드 중")
                update_log("📚 JSONL 학습 데이터를 로드하고 있습니다...")
                
                # 4단계: AI 보고서 생성
                update_progress(4, 5, "AI 보고서 생성 중")
                update_log("🤖 Gemini AI를 사용하여 투자심사보고서를 생성하고 있습니다...")
                update_log("⏱️ 이 과정은 30초~2분 정도 소요될 수 있습니다.")
                
                # 투자심사보고서 생성 (session state의 API 키 사용)
                investment_report = generate_investment_report(ir_summary, company_name, st.session_state.api_key)
                
                # 결과를 session state에 저장
                st.session_state.investment_report = investment_report
                st.session_state.ir_summary = ir_summary
                st.session_state.company_name = company_name
                st.session_state.analysis_complete = True
                
                # 5단계: 완료
                update_progress(5, 5, "분석 완료")
                update_log("✅ 투자심사보고서 생성이 완료되었습니다!")
                update_log(f"📄 보고서 길이: {len(investment_report):,} 글자")
                
                # 결과 표시
                with status_placeholder.container():
                    st.success("✅ 분석 완료!")
                
                # 페이지 새로고침하여 결과 표시
                st.rerun()
                
            except Exception as e:
                update_log(f"❌ 오류 발생: {str(e)}")
                with status_placeholder.container():
                    st.error(f"❌ 분석 실패: {str(e)}")
                st.error(f"분석 중 오류가 발생했습니다: {str(e)}")
    
    # 분석 완료 결과가 있을 때 전체 화면에 표시
    if st.session_state.analysis_complete and st.session_state.investment_report:
        st.markdown("---")
        st.markdown("""
        <div class="result-section">
            <h2>📋 투자심사보고서 생성 완료</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # 새 분석 시작 버튼을 상단에 배치
        col_reset1, col_reset2, col_reset3 = st.columns([1, 1, 1])
        with col_reset2:
            if st.button("🔄 새 분석 시작", type="secondary"):
                # 분석 결과 초기화
                st.session_state.analysis_complete = False
                st.session_state.investment_report = ""
                st.session_state.ir_summary = ""
                st.session_state.company_name = ""
                if 'logs' in st.session_state:
                    st.session_state.logs = []
                st.rerun()
        
        # 결과 탭 (전체 화면에 표시)
        tab1, tab2, tab3 = st.tabs(["📊 투자심사보고서", "📁 원본 자료", "🔍 처리 로그"])
        
        with tab1:
            st.markdown(f"## 🏢 {st.session_state.company_name} 투자심사보고서")
            st.markdown("---")
            st.markdown(st.session_state.investment_report)
            
            # 다운로드 버튼
            st.download_button(
                label="💾 보고서 다운로드 (텍스트)",
                data=st.session_state.investment_report,
                file_name=f"{st.session_state.company_name}_투자심사보고서_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                type="primary",
                use_container_width=True
            )
        
        with tab2:
            st.markdown("## 📄 원본 IR 자료 요약")
            st.text_area(
                "원본 자료", 
                value=st.session_state.ir_summary[:5000] + "..." if len(st.session_state.ir_summary) > 5000 else st.session_state.ir_summary, 
                height=400,
                disabled=True
            )
            
            # 원본 자료 다운로드
            st.download_button(
                label="💾 원본 자료 다운로드",
                data=st.session_state.ir_summary,
                file_name=f"{st.session_state.company_name}_원본자료_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with tab3:
            st.markdown("## 🔍 상세 처리 로그")
            if 'logs' in st.session_state and st.session_state.logs:
                for log in st.session_state.logs:
                    if "✅" in log or "완료" in log:
                        st.success(log)
                    elif "⚠️" in log or "진행" in log or "⏱️" in log:
                        st.warning(log)
                    elif "❌" in log or "실패" in log:
                        st.error(log)
                    else:
                        st.info(log)
            else:
                st.info("처리 로그가 없습니다.")

# 푸터
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🤖 AI 기반 IR 투자심사보고서 분석기 | Made with Streamlit</p>
    <p>📧 문의사항이 있으시면 언제든 연락주세요</p>
</div>
""", unsafe_allow_html=True)
