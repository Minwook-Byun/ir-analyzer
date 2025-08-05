"""
Storyteller Agent
visual-storyteller + content-creator의 전문성을 결합하여
변화이론의 시각화와 커뮤니케이션을 설계합니다.
"""

import google.generativeai as genai
from typing import Dict, Any


class Storyteller:
    """변화이론 시각화 및 스토리텔링 전문가"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    async def create_theory_visualization(self, complete_theory: Dict[str, Any]) -> Dict[str, Any]:
        """변화이론의 시각화와 스토리텔링 생성"""
        
        prompt = self._build_storytelling_prompt(complete_theory)
        
        try:
            response = self.model.generate_content(prompt)
            visualization = self._parse_storytelling_response(response.text, complete_theory)
            return visualization
            
        except Exception as e:
            print(f"Storytelling 오류: {str(e)}")
            return self._get_default_visualization(complete_theory)
    
    def _build_storytelling_prompt(self, complete_theory: Dict[str, Any]) -> str:
        """스토리텔링을 위한 프롬프트 구성"""
        
        context = complete_theory.get('context', {})
        strategy = complete_theory.get('strategy', {})
        user_insights = complete_theory.get('user_insights', {})
        
        mission = context.get('current_state', {}).get('mission', '사회적 가치 창출')
        target_outcome = strategy.get('intervention_logic', {}).get('target_outcome', '긍정적 사회 변화')
        
        return f"""
당신은 **Theory Visualization Specialist**입니다. visual-storyteller와 content-creator의 전문성을 결합하여 변화이론을 효과적으로 시각화하고 스토리텔링합니다.

## 변화이론 핵심 정보
### 조직 미션
{mission}

### 목표 성과
{target_outcome}

## 6가지 핵심 시각화 영역
1. **Theory Structure**: 5단계 변화이론 구조 설계
2. **Visual Design**: 색상, 레이아웃, 아이콘 체계
3. **Narrative Flow**: 스토리 흐름과 메시지
4. **Interaction Design**: 사용자 인터랙션 설계
5. **Stakeholder Messages**: 이해관계자별 맞춤 메시지
6. **Impact Communication**: 임팩트 커뮤니케이션 전략

## 시각화 설계 결과 JSON 구조로 반환:
```json
{{
  "theory_structure": {{
    "structure": {{
      "layers": [
        {{
          "id": "inputs",
          "name": "투입(Inputs)",
          "layer": 1,
          "yPosition": 100,
          "height": 120,
          "backgroundColor": "#E8F4FD",
          "borderColor": "#2196F3",
          "items": [
            {{
              "id": "resource1",
              "title": "자원 제목",
              "value": "구체적 수치",
              "description": "상세 설명",
              "position": {{"x": 50, "y": 100, "width": 180, "height": 80}},
              "icon": "적절한 이모티콘"
            }}
          ]
        }},
        {{
          "id": "activities",
          "name": "활동(Activities)",
          "layer": 2,
          "yPosition": 280,
          "height": 120,
          "backgroundColor": "#F3E5F5",
          "borderColor": "#9C27B0",
          "items": []
        }},
        {{
          "id": "outputs",
          "name": "산출(Outputs)",
          "layer": 3,
          "yPosition": 460,
          "height": 120,
          "backgroundColor": "#E8F5E8",
          "borderColor": "#4CAF50",
          "items": []
        }},
        {{
          "id": "outcomes",
          "name": "성과(Outcomes)",
          "layer": 4,
          "yPosition": 640,
          "height": 120,
          "backgroundColor": "#FFF3E0",
          "borderColor": "#FF9800",
          "items": []
        }},
        {{
          "id": "impact",
          "name": "임팩트(Impact)",
          "layer": 5,
          "yPosition": 820,
          "height": 120,
          "backgroundColor": "#FFEBEE",
          "borderColor": "#F44336",
          "items": []
        }}
      ],
      "connections": [
        {{
          "from": "source_id",
          "to": "target_id",
          "type": "arrow",
          "style": "solid"
        }}
      ]
    }},
    "designSpecs": {{
      "container": {{
        "width": "1200px",
        "height": "1000px",
        "background": "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
        "padding": "40px"
      }},
      "layerSpacing": 140,
      "itemSpacing": 20,
      "animations": {{
        "fadeIn": {{"duration": "0.6s", "delay": "0.1s"}},
        "slideUp": {{"duration": "0.8s", "distance": "30px"}}
      }}
    }}
  }},
  "narrative_elements": {{
    "main_story": "변화이론의 핵심 스토리 (2-3문장)",
    "key_messages": ["핵심 메시지 1", "핵심 메시지 2", "핵심 메시지 3"],
    "success_story": "예상되는 성공 사례 스토리"
  }},
  "visual_identity": {{
    "color_palette": {{
      "primary": "#2E8B57",
      "secondary": "#4169E1", 
      "accent": "#FF6B6B",
      "neutral": "#F8F9FA"
    }},
    "typography": {{
      "heading": "bold, 18px",
      "body": "regular, 14px",
      "caption": "light, 12px"
    }},
    "iconography": "modern, minimal, colorful emojis"
  }},
  "interaction_design": {{
    "hover_effects": "subtle scale and shadow",
    "click_interactions": "detailed view expansion",
    "navigation": "smooth scrolling between layers"
  }}
}}
```

각 단계별로 구체적이고 실행 가능한 항목들을 3-4개씩 포함하여 완전한 변화이론을 설계해주세요.
JSON 형태로만 응답하고, 다른 설명은 포함하지 마세요.
"""
    
    def _parse_storytelling_response(self, response_text: str, complete_theory: Dict[str, Any]) -> Dict[str, Any]:
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
                return self._get_default_visualization(complete_theory)
                
        except Exception as e:
            print(f"Storytelling parsing 오류: {str(e)}")
            return self._get_default_visualization(complete_theory)
    
    def _get_default_visualization(self, complete_theory: Dict[str, Any]) -> Dict[str, Any]:
        """기본 시각화 데이터 반환"""
        
        return {
            "theory_structure": {
                "structure": {
                    "layers": [
                        {
                            "id": "inputs",
                            "name": "투입(Inputs)",
                            "layer": 1,
                            "yPosition": 100,
                            "height": 120,
                            "backgroundColor": "#E8F4FD",
                            "borderColor": "#2196F3",
                            "items": [
                                {
                                    "id": "funding",
                                    "title": "자금",
                                    "value": "운영 자금",
                                    "description": "프로젝트 실행을 위한 기본 자금",
                                    "position": {"x": 50, "y": 100, "width": 180, "height": 80},
                                    "icon": "💰"
                                },
                                {
                                    "id": "team",
                                    "title": "인력",
                                    "value": "전문 팀",
                                    "description": "경험 있는 전문가와 자원봉사자",
                                    "position": {"x": 250, "y": 100, "width": 180, "height": 80},
                                    "icon": "👥"
                                },
                                {
                                    "id": "technology",
                                    "title": "기술",
                                    "value": "디지털 도구",
                                    "description": "효과적인 서비스 제공을 위한 기술",
                                    "position": {"x": 450, "y": 100, "width": 180, "height": 80},
                                    "icon": "💻"
                                }
                            ]
                        },
                        {
                            "id": "activities",
                            "name": "활동(Activities)",
                            "layer": 2,
                            "yPosition": 280,
                            "height": 120,
                            "backgroundColor": "#F3E5F5",
                            "borderColor": "#9C27B0",
                            "items": [
                                {
                                    "id": "education",
                                    "title": "교육 프로그램",
                                    "value": "맞춤형 교육",
                                    "description": "대상별 특화된 교육 과정",
                                    "position": {"x": 50, "y": 280, "width": 180, "height": 80},
                                    "icon": "📚"
                                },
                                {
                                    "id": "platform",
                                    "title": "플랫폼 구축",
                                    "value": "온라인 서비스",
                                    "description": "접근성 높은 디지털 플랫폼",
                                    "position": {"x": 250, "y": 280, "width": 180, "height": 80},
                                    "icon": "🔧"
                                },
                                {
                                    "id": "outreach",
                                    "title": "아웃리치",
                                    "value": "지역 연계",
                                    "description": "지역사회와의 적극적 소통",
                                    "position": {"x": 450, "y": 280, "width": 180, "height": 80},
                                    "icon": "📢"
                                }
                            ]
                        }
                    ],
                    "connections": []
                },
                "designSpecs": {
                    "container": {
                        "width": "1200px",
                        "height": "1000px",
                        "background": "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
                        "padding": "40px"
                    },
                    "layerSpacing": 140,
                    "itemSpacing": 20
                }
            },
            "narrative_elements": {
                "main_story": "체계적인 투입을 통해 의미 있는 활동을 실행하고, 측정 가능한 성과로 지속가능한 사회적 임팩트를 창출합니다.",
                "key_messages": ["실행 가능한 계획", "측정 가능한 성과", "지속가능한 변화"],
                "success_story": "참여자들이 프로그램을 통해 역량을 키우고, 더 나은 기회를 얻으며, 지역사회에 긍정적 영향을 미치는 선순환 구조"
            },
            "visual_identity": {
                "color_palette": {
                    "primary": "#2E8B57",
                    "secondary": "#4169E1",
                    "accent": "#FF6B6B", 
                    "neutral": "#F8F9FA"
                },
                "typography": {
                    "heading": "bold, 18px",
                    "body": "regular, 14px",
                    "caption": "light, 12px"
                }
            }
        }