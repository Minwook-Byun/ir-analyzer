import PyPDF2
import requests
from io import BytesIO
from typing import Dict, Optional
import re

class PDFProcessor:
    def __init__(self):
        self.max_text_length = 15000  # Gemini API 토큰 제한 고려
    
    def extract_text_from_url(self, pdf_url: str) -> Dict[str, str]:
        """URL에서 PDF를 다운로드하고 텍스트 추출"""
        try:
            # PDF 다운로드
            print(f"📥 PDF 다운로드 중: {pdf_url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(pdf_url, timeout=60, headers=headers)
            response.raise_for_status()
            
            # PDF 텍스트 추출
            pdf_content = self.extract_text_from_bytes(response.content)
            
            return {
                "success": True,
                "url": pdf_url,
                "file_size": len(response.content),
                "extracted_text": pdf_content["text"],
                "page_count": pdf_content["page_count"],
                "company_info": self.extract_company_info(pdf_content["text"])
            }
            
        except Exception as e:
            print(f"❌ PDF 처리 실패: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "url": pdf_url
            }
    
    def extract_text_from_bytes(self, pdf_bytes: bytes) -> Dict:
        """바이트 데이터에서 PDF 텍스트 추출"""
        try:
            pdf_file = BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            page_count = len(pdf_reader.pages)
            
            print(f"📄 PDF 페이지 수: {page_count}")
            
            # 모든 페이지에서 텍스트 추출
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    # 페이지별 구분 추가
                    text += f"\n=== 페이지 {page_num + 1} ===\n"
                    text += page_text
                    
                    # 길이 제한 (Gemini API 토큰 제한)
                    if len(text) > self.max_text_length:
                        text = text[:self.max_text_length] + "\n[... 텍스트 길이 제한으로 중단 ...]"
                        print(f"⚠️ 텍스트 길이 제한: {self.max_text_length}자로 제한")
                        break
                        
                except Exception as e:
                    print(f"⚠️ 페이지 {page_num + 1} 처리 실패: {e}")
                    continue
            
            return {
                "text": text,
                "page_count": page_count,
                "success": True
            }
            
        except Exception as e:
            print(f"❌ PDF 바이트 처리 실패: {str(e)}")
            return {
                "text": "",
                "page_count": 0,
                "success": False,
                "error": str(e)
            }
    
    def extract_company_info(self, text: str) -> Dict[str, str]:
        """PDF 텍스트에서 기업 기본 정보 추출"""
        company_info = {}
        
        # 회사명 추출 (다양한 패턴)
        company_patterns = [
            r'주식회사\s*([가-힣A-Za-z0-9\s]+)',
            r'㈜\s*([가-힣A-Za-z0-9\s]+)',
            r'농업회사법인\s*([가-힣A-Za-z0-9\s]+)',
            r'회사명[:\s]*([가-힣A-Za-z0-9\s]+)',
            r'기업명[:\s]*([가-힣A-Za-z0-9\s]+)',
            r'법인명[:\s]*([가-힣A-Za-z0-9\s]+)'
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, text)
            if match:
                company_name = match.group(1).strip()
                # 불필요한 단어 제거
                company_name = re.sub(r'(투자심사보고서|보고서|IR|자료)', '', company_name).strip()
                if len(company_name) > 1:  # 의미있는 길이인지 확인
                    company_info["company_name"] = company_name
                    break
        
        # 사업 분야 추출
        business_keywords = ["사업", "분야", "업종", "사업영역", "주요사업", "서비스", "제품"]
        for keyword in business_keywords:
            pattern = f'{keyword}[:\s]*([가-힣A-Za-z0-9\s,·]+)'
            match = re.search(pattern, text)
            if match:
                business_area = match.group(1).strip()[:200]  # 길이 제한
                company_info["business_area"] = business_area
                break
        
        # 설립년도 추출
        year_patterns = [
            r'설립[:\s]*(\d{4})',
            r'창립[:\s]*(\d{4})',
            r'(\d{4})년?\s*설립',
            r'(\d{4})년?\s*창립'
        ]
        
        for pattern in year_patterns:
            match = re.search(pattern, text)
            if match:
                year = match.group(1)
                if 1900 <= int(year) <= 2025:  # 유효한 년도인지 확인
                    company_info["founded_year"] = year
                    break
        
        # 매출액 추출
        revenue_patterns = [
            r'매출액[:\s]*([0-9,]+)\s*억',
            r'매출[:\s]*([0-9,]+)\s*억원',
            r'매출[:\s]*([0-9,]+)\s*백만원'
        ]
        
        for pattern in revenue_patterns:
            match = re.search(pattern, text)
            if match:
                revenue = match.group(1).replace(',', '')
                company_info["revenue"] = revenue
                break
        
        return company_info
    
    def create_ir_summary(self, extracted_data: Dict) -> str:
        """추출된 데이터를 요약하여 Gemini에 전달할 형태로 변환"""
        if not extracted_data["success"]:
            return f"PDF 처리 실패: {extracted_data.get('error', '알 수 없는 오류')}"
        
        summary = f"""
=== IR 자료 분석 원본 데이터 ===

📊 파일 정보:
- URL: {extracted_data['url']}
- 파일 크기: {extracted_data['file_size']:,} bytes
- 페이지 수: {extracted_data['page_count']}페이지

🏢 추출된 기업 정보:
"""
        
        company_info = extracted_data['company_info']
        if company_info.get('company_name'):
            summary += f"- 회사명: {company_info['company_name']}\n"
        if company_info.get('business_area'):
            summary += f"- 사업 분야: {company_info['business_area']}\n"
        if company_info.get('founded_year'):
            summary += f"- 설립년도: {company_info['founded_year']}\n"
        if company_info.get('revenue'):
            summary += f"- 매출액: {company_info['revenue']}\n"
        
        summary += f"""
📄 PDF 원문 내용:
{extracted_data['extracted_text']}

=== 분석 요청 ===
위의 IR 자료를 바탕으로 투자심사보고서를 작성해주세요.
"""
        
        return summary

# 테스트 함수
def test_pdf_processor():
    processor = PDFProcessor()
    
    print("=== PDF 처리기 테스트 ===")
    
    # 테스트용 URL (실제 사용 시 교체)
    test_urls = [
        "https://example.com/sample.pdf",  # 실제 URL로 교체
        # 더 많은 테스트 URL 추가 가능
    ]
    
    for url in test_urls:
        print(f"\n📋 테스트 URL: {url}")
        result = processor.extract_text_from_url(url)
        
        if result["success"]:
            print(f"✅ PDF 처리 성공!")
            print(f"📄 페이지 수: {result['page_count']}")
            print(f"📝 추출된 텍스트 길이: {len(result['extracted_text'])} 글자")
            print(f"🏢 회사 정보: {result['company_info']}")
        else:
            print(f"❌ PDF 처리 실패: {result['error']}")
    
    return processor

if __name__ == "__main__":
    test_pdf_processor()
    