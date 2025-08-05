"""
Context Analyzer Agent
analytics-reporter + trend-researcher의 전문성을 결합하여 
조직의 현재 상황과 변화 기회를 체계적으로 분석합니다.
"""

import google.generativeai as genai
from typing import Dict, Any, Optional


class ContextAnalyzer:
    """현황 분석과 기회 식별 전문가"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    async def analyze_organization_context(self, org_data: Dict[str, Any]) -> Dict[str, Any]:
        """조직의 현재 상황과 변화 기회를 분석"""
        
        prompt = self._build_context_analysis_prompt(org_data)
        
        try:
            response = self.model.generate_content(prompt)
            context_analysis = self._parse_context_response(response.text, org_data)
            return context_analysis
            
        except Exception as e:
            print(f"Context analysis 오류: {str(e)}")
            return self._get_default_context(org_data)
    
    def _build_context_analysis_prompt(self, org_data: Dict[str, Any]) -> str:
        """현황 분석을 위한 프롬프트 구성"""
        
        org_name = org_data.get('name', '조직')
        impact_focus = org_data.get('focus', '사회혁신')
        
        return f"""
당신은 **Context Analysis Specialist**입니다. analytics-reporter와 trend-researcher의 전문성을 결합하여 조직의 현재 상황과 변화 기회를 체계적으로 분석합니다.

## 분석 대상
- 조직명: {org_name}
- 임팩트 영역: {impact_focus}

## 6가지 핵심 분석 영역
1. **Current State Analysis**: 현재 조직의 상태와 성과
2. **Market Context**: 해당 임팩트 영역의 시장 상황과 기회
3. **Trend Integration**: 관련 트렌드와 타이밍 분석
4. **Stakeholder Mapping**: 주요 이해관계자 식별
5. **Resource Assessment**: 가용 자원과 제약사항
6. **Opportunity Prioritization**: 변화 기회의 우선순위

## 분석 결과 JSON 구조로 반환:
```json
{{
  "current_state": {{
    "mission": "조직의 미션 (한 문장)",
    "vision": "조직의 비전 (한 문장)", 
    "team_size": "추정 팀 규모",
    "funding": "자금 현황 추정",
    "funding_desc": "자금 관련 상세 설명"
  }},
  "market_context": {{
    "market_size": "{impact_focus} 시장 규모 추정",
    "growth_trend": "성장 트렌드 분석",
    "key_opportunities": ["기회 1", "기회 2", "기회 3"]
  }},
  "stakeholders": {{
    "primary": ["핵심 이해관계자들"],
    "secondary": ["2차 이해관계자들"],
    "influencers": ["의사결정 영향자들"]
  }},
  "resources": {{
    "technology": "필요한 기술 자원",
    "tech_desc": "기술 자원 설명",
    "key_constraints": ["주요 제약사항들"],
    "competitive_advantages": ["경쟁 우위 요소들"]
  }},
  "opportunities": {{
    "high_priority": ["높은 우선순위 기회들"],
    "medium_priority": ["중간 우선순위 기회들"],
    "timing_factors": ["타이밍 고려사항들"]
  }}
}}
```

{impact_focus} 영역의 전문가로서 현실적이고 구체적인 분석을 제공해주세요.
JSON 형태로만 응답하고, 다른 설명은 포함하지 마세요.
"""
    
    def _parse_context_response(self, response_text: str, org_data: Dict[str, Any]) -> Dict[str, Any]:
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
                return self._get_default_context(org_data)
                
        except Exception as e:
            print(f"Context parsing 오류: {str(e)}")
            return self._get_default_context(org_data)
    
    def _get_default_context(self, org_data: Dict[str, Any]) -> Dict[str, Any]:
        """기본 컨텍스트 데이터 반환"""
        org_name = org_data.get('name', '조직')
        impact_focus = org_data.get('focus', '사회혁신')
        
        return {
            "current_state": {
                "mission": f"{org_name}의 {impact_focus}을 통한 사회적 가치 창출",
                "vision": "지속가능한 사회 변화 실현",
                "team_size": "10명",
                "funding": "초기 자금 확보 필요",
                "funding_desc": "프로젝트 시작을 위한 기본 운영 자금"
            },
            "market_context": {
                "market_size": f"{impact_focus} 시장 분석 필요",
                "growth_trend": "성장 가능성 높음",
                "key_opportunities": ["디지털 전환", "파트너십 구축", "정책 지원 활용"]
            },
            "stakeholders": {
                "primary": ["수혜자", "파트너 기관", "후원자"],
                "secondary": ["지역사회", "정부기관", "미디어"],
                "influencers": ["전문가", "오피니언 리더", "정책결정자"]
            },
            "resources": {
                "technology": "디지털 플랫폼",
                "tech_desc": "온라인 서비스 제공을 위한 기술 인프라",
                "key_constraints": ["예산 제약", "인력 부족", "시장 진입 장벽"],
                "competitive_advantages": ["전문성", "네트워크", "혁신적 접근"]
            },
            "opportunities": {
                "high_priority": ["핵심 서비스 개발", "파트너십 구축"],
                "medium_priority": ["마케팅 확대", "기술 고도화"],
                "timing_factors": ["시장 준비도", "정책 환경", "경쟁 상황"]
            }
        }