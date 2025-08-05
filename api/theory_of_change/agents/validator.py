"""
Validator Agent
experiment-tracker + finance-tracker의 전문성을 결합하여
가설 검증과 임팩트 측정 체계를 설계합니다.
"""

import google.generativeai as genai
from typing import Dict, Any


class Validator:
    """검증 및 측정 체계 설계 전문가"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    async def design_validation_framework(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """가설 검증과 임팩트 측정 체계 설계"""
        
        prompt = self._build_validation_prompt(strategy)
        
        try:
            response = self.model.generate_content(prompt)
            validation = self._parse_validation_response(response.text, strategy)
            return validation
            
        except Exception as e:
            print(f"Validation design 오류: {str(e)}")
            return self._get_default_validation(strategy)
    
    def _build_validation_prompt(self, strategy: Dict[str, Any]) -> str:
        """검증 체계 설계를 위한 프롬프트 구성"""
        
        core_hypothesis = strategy.get('intervention_logic', {}).get('core_hypothesis', '')
        target_outcome = strategy.get('intervention_logic', {}).get('target_outcome', '')
        
        return f"""
당신은 **Validation Framework Specialist**입니다. experiment-tracker와 finance-tracker의 전문성을 결합하여 가설 검증과 임팩트 측정을 위한 체계적인 프레임워크를 설계합니다.

## 검증 대상
### 핵심 가설
{core_hypothesis}

### 목표 성과
{target_outcome}

## 6가지 핵심 설계 영역
1. **Success Metrics Definition**: 성공 지표 정의와 측정 방법
2. **Experiment Design**: A/B 테스트와 실험 설계
3. **Data Collection Strategy**: 데이터 수집 전략과 도구
4. **Financial Tracking**: 재무 성과와 ROI 측정
5. **Impact Measurement**: 사회적 임팩트 측정 방법
6. **Iteration Framework**: 학습과 개선 체계

## 검증 체계 설계 결과 JSON 구조로 반환:
```json
{{
  "success_metrics": {{
    "quantitative": {{
      "target_participants": "참여자 목표 수",
      "service_count": "제공 서비스 수",
      "partnerships": "파트너십 수",
      "engagement_rate": "참여율 목표"
    }},
    "qualitative": {{
      "satisfaction_score": "만족도 점수 목표",
      "behavior_change": "행동 변화 지표",
      "community_impact": "지역사회 임팩트"
    }}
  }},
  "measurement_methods": {{
    "data_collection": {{
      "surveys": "설문조사 계획",
      "interviews": "인터뷰 계획",
      "observations": "관찰 조사 계획",
      "analytics": "데이터 분석 계획"
    }},
    "tracking_tools": ["도구 1", "도구 2", "도구 3"],
    "reporting_frequency": "보고 주기"
  }},
  "experiment_design": {{
    "hypothesis_tests": [
      {{
        "hypothesis": "검증할 가설",
        "test_method": "테스트 방법",
        "success_criteria": "성공 기준",
        "timeline": "실험 기간"
      }}
    ],
    "control_variables": ["통제 변수들"],
    "sample_size": "표본 크기 계획"
  }},
  "financial_framework": {{
    "budget_tracking": {{
      "cost_per_beneficiary": "수혜자당 비용",
      "operational_efficiency": "운영 효율성 지표",
      "roi_calculation": "ROI 계산 방법"
    }},
    "sustainability_metrics": {{
      "revenue_diversification": "수익 다각화 계획",
      "cost_optimization": "비용 최적화 전략",
      "funding_pipeline": "펀딩 파이프라인"
    }}
  }},
  "impact_assessment": {{
    "short_term": ["단기 임팩트 지표들"],
    "medium_term": ["중기 임팩트 지표들"],
    "long_term": ["장기 임팩트 지표들"],
    "measurement_timeline": "측정 일정"
  }}
}}
```

측정 가능하고 실행 가능한 검증 체계를 설계해주세요.
JSON 형태로만 응답하고, 다른 설명은 포함하지 마세요.
"""
    
    def _parse_validation_response(self, response_text: str, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Gemini 응답 파싱"""
        try:
            import json
            
            # JSON 블록 추출
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                parsed_data = json.loads(json_str)
                return parsed_data
            else:
                return self._get_default_validation(strategy)
                
        except Exception as e:
            print(f"Validation parsing 오류: {str(e)}")
            return self._get_default_validation(strategy)
    
    def _get_default_validation(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """기본 검증 체계 데이터 반환"""
        
        return {
            "success_metrics": {
                "quantitative": {
                    "target_participants": "100명",
                    "service_count": "5개 서비스",
                    "partnerships": "3개 파트너십",
                    "engagement_rate": "80%"
                },
                "qualitative": {
                    "satisfaction_score": "4.5/5.0",
                    "behavior_change": "긍정적 변화 70%",
                    "community_impact": "지역사회 인식 개선"
                }
            },
            "measurement_methods": {
                "data_collection": {
                    "surveys": "월별 만족도 조사",
                    "interviews": "심층 인터뷰 (분기별)",
                    "observations": "활동 참여 관찰",
                    "analytics": "플랫폼 사용 데이터 분석"
                },
                "tracking_tools": ["Google Analytics", "설문조사 도구", "데이터베이스"],
                "reporting_frequency": "월별 리포트"
            },
            "experiment_design": {
                "hypothesis_tests": [
                    {
                        "hypothesis": "교육 프로그램이 역량 향상에 효과적인가",
                        "test_method": "사전-사후 비교",
                        "success_criteria": "30% 이상 향상",
                        "timeline": "3개월"
                    }
                ],
                "control_variables": ["참여자 배경", "교육 기간", "강사 역량"],
                "sample_size": "최소 50명"
            },
            "financial_framework": {
                "budget_tracking": {
                    "cost_per_beneficiary": "수혜자당 50만원",
                    "operational_efficiency": "운영비 30% 이하",
                    "roi_calculation": "사회적 수익률 측정"
                },
                "sustainability_metrics": {
                    "revenue_diversification": "다양한 펀딩 소스 확보",
                    "cost_optimization": "효율성 개선 계획",
                    "funding_pipeline": "지속 가능한 자금 조달"
                }
            },
            "impact_assessment": {
                "short_term": ["참여율", "만족도", "기초 역량 향상"],
                "medium_term": ["행동 변화", "네트워크 확장", "자립도 향상"],
                "long_term": ["사회적 지위 개선", "지역사회 기여", "모델 확산"],
                "measurement_timeline": "분기별 평가"
            }
        }