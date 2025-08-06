"""
Enhanced Impact Story Builder - 기존 agents 프롬프트 통합
고도화된 AI 프롬프트를 활용한 더 정교한 스토리 생성
"""

import google.generativeai as genai
from typing import Dict, Any, Optional, List
from .templates import StoryTemplates
from .validator import StoryValidator


class EnhancedImpactStoryBuilder:
    """기존 agents 프롬프트를 통합한 고도화된 스토리 빌더"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.templates = StoryTemplates()
        self.validator = StoryValidator()
        self.api_key = api_key
        
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        else:
            self.model = None
    
    async def build_enhanced_story(self, steps: Dict[str, str], use_ai: bool = True) -> Dict[str, Any]:
        """AI 프롬프트를 활용한 고도화된 스토리 생성"""
        
        # 입력 검증
        validation_result = self.validator.validate_steps(steps)
        if not validation_result["valid"]:
            return {
                "success": False,
                "error": validation_result["errors"],
                "story": None
            }
        
        if use_ai and self.model:
            # AI 기반 고도화된 생성
            return await self._generate_ai_enhanced_story(steps)
        else:
            # 기본 템플릿 기반 생성 (fallback)
            return self._generate_template_story(steps)
    
    async def _generate_ai_enhanced_story(self, steps: Dict[str, str]) -> Dict[str, Any]:
        """AI를 활용한 고도화된 스토리 생성"""
        
        try:
            # 1. Context Analysis (기존 ContextAnalyzer 프롬프트 활용)
            context_analysis = await self._analyze_context_with_ai(steps)
            
            # 2. User Insight Analysis (기존 UserInsightAgent 프롬프트 활용)  
            user_insights = await self._analyze_user_insights_with_ai(steps, context_analysis)
            
            # 3. Strategy Design (기존 StrategyDesigner 프롬프트 활용)
            strategy_design = await self._design_strategy_with_ai(steps, context_analysis, user_insights)
            
            # 4. Storytelling (기존 Storyteller 프롬프트 활용)
            story_visualization = await self._create_story_with_ai(steps, context_analysis, user_insights, strategy_design)
            
            return {
                "success": True,
                "story": story_visualization,
                "context_analysis": context_analysis,
                "user_insights": user_insights,
                "strategy_design": strategy_design,
                "generation_method": "ai_enhanced"
            }
            
        except Exception as e:
            print(f"AI 스토리 생성 오류: {str(e)}")
            # AI 실패시 기본 템플릿으로 fallback
            return self._generate_template_story(steps)
    
    async def _analyze_context_with_ai(self, steps: Dict[str, str]) -> Dict[str, Any]:
        """기존 ContextAnalyzer 프롬프트를 활용한 현황 분석"""
        
        # 기존 context_analyzer.py의 프롬프트 패턴 활용
        prompt = f"""
당신은 **Context Analysis Specialist**입니다. analytics-reporter와 trend-researcher의 전문성을 결합하여 조직의 현재 상황과 변화 기회를 체계적으로 분석합니다.

## 분석 대상 임팩트 프로젝트
- 해결 문제: {steps.get('problem', '')}
- 대상 그룹: {steps.get('target', '')}
- 솔루션: {steps.get('solution', '')}
- 기대 변화: {steps.get('change', '')}

## 6가지 핵심 분석 영역
1. **Current State Analysis**: 현재 문제의 상태와 심각성
2. **Market Context**: 해당 문제 영역의 시장 상황과 기회
3. **Trend Integration**: 관련 트렌드와 타이밍 분석
4. **Stakeholder Mapping**: 주요 이해관계자 식별
5. **Resource Assessment**: 가용 자원과 제약사항
6. **Opportunity Prioritization**: 변화 기회의 우선순위

## 분석 결과 JSON 구조로 반환:
```json
{{
  "current_state": {{
    "problem_severity": "문제의 심각성 분석",
    "affected_population": "영향받는 인구 규모",
    "existing_solutions": "기존 해결책과 한계",
    "urgency_level": "해결의 시급성"
  }},
  "market_context": {{
    "market_size": "해당 영역 시장 규모",
    "growth_trend": "성장 트렌드 분석",
    "key_opportunities": ["기회 1", "기회 2", "기회 3"],
    "competitive_landscape": "경쟁 환경 분석"
  }},
  "stakeholders": {{
    "primary": ["핵심 이해관계자들"],
    "secondary": ["2차 이해관계자들"],
    "influencers": ["의사결정 영향자들"],
    "beneficiaries": ["직접 수혜자들"]
  }},
  "success_factors": {{
    "critical_factors": ["성공 핵심 요인들"],
    "risk_factors": ["주요 위험 요인들"],
    "timing_considerations": ["타이밍 고려사항들"]
  }}
}}
```

임팩트 창출 관점에서 전문적이고 현실적인 분석을 제공해주세요.
JSON 형태로만 응답하고, 다른 설명은 포함하지 마세요.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_json_response(response.text, "context_analysis")
        except Exception as e:
            print(f"Context analysis AI 오류: {str(e)}")
            return self._get_default_context_analysis(steps)
    
    async def _analyze_user_insights_with_ai(self, steps: Dict[str, str], context: Dict[str, Any]) -> Dict[str, Any]:
        """기존 UserInsightAgent 프롬프트를 활용한 사용자 인사이트 분석"""
        
        problem = steps.get('problem', '')
        target = steps.get('target', '')
        
        prompt = f"""
당신은 **User Insight Specialist**입니다. feedback-synthesizer와 ux-researcher의 전문성을 결합하여 사용자의 진짜 니즈와 행동 패턴을 깊이 있게 분석합니다.

## 분석 대상
- 문제 상황: {problem}
- 타겟 사용자: {target}
- 시장 컨텍스트: {context.get('market_context', {}).get('market_size', '분석 필요')}

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
      "behaviors": ["행동 패턴 1", "행동 패턴 2"],
      "motivations": ["동기 1", "동기 2"]
    }}
  ],
  "key_insights": {{
    "primary_needs": ["핵심 니즈 1", "핵심 니즈 2", "핵심 니즈 3"],
    "behavioral_drivers": ["행동 동기 1", "행동 동기 2"],
    "decision_factors": ["결정 요인 1", "결정 요인 2"],
    "barriers": ["장벽 1", "장벽 2"]
  }},
  "user_journey": {{
    "awareness": "인지 단계 특성",
    "consideration": "고려 단계 특성", 
    "adoption": "채택 단계 특성",
    "retention": "유지 단계 특성"
  }},
  "impact_expectations": {{
    "immediate_benefits": ["즉시 얻는 혜택들"],
    "long_term_value": ["장기적 가치들"],
    "success_metrics": ["사용자 성공 지표들"]
  }}
}}
```

사용자 중심의 깊이 있는 분석을 제공해주세요.
JSON 형태로만 응답하고, 다른 설명은 포함하지 마세요.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_json_response(response.text, "user_insights")
        except Exception as e:
            print(f"User insights AI 오류: {str(e)}")
            return self._get_default_user_insights(steps)
    
    async def _design_strategy_with_ai(self, steps: Dict[str, str], context: Dict[str, Any], user_insights: Dict[str, Any]) -> Dict[str, Any]:
        """기존 StrategyDesigner 프롬프트를 활용한 전략 설계"""
        
        solution = steps.get('solution', '')
        change = steps.get('change', '')
        
        prompt = f"""
당신은 **Strategy Design Specialist**입니다. sprint-prioritizer와 studio-producer의 전문성을 결합하여 실행 가능한 임팩트 전략을 수립합니다.

## 입력 정보
### 솔루션 접근법
{solution}

### 기대하는 변화
{change}

### 사용자 핵심 니즈
{', '.join(user_insights.get('key_insights', {}).get('primary_needs', []))}

## 6가지 핵심 설계 영역
1. **Impact Logic**: 임팩트를 만들어낼 핵심 논리
2. **Activity Design**: 구체적 활동과 프로그램 설계
3. **Resource Allocation**: 효율적 자원 배분 전략
4. **Timeline Planning**: 단계별 실행 일정
5. **Partnership Strategy**: 핵심 파트너십 전략
6. **Risk Mitigation**: 위험 요소 완화 방안

## 전략 설계 결과 JSON 구조로 반환:
```json
{{
  "impact_logic": {{
    "core_hypothesis": "핵심 가설 (한 문장)",
    "change_mechanism": "변화 메커니즘 설명",
    "target_outcome": "목표하는 변화",
    "success_indicators": ["성공 지표 1", "성공 지표 2"]
  }},
  "implementation_strategy": {{
    "phase1": {{
      "duration": "기간",
      "key_activities": ["핵심 활동 1", "핵심 활동 2"],
      "milestones": ["마일스톤 1", "마일스톤 2"],
      "resources_needed": ["필요 자원 1", "필요 자원 2"]
    }},
    "phase2": {{
      "duration": "기간",
      "key_activities": ["핵심 활동 1", "핵심 활동 2"],
      "milestones": ["마일스톤 1", "마일스톤 2"],
      "scaling_approach": "확산 접근법"
    }},
    "phase3": {{
      "duration": "기간",
      "key_activities": ["지속가능성 확보", "임팩트 측정"],
      "sustainability_plan": "지속가능성 계획"
    }}
  }},
  "partnership_strategy": {{
    "strategic_partners": ["전략적 파트너 1", "전략적 파트너 2"],
    "funding_sources": ["펀딩 소스 1", "펀딩 소스 2"],
    "collaboration_models": ["협력 모델 1", "협력 모델 2"]
  }},
  "risk_management": {{
    "high_risks": ["높은 위험 1", "높은 위험 2"],
    "mitigation_plans": ["완화 계획 1", "완화 계획 2"],
    "contingency_measures": ["비상 조치 1", "비상 조치 2"]
  }}
}}
```

실행 가능하고 현실적인 임팩트 전략을 설계해주세요.
JSON 형태로만 응답하고, 다른 설명은 포함하지 마세요.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_json_response(response.text, "strategy_design")
        except Exception as e:
            print(f"Strategy design AI 오류: {str(e)}")
            return self._get_default_strategy_design(steps)
    
    async def _create_story_with_ai(self, steps: Dict[str, str], context: Dict[str, Any], user_insights: Dict[str, Any], strategy: Dict[str, Any]) -> Dict[str, Any]:
        """기존 Storyteller 프롬프트를 활용한 스토리 생성"""
        
        # 모든 분석 결과를 통합한 스토리텔링
        prompt = f"""
당신은 **Impact Story Specialist**입니다. visual-storyteller와 content-creator의 전문성을 결합하여 임팩트 스토리를 효과적으로 구성하고 전달합니다.

## 통합 임팩트 분석 정보
### 원본 입력
- 문제: {steps.get('problem', '')}
- 대상: {steps.get('target', '')}
- 솔루션: {steps.get('solution', '')}
- 변화: {steps.get('change', '')}
- 측정: {steps.get('measurement', '')}

### 분석 결과 활용
- 핵심 가설: {strategy.get('impact_logic', {}).get('core_hypothesis', '체계적 접근을 통한 긍정적 변화 창출')}
- 사용자 니즈: {', '.join(user_insights.get('key_insights', {}).get('primary_needs', ['개선된 서비스', '접근성 향상']))}
- 시장 기회: {', '.join(context.get('market_context', {}).get('key_opportunities', ['디지털 혁신', '사회적 니즈 증가']))}

## 6가지 핵심 스토리텔링 영역
1. **Compelling Headline**: 강력한 임팩트 헤드라인
2. **Problem Narrative**: 문제의 스토리텔링
3. **Solution Story**: 솔루션의 독특함과 효과
4. **Impact Visualization**: 임팩트의 시각적 표현
5. **Success Metrics**: 성공을 보여주는 지표들
6. **Call to Action**: 행동 촉구 메시지

## 완성된 임팩트 스토리 JSON 구조로 반환:
```json
{{
  "headline": "임팩트를 한 문장으로 표현한 강력한 헤드라인",
  "story_elements": {{
    "problem_narrative": {{
      "hook": "문제를 생생하게 보여주는 훅",
      "context": "문제의 배경과 맥락",
      "urgency": "해결의 시급성"
    }},
    "solution_story": {{
      "uniqueness": "솔루션의 독특한 점",
      "approach": "접근 방식의 혁신성",
      "effectiveness": "효과성 예상"
    }},
    "impact_promise": {{
      "immediate_impact": "즉시 나타날 변화",
      "long_term_vision": "장기적 비전",
      "ripple_effect": "파급 효과"
    }}
  }},
  "key_metrics": [
    {{
      "type": "reach",
      "icon": "👥",
      "label": "도달 규모",
      "value": "추출된 숫자 또는 목표",
      "description": "설명"
    }},
    {{
      "type": "depth",
      "icon": "📈", 
      "label": "변화 정도",
      "value": "개선 정도 수치",
      "description": "설명"
    }},
    {{
      "type": "speed",
      "icon": "⚡",
      "label": "달성 기간",
      "value": "시간 단위",
      "description": "설명"
    }}
  ],
  "supporting_details": {{
    "problem_context": {{
      "current_situation": "현재 상황 요약",
      "affected_group": "영향받는 그룹",  
      "root_causes": ["근본 원인들"]
    }},
    "solution_approach": {{
      "methodology": "방법론",
      "innovation": "혁신 요소",
      "scalability": "확장 가능성"
    }},
    "expected_impact": {{
      "direct_beneficiaries": "직접 수혜자",
      "indirect_effects": "간접 효과",
      "social_value": "사회적 가치"
    }},
    "measurement_plan": {{
      "success_criteria": "성공 기준",
      "tracking_method": "추적 방법",
      "evaluation_timeline": "평가 일정"
    }}
  }},
  "call_to_action": {{
    "primary_message": "주요 행동 촉구",
    "target_audience": "대상 청중",
    "next_steps": ["다음 단계들"]
  }}
}}
```

설득력 있고 감동적인 임팩트 스토리를 완성해주세요.
JSON 형태로만 응답하고, 다른 설명은 포함하지 마세요.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_json_response(response.text, "story_visualization")
        except Exception as e:
            print(f"Story creation AI 오류: {str(e)}")
            return self._get_default_story_visualization(steps)
    
    def _parse_json_response(self, response_text: str, analysis_type: str) -> Dict[str, Any]:
        """AI 응답에서 JSON 파싱"""
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
                raise ValueError("JSON 블록을 찾을 수 없음")
                
        except Exception as e:
            print(f"{analysis_type} JSON 파싱 오류: {str(e)}")
            return self._get_fallback_data(analysis_type)
    
    def _generate_template_story(self, steps: Dict[str, str]) -> Dict[str, Any]:
        """기본 템플릿 기반 스토리 생성 (AI 없이)"""
        
        # 기존 builder.py의 로직 활용
        from .builder import ImpactStoryBuilder
        basic_builder = ImpactStoryBuilder()
        
        return basic_builder.build_story_from_steps(steps)
    
    def _get_fallback_data(self, data_type: str) -> Dict[str, Any]:
        """AI 실패시 기본 데이터 반환"""
        
        fallbacks = {
            "context_analysis": {
                "current_state": {"problem_severity": "분석 필요", "affected_population": "확인 필요"},
                "market_context": {"market_size": "조사 중", "growth_trend": "긍정적"},
                "stakeholders": {"primary": ["수혜자", "파트너"], "secondary": ["지역사회"]},
                "success_factors": {"critical_factors": ["실행력", "파트너십"]}
            },
            "user_insights": {
                "user_personas": [{"name": "핵심 사용자", "description": "분석 필요"}],
                "key_insights": {"primary_needs": ["문제 해결", "접근성 향상"]},
                "user_journey": {"awareness": "문제 인식"}
            },
            "strategy_design": {
                "impact_logic": {"core_hypothesis": "체계적 접근을 통한 변화 창출"},
                "implementation_strategy": {"phase1": {"duration": "3개월", "key_activities": ["기반 구축"]}}
            },
            "story_visualization": {
                "headline": "임팩트 스토리 생성 중...",
                "key_metrics": [
                    {"type": "reach", "icon": "👥", "label": "대상", "value": "확인 필요"},
                    {"type": "depth", "icon": "📈", "label": "변화", "value": "측정 예정"},
                    {"type": "speed", "icon": "⚡", "label": "기간", "value": "계획 수립 중"}
                ]
            }
        }
        
        return fallbacks.get(data_type, {})
    
    def _get_default_context_analysis(self, steps: Dict[str, str]) -> Dict[str, Any]:
        """기본 컨텍스트 분석"""
        return self._get_fallback_data("context_analysis")
    
    def _get_default_user_insights(self, steps: Dict[str, str]) -> Dict[str, Any]:
        """기본 사용자 인사이트"""
        return self._get_fallback_data("user_insights")
    
    def _get_default_strategy_design(self, steps: Dict[str, str]) -> Dict[str, Any]:
        """기본 전략 설계"""
        return self._get_fallback_data("strategy_design")
    
    def _get_default_story_visualization(self, steps: Dict[str, str]) -> Dict[str, Any]:
        """기본 스토리 시각화"""
        return self._get_fallback_data("story_visualization")