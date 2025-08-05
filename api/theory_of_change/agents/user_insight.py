"""
User Insight Agent
feedback-synthesizer + ux-researcher의 전문성을 결합하여
사용자 니즈와 행동 패턴을 분석합니다.
"""

import google.generativeai as genai
from typing import Dict, Any


class UserInsightAgent:
    """사용자 인사이트 분석 전문가"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    async def synthesize_user_needs(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """사용자 니즈와 행동 패턴 분석"""
        
        prompt = self._build_user_insight_prompt(context_data)
        
        try:
            response = self.model.generate_content(prompt)
            user_insights = self._parse_user_response(response.text, context_data)
            return user_insights
            
        except Exception as e:
            print(f"User insight 오류: {str(e)}")
            return self._get_default_insights(context_data)
    
    def _build_user_insight_prompt(self, context_data: Dict[str, Any]) -> str:
        """사용자 인사이트 분석을 위한 프롬프트 구성"""
        
        mission = context_data.get('current_state', {}).get('mission', '사회적 가치 창출')
        stakeholders = context_data.get('stakeholders', {}).get('primary', ['사용자'])
        
        return f"""
당신은 **User Insight Specialist**입니다. feedback-synthesizer와 ux-researcher의 전문성을 결합하여 사용자의 진짜 니즈와 행동 패턴을 깊이 있게 분석합니다.

## 분석 대상 조직 정보
- 미션: {mission}
- 주요 이해관계자: {', '.join(stakeholders)}

## 6가지 핵심 분석 영역
1. **User Persona Development**: 핵심 사용자 그룹 정의
2. **Pain Point Analysis**: 주요 문제점과 불편사항
3. **Behavioral Patterns**: 사용자 행동 패턴과 여정
4. **Motivation Drivers**: 핵심 동기와 목표
5. **Unmet Needs**: 충족되지 않은 니즈
6. **Success Indicators**: 사용자 성공 지표

## 분석 결과 JSON 구조로 반환:
```json
{{
  "user_personas": [
    {{
      "name": "페르소나 이름",
      "description": "페르소나 설명",
      "demographics": "인구통계학적 특성",
      "goals": ["목적 1", "목적 2"],
      "pain_points": ["문제점 1", "문제점 2"],
      "behaviors": ["행동 패턴 1", "행동 패턴 2"]
    }}
  ],
  "key_insights": {{
    "primary_needs": ["핵심 니즈 1", "핵심 니즈 2", "핵심 니즈 3"],
    "behavioral_drivers": ["행동 동기 1", "행동 동기 2"],
    "decision_factors": ["결정 요인 1", "결정 요인 2"],
    "barriers": ["장벽 1", "장벽 2"]
  }},
  "success_metrics": {{
    "skill_target": "역량 향상 목표 (예: 80%)",
    "skill_desc": "역량 향상 관련 설명",
    "behavior_target": "행동 변화 목표 (예: 70%)",
    "behavior_desc": "행동 변화 관련 설명",
    "network_target": "네트워크 확장 목표",
    "network_desc": "네트워크 확장 관련 설명"
  }},
  "user_journey": {{
    "awareness": "인지 단계 특성",
    "consideration": "고려 단계 특성",
    "adoption": "채택 단계 특성",
    "retention": "유지 단계 특성"
  }}
}}
```

사용자 중심의 깊이 있는 분석을 제공해주세요.
JSON 형태로만 응답하고, 다른 설명은 포함하지 마세요.
"""
    
    def _parse_user_response(self, response_text: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
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
                return self._get_default_insights(context_data)
                
        except Exception as e:
            print(f"User insight parsing 오류: {str(e)}")
            return self._get_default_insights(context_data)
    
    def _get_default_insights(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """기본 사용자 인사이트 데이터 반환"""
        
        return {
            "user_personas": [
                {
                    "name": "핵심 수혜자",
                    "description": "서비스의 주요 대상 그룹",
                    "demographics": "분석 필요",
                    "goals": ["문제 해결", "역량 향상", "기회 확대"],
                    "pain_points": ["기존 해결책 부족", "접근성 제약", "정보 부족"],
                    "behaviors": ["적극적 참여", "네트워크 활용", "학습 지향"]
                }
            ],
            "key_insights": {
                "primary_needs": ["실질적 도움", "지속적 지원", "커뮤니티 연결"],
                "behavioral_drivers": ["성취감", "소속감", "성장 욕구"],
                "decision_factors": ["신뢰성", "효과성", "접근성"],
                "barriers": ["시간 부족", "비용 부담", "정보 부족"]
            },
            "success_metrics": {
                "skill_target": "75%",
                "skill_desc": "참여자의 핵심 역량 향상도",
                "behavior_target": "60%",
                "behavior_desc": "긍정적 행동 변화 비율",
                "network_target": "확장",
                "network_desc": "사회적 연결망 확대 정도"
            },
            "user_journey": {
                "awareness": "문제 인식과 해결책 탐색",
                "consideration": "서비스 비교와 평가",
                "adoption": "초기 참여와 적응",
                "retention": "지속적 참여와 성장"
            }
        }