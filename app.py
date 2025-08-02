import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import os
from dotenv import load_dotenv
import tempfile
from datetime import datetime
import json

# 환경변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="IR Pro - 전문 투자심사보고서 분석 플랫폼",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Session state 초기화
if 'api_key' not in st.session_state:
    st.session_state.api_key = os.getenv('GOOGLE_API_KEY', '')
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def load_html_template():
    """HTML 템플릿 로드"""
    try:
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None

def validate_api_key(api_key):
    """API 키 유효성 검사"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Hello")
        return True
    except Exception as e:
        return False

def process_uploaded_file(file_content, filename):
    """업로드된 파일 처리"""
    try:
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{filename.split('.')[-1]}") as tmp_file:
            tmp_file.write(file_content)
            tmp_file_path = tmp_file.name
        
        # 파일 확장자에 따른 처리
        file_ext = filename.lower().split('.')[-1]
        
        if file_ext == 'pdf':
            try:
                from pdf_processor import PDFProcessor
                processor = PDFProcessor()
                pdf_result = processor.extract_text_from_bytes(file_content)
                
                if pdf_result["success"]:
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
            except ImportError:
                return f"""
=== IR 자료 분석 원본 데이터 ===

📊 파일 정보:
- 파일명: {filename}
- 파일 크기: {len(file_content):,} bytes
- 파일 형식: PDF

📄 파일 내용:
PDF 파일이 업로드되었습니다.
PDF 처리 모듈을 설치해주세요: pip install PyPDF2

=== 분석 요청 ===
위의 IR 자료를 바탕으로 투자심사보고서를 작성해주세요.
"""
        
        return f"""
=== IR 자료 분석 원본 데이터 ===

📊 파일 정보:
- 파일명: {filename}
- 파일 크기: {len(file_content):,} bytes
- 파일 형식: {file_ext.upper()}

📄 파일 내용:
{file_ext.upper()} 파일이 업로드되었습니다.
파일 처리 기능을 구현 중입니다.

=== 분석 요청 ===
위의 IR 자료를 바탕으로 투자심사보고서를 작성해주세요.
"""
            
    except Exception as e:
        raise Exception(f"파일 처리 실패: {str(e)}")
    finally:
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
    """투자심사보고서 생성"""
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

당신은 대한민국 최고의 임팩트 투자사에서 근무하는 선임 심사역입니다. 주어진 IR 자료를 바탕으로 내부투자심의위원회에 상정할 상세하고 설득력 있는 '투자심사보고서' 초안을 작성하세요.

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
        
        # 사용자 API 키로 Gemini 설정
        genai.configure(api_key=api_key)
        
        # Gemini API 호출
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        return response.text
        
    except Exception as e:
        raise Exception(f"투자심사보고서 생성 실패: {str(e)}")

# API 엔드포인트 처리
def check_authentication():
    """인증 상태 확인"""
    valid_api_key = "AIzaSyDF845d0PrBSyB92AJ1e8etEo0BDdmbNoY"
    
    # URL 파라미터에서 인증 정보 확인
    query_params = st.query_params
    if query_params.get("authenticated") == "true" and query_params.get("api_key") == valid_api_key:
        st.session_state.authenticated = True
        st.session_state.api_key = valid_api_key
        return True
    
    # 세션 상태 확인
    if st.session_state.get('authenticated') and st.session_state.get('api_key') == valid_api_key:
        return True
    
    return False

def load_login_template():
    """로그인 HTML 템플릿 로드"""
    try:
        with open('templates/login.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None

def handle_api_request():
    """API 요청 처리"""
    query_params = st.query_params
    
    if query_params.get("api") == "analyze-ir-file":
        # 파일 업로드 분석 API
        return {"type": "file_upload", "endpoint": "/api/analyze-ir-file"}
    elif query_params.get("api") == "analyze-ir":
        # URL 분석 API
        return {"type": "url_analysis", "endpoint": "/api/analyze-ir"}
    
    return None

# 인증 확인
if not check_authentication():
    # 로그인 페이지 표시
    login_template = load_login_template()
    if login_template:
        components.html(login_template, height=800, scrolling=True)
    else:
        st.error("❌ 로그인 페이지를 로드할 수 없습니다.")
        st.info("templates/login.html 파일이 존재하는지 확인해주세요.")
    st.stop()

# API 키 확인
api_key = st.session_state.api_key
if not api_key:
    api_key = os.getenv('GOOGLE_API_KEY', '')

# HTML 템플릿 로드
html_template = load_html_template()

if html_template:
    # API 키가 있는 경우 HTML에 JavaScript로 전달
    if api_key:
        # HTML에 API 키 정보 주입 (보안상 실제 키는 숨김)
        html_template = html_template.replace(
            '<script>',
            f'''<script>
                window.APP_CONFIG = {{
                    hasApiKey: true,
                    apiKeyStatus: "configured"
                }};
            '''
        )
    
    # API 엔드포인트 처리를 위한 JavaScript 주입
    api_handler_js = '''
    <script>
    // API 요청 처리
    async function handleAnalysisRequest(formData, isFile = true) {
        try {
            const endpoint = isFile ? '/api/analyze-ir-file' : '/api/analyze-ir';
            
            // Streamlit으로 API 요청 시뮬레이션
            if (isFile) {
                // 파일 업로드 처리
                const file = formData.get('file');
                const companyName = formData.get('company_name');
                
                // Streamlit 세션에 데이터 전달
                window.parent.postMessage({
                    type: 'streamlit:file_upload',
                    file: file,
                    company_name: companyName
                }, '*');
                
            } else {
                // URL 분석 처리
                const data = JSON.parse(formData);
                
                window.parent.postMessage({
                    type: 'streamlit:url_analysis',
                    company_name: data.company_name,
                    ir_url: data.ir_url
                }, '*');
            }
            
            return { success: true, message: "분석 요청이 전송되었습니다." };
            
        } catch (error) {
            console.error('API 요청 오류:', error);
            return { success: false, error: error.message };
        }
    }
    
    // HTML 폼과 Streamlit 백엔드 연결
    document.addEventListener('DOMContentLoaded', function() {
        const analysisForm = document.getElementById('analysisForm');
        if (analysisForm) {
            analysisForm.addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const companyName = document.getElementById('companyName').value;
                const irUrl = document.getElementById('irUrl').value;
                const fileInput = document.getElementById('fileInput');
                const file = fileInput.files[0];
                
                if (!companyName) {
                    alert('회사명을 입력해주세요.');
                    return;
                }
                
                if (!file && !irUrl) {
                    alert('IR 자료 파일을 업로드하거나 URL을 입력해주세요.');
                    return;
                }
                
                // 로딩 상태 표시
                const progressContainer = document.getElementById('progressContainer');
                const analysisForm = document.getElementById('analysisForm');
                
                analysisForm.style.display = 'none';
                progressContainer.style.display = 'block';
                
                // 진행률 시뮬레이션
                simulateProgress();
                
                try {
                    let result;
                    if (file) {
                        const formData = new FormData();
                        formData.append('file', file);
                        formData.append('company_name', companyName);
                        result = await handleAnalysisRequest(formData, true);
                    } else {
                        const data = JSON.stringify({
                            company_name: companyName,
                            ir_url: irUrl,
                            analysis_type: 'investment_report'
                        });
                        result = await handleAnalysisRequest(data, false);
                    }
                    
                    if (result.success) {
                        // 성공 시 결과 표시는 Streamlit에서 처리
                        setTimeout(() => {
                            window.location.reload();
                        }, 3000);
                    } else {
                        showError(result.error || '분석 중 오류가 발생했습니다.');
                    }
                    
                } catch (error) {
                    console.error('분석 오류:', error);
                    showError('서버 연결에 실패했습니다. 잠시 후 다시 시도해주세요.');
                }
            });
        }
    });
    </script>
    '''
    
    # JavaScript를 HTML에 추가
    html_template = html_template.replace('</body>', f'{api_handler_js}</body>')
    
    # HTML 렌더링
    components.html(html_template, height=800, scrolling=True)
    

else:
    # HTML 템플릿을 찾을 수 없는 경우 기본 Streamlit UI
    st.error("❌ HTML 템플릿을 찾을 수 없습니다.")
    st.info("templates/index.html 파일이 존재하는지 확인해주세요.")
    
    # 기본 폴백 UI
    st.title("📊 IR 투자심사보고서 분석기")
    st.write("HTML 템플릿 로드 실패 - 기본 모드로 실행 중")
    
    # 간단한 분석 인터페이스
    company_name = st.text_input("회사명")
    uploaded_file = st.file_uploader("IR 파일 업로드", type=['pdf', 'xlsx', 'xls', 'docx', 'doc'])
    
    if st.button("분석하기") and company_name and uploaded_file:
        if api_key:
            try:
                # 파일 처리
                ir_summary = process_uploaded_file(uploaded_file.getvalue(), uploaded_file.name)
                
                # 보고서 생성
                report = generate_investment_report(ir_summary, company_name, api_key)
                
                st.success("분석 완료!")
                st.markdown("## 투자심사보고서")
                st.markdown(report)
                
            except Exception as e:
                st.error(f"분석 실패: {str(e)}")
        else:
            st.error("API 키를 설정해주세요.")
            new_api_key = st.text_input("Gemini API 키", type="password")
            if st.button("API 키 저장") and new_api_key:
                if validate_api_key(new_api_key):
                    st.session_state.api_key = new_api_key
                    st.success("API 키 저장 완료!")
                    st.rerun()
                else:
                    st.error("유효하지 않은 API 키입니다.")