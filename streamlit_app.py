import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import pandas as pd
from datetime import datetime
import time
import os

# 페이지 설정
st.set_page_config(
    page_title="MYSC IR Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일
st.markdown("""
<style>
    .main {
        padding-top: 0rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #0969da;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #0860ca;
        transform: translateY(-1px);
    }
    .success-box {
        padding: 1rem;
        border-radius: 8px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 8px;
        background-color: #e7f3ff;
        border: 1px solid #b3d9ff;
        color: #004085;
        margin: 1rem 0;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid #e5e5e5;
        text-align: center;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #0969da;
        margin: 0.5rem 0;
    }
    .metric-label {
        color: #666;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'api_key' not in st.session_state:
    st.session_state.api_key = None
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

# 헤더
st.title("🚀 MYSC IR Platform")
st.markdown("### AI 기반 투자 분석 플랫폼")

# 사이드바 - 로그인
with st.sidebar:
    st.markdown("### 🔐 인증")
    
    if not st.session_state.authenticated:
        api_key = st.text_input("Gemini API Key", type="password", help="Gemini API 키를 입력하세요")
        
        if st.button("로그인", use_container_width=True):
            if api_key and api_key.startswith("AIza"):
                st.session_state.api_key = api_key
                st.session_state.authenticated = True
                st.success("✅ 로그인 성공!")
                st.rerun()
            else:
                st.error("올바른 API 키를 입력해주세요")
    else:
        st.success(f"✅ 로그인됨")
        if st.button("로그아웃", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.api_key = None
            st.session_state.analysis_result = None
            st.rerun()

# 메인 컨텐츠
if st.session_state.authenticated:
    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["📄 문서 분석", "📊 분석 결과", "ℹ️ 사용 가이드"])
    
    with tab1:
        st.markdown("### 투자 문서 분석")
        
        # 회사명 입력
        company_name = st.text_input("회사명", placeholder="분석할 회사명을 입력하세요")
        
        # 파일 업로드
        uploaded_files = st.file_uploader(
            "IR 문서 업로드",
            accept_multiple_files=True,
            type=['pdf', 'xlsx', 'docx'],
            help="PDF, Excel, Word 파일을 업로드하세요 (최대 200MB)"
        )
        
        if uploaded_files:
            st.info(f"📁 {len(uploaded_files)}개 파일 업로드됨")
            for file in uploaded_files:
                st.write(f"- {file.name} ({file.size/1024/1024:.1f}MB)")
        
        # 분석 버튼
        if st.button("🔍 VC급 투자 분석 시작", use_container_width=True, disabled=not (company_name and uploaded_files)):
            with st.spinner("🤖 AI가 문서를 분석하고 있습니다..."):
                try:
                    # 진행 상황 표시
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Stage 1: 파일 읽기
                    status_text.text("📄 문서 내용 추출 중...")
                    progress_bar.progress(20)
                    
                    all_text = ""
                    for file in uploaded_files:
                        if file.type == "application/pdf":
                            pdf_reader = PdfReader(file)
                            for page in pdf_reader.pages:
                                all_text += page.extract_text() + "\n"
                    
                    time.sleep(1)
                    
                    # Stage 2: Gemini 분석
                    status_text.text("🧠 AI 심화 분석 진행 중...")
                    progress_bar.progress(60)
                    
                    # Gemini 설정
                    genai.configure(api_key=st.session_state.api_key)
                    model = genai.GenerativeModel('gemini-2.0-flash-exp')
                    
                    # VC급 프롬프트
                    prompt = f"""VC 파트너로서 {company_name}의 Investment Thesis Memo 작성:

분석할 문서:
{all_text[:30000]}

다음 구조로 상세히 작성:

# Executive Summary
- 핵심 투자 논지 (1-2문장)
- 투자 추천 점수: X.X/10

## 1. 투자 개요
### 1.1 기업 개요
### 1.2 투자 조건

## 2. 기업 현황
### 2.1 사업 모델
### 2.2 핵심 경쟁력

## 3. 시장 분석
### 3.1 시장 규모 및 성장성
### 3.2 경쟁 환경

## 4. 투자 포인트
### 4.1 강점 (3-5개)
### 4.2 리스크 (3-5개)

## 5. Exit 전략

## 6. 종합 추천
- Buy/Hold/Pass 중 선택
- 핵심 근거 3줄 요약
"""
                    
                    response = model.generate_content(prompt)
                    result = response.text
                    
                    # Stage 3: 완료
                    status_text.text("✅ 분석 완료!")
                    progress_bar.progress(100)
                    time.sleep(1)
                    
                    # 결과 저장
                    st.session_state.analysis_result = {
                        'company': company_name,
                        'report': result,
                        'timestamp': datetime.now(),
                        'files': [f.name for f in uploaded_files]
                    }
                    
                    # 결과 탭으로 이동
                    st.success("✅ 분석이 완료되었습니다! '분석 결과' 탭에서 확인하세요.")
                    
                except Exception as e:
                    st.error(f"❌ 분석 중 오류 발생: {str(e)}")
    
    with tab2:
        st.markdown("### 📊 투자 분석 결과")
        
        if st.session_state.analysis_result:
            result = st.session_state.analysis_result
            
            # 메타 정보
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**회사명:** {result['company']}")
            with col2:
                st.markdown(f"**분석 시간:** {result['timestamp'].strftime('%Y-%m-%d %H:%M')}")
            with col3:
                st.markdown(f"**분석 파일:** {len(result['files'])}개")
            
            st.divider()
            
            # 분석 결과 표시
            st.markdown(result['report'])
            
            # 다운로드 버튼
            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 보고서 다운로드 (TXT)",
                    data=result['report'],
                    file_name=f"{result['company']}_투자분석_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with col2:
                if st.button("🔄 새로운 분석", use_container_width=True):
                    st.session_state.analysis_result = None
                    st.rerun()
        else:
            st.info("📄 먼저 문서를 업로드하고 분석을 실행하세요.")
    
    with tab3:
        st.markdown("""
        ### 📖 사용 가이드
        
        #### 1. 로그인
        - 사이드바에 Gemini API 키 입력
        - API 키는 [Google AI Studio](https://makersuite.google.com/app/apikey)에서 발급
        
        #### 2. 문서 업로드
        - 회사명 입력
        - IR 문서 업로드 (PDF, Excel, Word)
        - 최대 200MB까지 지원
        
        #### 3. 분석 실행
        - 'VC급 투자 분석 시작' 버튼 클릭
        - 1-2분 대기
        
        #### 4. 결과 확인
        - '분석 결과' 탭에서 상세 보고서 확인
        - TXT 파일로 다운로드 가능
        
        #### 💡 특징
        - ✅ **무제한 실행 시간** (Streamlit Cloud)
        - ✅ **대용량 파일 지원** (200MB+)
        - ✅ **실시간 진행률 표시**
        - ✅ **VC급 심화 분석**
        """)
else:
    # 로그인 안내
    st.info("🔐 먼저 사이드바에서 Gemini API 키로 로그인하세요.")
    st.markdown("""
    ### 시작하기
    1. 좌측 사이드바에서 Gemini API 키 입력
    2. [Google AI Studio](https://makersuite.google.com/app/apikey)에서 API 키 발급
    3. 로그인 후 문서 분석 시작
    """)

# 푸터
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.8rem;'>
    MYSC IR Platform v2.0 | Powered by Gemini AI & Streamlit
</div>
""", unsafe_allow_html=True)