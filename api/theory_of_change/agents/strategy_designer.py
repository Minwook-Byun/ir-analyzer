"""
Strategy Designer Agent
sprint-prioritizer + studio-producer의 전문성을 결합하여
실행 가능한 변화이론 전략을 수립합니다.
"""

import google.generativeai as genai
from typing import Dict, Any


class StrategyDesigner:
    """실행 전략 설계 전문가"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    async def design_intervention_logic(
        self, 
        context: Dict[str, Any], 
        user_insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """실행 가능한 개입 논리와 전략 설계"""
        
        prompt = self._build_strategy_prompt(context, user_insights)
        
        try:
            response = self.model.generate_content(prompt)
            strategy = self._parse_strategy_response(response.text, context, user_insights)
            return strategy
            
        except Exception as e:
            print(f"Strategy design 오류: {str(e)}")
            return self._get_default_strategy(context, user_insights)
    
    def _build_strategy_prompt(self, context: Dict[str, Any], user_insights: Dict[str, Any]) -> str:
        """전략 설계를 위한 프롬프트 구성"""
        
        mission = context.get('current_state', {}).get('mission', '사회적 가치 창출')
        opportunities = context.get('opportunities', {}).get('high_priority', [])
        user_needs = user_insights.get('key_insights', {}).get('primary_needs', [])
        
        return f"""
당신은 **Strategy Design Specialist**입니다. sprint-prioritizer와 studio-producer의 전문성을 결합하여 실행 가능한 변화이론 전략을 수립합니다.

## 입력 정보
### 조직 미션
{mission}

### 핵심 기회
{', '.join(opportunities) if opportunities else '기회 분석 필요'}

### 사용자 핵심 니즈
{', '.join(user_needs) if user_needs else '니즈 분석 필요'}

## 6가지 핵심 설계 영역
1. **Intervention Logic**: 변화를 만들어낼 핵심 개입 논리
2. **Activity Design**: 구체적 활동과 프로그램 설계
3. **Resource Allocation**: 효율적 자원 배분 전략
4. **Timeline Planning**: 단계별 실행 일정
5. **Partnership Strategy**: 핵심 파트너십 전략
6. **Risk Mitigation**: 위험 요소 완화 방안

## 전략 설계 결과 JSON 구조로 반환:
```json
{{
  "intervention_logic": {{
    "core_hypothesis": "핵심 가설 (한 문장)",
    "change_mechanism": "변화 메커니즘 설명",
    "target_outcome": "목표하는 변화",
    "success_indicators": ["성공 지표 1", "성공 지표 2"]
  }},
  "key_activities": {{
    "education_programs": "교육 프로그램 계획",
    "education_desc": "교육 프로그램 상세 설명",
    "platform_dev": "플랫폼 개발 계획",
    "platform_desc": "플랫폼 관련 상세 설명",
    "outreach": "아웃리치 활동 계획",
    "outreach_desc": "아웃리치 활동 상세 설명"
  }},
  "resource_strategy": {{
    "budget_allocation": {{
      "programs": "프로그램 예산 비율",
      "operations": "운영 예산 비율",
      "marketing": "마케팅 예산 비율"
    }},
    "team_structure": {{
      "core_team": "핵심 팀 구성",
      "advisors": "자문단 구성",
      "volunteers": "자원봉사자 활용"
    }}
  }},
  "implementation_plan": {{
    "phase1": "1단계 (1-3개월) 주요 활동",
    "phase2": "2단계 (4-6개월) 주요 활동", 
    "phase3": "3단계 (7-12개월) 주요 활동",
    "milestones": ["주요 마일스톤 1", "주요 마일스톤 2"]
  }},
  "partnership_strategy": {{
    "strategic_partners": ["전략적 파트너 1", "전략적 파트너 2"],
    "funding_sources": ["펀딩 소스 1", "펀딩 소스 2"],
    "collaboration_models": ["협력 모델 1", "협력 모델 2"]
  }}
}}
```

실행 가능하고 현실적인 전략을 설계해주세요.
JSON 형태로만 응답하고, 다른 설명은 포함하지 마세요.
"""
    
    def _parse_strategy_response(
        self, 
        response_text: str, 
        context: Dict[str, Any], 
        user_insights: Dict[str, Any]
    ) -> Dict[str, Any]:
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
                return self._get_default_strategy(context, user_insights)
                
        except Exception as e:
            print(f"Strategy parsing 오류: {str(e)}")
            return self._get_default_strategy(context, user_insights)
    
    def _get_default_strategy(self, context: Dict[str, Any], user_insights: Dict[str, Any]) -> Dict[str, Any]:
        """기본 전략 데이터 반환"""
        
        return {
            "intervention_logic": {
                "core_hypothesis": "체계적 지원을 통해 대상 그룹의 역량과 기회를 확대할 수 있다",
                "change_mechanism": "교육-실습-네트워킹-지원의 통합적 접근",
                "target_outcome": "개인 역량 향상과 사회적 연결망 확대",
                "success_indicators": ["참여율 증가", "역량 향상", "네트워크 확장"]
            },
            "key_activities": {
                "education_programs": "맞춤형 교육과정 개발",
                "education_desc": "대상별 특성을 고려한 단계적 교육 프로그램",
                "platform_dev": "온라인 서비스 플랫폼 구축",
                "platform_desc": "접근성과 편의성을 높인 디지털 서비스",
                "outreach": "지역사회 연계 활동",
                "outreach_desc": "지역 커뮤니티와의 협력과 홍보"
            },
            "resource_strategy": {
                "budget_allocation": {
                    "programs": "60%",
                    "operations": "25%",
                    "marketing": "15%"
                },
                "team_structure": {
                    "core_team": "전문가 3-5명",
                    "advisors": "분야별 전문가 자문단",
                    "volunteers": "지역사회 자원봉사자"
                }
            },
            "implementation_plan": {
                "phase1": "기반 구축 및 파일럿 프로그램 시작",
                "phase2": "서비스 확대 및 파트너십 구축",
                "phase3": "성과 측정 및 지속가능성 확보",
                "milestones": ["파일럿 완료", "파트너십 체결", "성과 달성"]
            },
            "partnership_strategy": {
                "strategic_partners": ["관련 기관", "전문 단체", "기업 파트너"],
                "funding_sources": ["정부 지원금", "민간 후원", "사회적 투자"],
                "collaboration_models": ["업무 협약", "공동 사업", "네트워크 참여"]
            }
        }