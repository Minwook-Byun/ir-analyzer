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
        jsonl_files = glob.glob(f"{self.jsonl_folder_path}/*.jsonl")
        
        print(f"발견된 JSONL 파일 수: {len(jsonl_files)}")
        
        for file_path in jsonl_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.learned_reports.append({
                        "filename": os.path.basename(file_path),
                        "company_name": data.get("report_meta", {}).get("company_name", "Unknown"),
                        "data": data
                    })
                    print(f"✅ 로드 완료: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"❌ 파일 로드 실패: {file_path}, 오류: {e}")
        
        return self.learned_reports
    
    def create_learning_context(self) -> str:
        """JSONL 데이터를 Gemini 학습용 컨텍스트로 변환"""
        if not self.learned_reports:
            self.load_all_jsonl_files()
        
        context = "=== 투자심사보고서 학습 데이터 ===\n\n"
        context += f"총 {len(self.learned_reports)}개의 기업 보고서를 학습했습니다.\n\n"
        
        # 각 기업별 핵심 정보 요약
        for i, report in enumerate(self.learned_reports, 1):
            company_name = report["company_name"]
            data = report["data"]
            
            context += f"[{i}] {company_name}\n"
            
            # 요약 정보
            if "executive_summary_data" in data:
                summary = data["executive_summary_data"]
                context += f"  • 정체성: {summary.get('identity_statement', 'N/A')}\n"
                context += f"  • 핵심 투자포인트: {len(summary.get('investment_highlights', []))}개\n"
            
            # 시장 정보
            if "market_and_business_analysis" in data:
                market = data["market_and_business_analysis"]["market_analysis"]
                context += f"  • TAM: {market.get('tam', {}).get('value_krw', 0):,}원\n"
                context += f"  • SAM: {market.get('sam', {}).get('value_krw', 0):,}원\n"
            
            # 투자 논리
            if "thesis_and_impact" in data:
                points = data["thesis_and_impact"]["investment_points"]
                context += f"  • 투자 포인트: {len(points)}개 (기술/시장/임팩트)\n"
            
            context += "\n"
        
        return context
    
    def get_report_structure_template(self) -> str:
        """학습된 보고서 구조를 템플릿으로 반환"""
        if not self.learned_reports:
            self.load_all_jsonl_files()
        
        # 첫 번째 보고서의 구조를 템플릿으로 사용
        if self.learned_reports:
            sample_data = self.learned_reports[0]["data"]
            
            template = """
# 투자심사보고서 구조 (학습된 템플릿)

## 1. Executive Summary
- identity_statement (기업 정체성)
- problem_and_solution (문제와 해결책)  
- investment_highlights (투자 하이라이트)
- expected_impact_summary (예상 임팩트)
- investment_terms_summary (투자 조건)

## 2. 기업 현황
- general_info_table (일반 현황)
- history (연혁)
- team (팀 구성)

## 3. 시장 및 사업 분석  
- market_analysis (TAM/SAM/SOM, 문제 정의)
- competitive_landscape (경쟁 환경)
- business_model (비즈니스 모델)

## 4. 투자 논리 및 임팩트 분석
- investment_points (핵심 투자 포인트: 기술/시장/임팩트)
- theory_of_change (변화이론)

## 5. 리스크 및 결론
- risk_factors (주요 리스크)
- overall_conclusion (종합 결론)
"""
            return template
        
        return "템플릿을 생성할 수 없습니다."
    
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
    