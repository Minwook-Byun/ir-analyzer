import json
import os
from typing import List, Dict
import glob

class JSONLProcessor:
    def __init__(self, jsonl_folder_path: str = None):
        # 환경변수에서 경로 가져오기 (보안)
        self.jsonl_folder_path = jsonl_folder_path or os.getenv("JSONL_DATA_PATH", "./jsonl_data")
        self.learned_reports = []
        self.is_production = os.getenv("ENVIRONMENT") == "production"
    
    def load_all_jsonl_files(self) -> List[Dict]:
        """모든 JSONL 파일을 로드하여 학습 데이터로 변환"""
        print(f"JSONL 폴더 경로: {self.jsonl_folder_path}")
        
        # 폴더 존재 확인
        if not os.path.exists(self.jsonl_folder_path):
            print(f"[ERROR] JSONL 폴더가 존재하지 않습니다: {self.jsonl_folder_path}")
            return []
        
        # .jsonl과 .json 파일 모두 검색
        jsonl_files = glob.glob(f"{self.jsonl_folder_path}/*.jsonl") + glob.glob(f"{self.jsonl_folder_path}/*.json")
        print(f"발견된 JSONL 파일 수: {len(jsonl_files)}")
        
        for file_path in jsonl_files:
            try:
                print(f"[INFO] 파일 로드 시도: {file_path}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    # JSON 파싱 시도 - 첫 번째 유효한 JSON 객체까지만 파싱
                    try:
                        data = json.loads(content)
                    except json.JSONDecodeError as e:
                        # 에러 위치까지만 잘라서 다시 시도
                        error_pos = e.pos if hasattr(e, 'pos') else len(content)
                        content_truncated = content[:error_pos]
                        # 마지막 완전한 } 까지 찾기
                        last_brace = content_truncated.rfind('}')
                        if last_brace > 0:
                            content_clean = content_truncated[:last_brace+1]
                            data = json.loads(content_clean)
                        else:
                            raise e
                    
                    self.learned_reports.append({
                        "filename": os.path.basename(file_path),
                        "company_name": data.get("report_meta", {}).get("company_name", "Unknown"),
                        "data": data
                    })
                    print(f"[SUCCESS] 로드 완료: {os.path.basename(file_path)}")
            except json.JSONDecodeError as e:
                print(f"[ERROR] JSON 파싱 오류: {file_path}, 오류: {e}")
                print(f"[INFO] 파일 길이: {len(content) if 'content' in locals() else 'unknown'}")
            except Exception as e:
                print(f"[ERROR] 파일 로드 실패: {file_path}, 오류: {e}")
        
        return self.learned_reports
    
    def create_learning_context(self) -> str:
        """JSONL 데이터를 Gemini 학습용 컨텍스트로 변환"""
        if not self.learned_reports:
            self.load_all_jsonl_files()
        
        if not self.learned_reports:
            return "=== 학습 데이터 없음 ===\n학습할 투자심사보고서 데이터가 없습니다."
        
        context = "=== 투자심사보고서 학습 데이터 ===\n\n"
        context += f"총 {len(self.learned_reports)}개의 기업 보고서를 학습했습니다.\n\n"
        
        # 각 기업별 핵심 정보 요약
        for i, report in enumerate(self.learned_reports, 1):
            company_name = report["company_name"]
            data = report["data"]
            
            context += f"[학습사례 {i}] {company_name}\n"
            
            # Executive Summary 정보
            if "executive_summary_data" in data:
                summary = data["executive_summary_data"]
                context += f"  - 정체성: {summary.get('identity_statement', 'N/A')[:100]}...\n"
                context += f"  - 문제와 해결책: {summary.get('problem_and_solution', 'N/A')[:150]}...\n"
                
                if 'investment_highlights' in summary:
                    highlights = summary['investment_highlights']
                    context += f"  - 투자 하이라이트 ({len(highlights)}개):\n"
                    for j, highlight in enumerate(highlights[:3], 1):  # 최대 3개만
                        if isinstance(highlight, str):
                            context += f"    - {highlight[:80]}...\n"
                        else:
                            context += f"    - {highlight.get('title', f'포인트 {j}')}: {highlight.get('description', '')[:80]}...\n"
            
            # 시장 정보
            if "market_and_business_analysis" in data:
                market_data = data["market_and_business_analysis"]
                if "market_analysis" in market_data:
                    market = market_data["market_analysis"]
                    tam = market.get('tam', {}).get('value_krw', 0)
                    sam = market.get('sam', {}).get('value_krw', 0)
                    if tam > 0:
                        context += f"  - TAM: {tam:,}원\n"
                    if sam > 0:
                        context += f"  - SAM: {sam:,}원\n"
            
            # 투자 논리
            if "thesis_and_impact" in data:
                thesis = data["thesis_and_impact"]
                if "investment_points" in thesis:
                    points = thesis["investment_points"]
                    context += f"  - 투자 포인트: {len(points)}개\n"
                    for point in points[:2]:  # 최대 2개만
                        context += f"    - {point.get('category', '')}: {point.get('title', '')}\n"
            
            context += "\n"
        
        # 학습 패턴 요약
        context += "\n=== 학습된 보고서 작성 패턴 ===\n"
        context += "1. Executive Summary에서 문제 정의와 해결책을 명확히 제시\n"
        context += "2. 투자 하이라이트를 3-5개 핵심 포인트로 구조화\n"
        context += "3. 시장 분석에서 TAM/SAM 수치를 구체적으로 제시\n"
        context += "4. 투자 논리를 기술/시장/임팩트 관점으로 분류\n"
        context += "5. 전문적이면서도 이해하기 쉬운 비즈니스 언어 사용\n\n"
        
        return context
    
    def get_report_structure_template(self) -> str:
        """학습된 보고서 구조를 템플릿으로 반환"""
        if not self.learned_reports:
            self.load_all_jsonl_files()
        
        if not self.learned_reports:
            return "템플릿을 생성할 수 없습니다. 학습 데이터가 없습니다."
        
        # 실제 학습된 데이터 구조를 바탕으로 템플릿 생성
        sample_data = self.learned_reports[0]["data"]
        
        template = """
=== 투자심사보고서 작성 가이드 (학습된 구조) ===

아래는 실제 투자심사보고서에서 학습한 구조와 작성 방식입니다.

## 1. Executive Summary
### 작성 요소:
- **기업 정체성 (Identity Statement)**: 기업의 미션과 비전을 한 문장으로 명확히 표현
- **문제와 해결책 (Problem & Solution)**: 해결하고자 하는 문제와 기업의 솔루션을 구체적으로 서술
- **투자 하이라이트 (Investment Highlights)**: 3-5개의 핵심 투자 포인트를 제목과 설명으로 구조화
- **예상 임팩트 요약**: 사회적/환경적 임팩트의 정량적/정성적 효과
- **투자 조건 요약**: 투자 금액, 지분율, 사용 용도 등

## 2. 기업 현황 분석
### 작성 요소:
- **일반 현황**: 설립일, 본사 위치, 사업자등록번호, 대표자, 직원 수 등을 표 형태로 정리
- **연혁**: 주요 마일스톤을 시간순으로 나열 (설립, 주요 투자, 제품 출시, 인증 획득 등)
- **주주 현황**: 현재 주주 구성과 지분율
- **팀 구성**: 핵심 경영진과 주요 구성원의 배경과 역할

## 3. 시장 및 사업 분석
### 작성 요소:
- **시장 현황**: TAM/SAM/SOM 수치와 시장 성장률, 주요 트렌드
- **문제 정의**: 타겟 시장의 핵심 문제점과 기존 솔루션의 한계
- **경쟁 환경**: 직접/간접 경쟁사 분석과 차별화 포인트
- **비즈니스 모델**: 수익 구조와 고객 획득 전략

## 4. 투자 논리 및 임팩트
### 작성 요소:
- **핵심 투자 포인트**: 기술적 우위, 시장 기회, 임팩트 잠재력을 카테고리별로 분석
- **변화 이론 (Theory of Change)**: 투입 → 활동 → 산출 → 결과 → 임팩트의 논리적 연결고리
- **임팩트 측정**: 정량적 지표와 측정 방법론

## 5. 리스크 및 결론
### 작성 요소:
- **주요 리스크**: 기술, 시장, 운영, 규제 리스크와 완화 방안
- **종합 결론**: 투자 추천/보류/반대와 그 근거

### 작성 톤앤매너:
- 전문적이고 객관적인 비즈니스 언어 사용
- 데이터와 근거를 바탕으로 한 논리적 서술
- 긍정적 관점에서 리스크도 균형있게 제시
- 임팩트 투자 관점에서 사회적 가치 강조
"""
        return template
    
    def find_similar_companies(self, target_industry: str) -> List[Dict]:
        """타겟 산업과 유사한 기업들을 찾아서 참고용으로 반환"""
        similar_companies = []
        
        for report in self.learned_reports:
            # 간단한 키워드 매칭 (나중에 더 정교하게 개선 가능)
            company_info = str(report["data"]).lower()
            if target_industry.lower() in company_info:
                similar_companies.append({
                    "company_name": report["company_name"],
                    "filename": report["filename"]
                })
        
        return similar_companies

# 테스트 함수
def test_jsonl_processor():
    processor = JSONLProcessor()
    
    # JSONL 파일들 로드
    reports = processor.load_all_jsonl_files()
    print(f"\n총 {len(reports)}개 보고서 로드 완료")
    
    # 학습 컨텍스트 생성
    context = processor.create_learning_context()
    print("\n=== 학습 컨텍스트 미리보기 ===")
    print(context[:500] + "...")
    
    return processor

if __name__ == "__main__":
    test_jsonl_processor()
    