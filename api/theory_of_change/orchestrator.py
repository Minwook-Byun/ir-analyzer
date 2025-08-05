"""
변화이론 생성 오케스트레이터
studio-coach 패턴으로 다중 에이전트를 조율하여 변화이론을 생성합니다.
"""

import google.generativeai as genai
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from .agents.context_analyzer import ContextAnalyzer
from .agents.user_insight import UserInsightAgent
from .agents.strategy_designer import StrategyDesigner
from .agents.validator import Validator
from .agents.storyteller import Storyteller


class TheoryOfChangeOrchestrator:
    """다중 에이전트 조율기 - studio-coach 패턴"""
    
    def __init__(self, api_key: str):
        """오케스트레이터 초기화"""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        
        # 각 전문 에이전트 초기화
        self.context_analyzer = ContextAnalyzer(api_key)
        self.user_insight = UserInsightAgent(api_key)
        self.strategy_designer = StrategyDesigner(api_key)
        self.validator = Validator(api_key)
        self.storyteller = Storyteller(api_key)
    
    async def generate_theory_of_change(
        self, 
        organization_name: str, 
        impact_focus: Optional[str] = None,
        files: Optional[List] = None
    ) -> Dict[str, Any]:
        """6단계 협업 파이프라인으로 변화이론 생성"""
        
        try:
            print(f"🎯 변화이론 생성 시작: {organization_name}")
            
            # Phase 1: 현황 분석 (Context Analysis)
            print("📊 Phase 1: 현황 분석 중...")
            context = await self.context_analyzer.analyze_organization_context({
                "name": organization_name,
                "focus": impact_focus,
                "files": files
            })
            
            # Phase 2: 사용자 인사이트 (User Insights)
            print("👥 Phase 2: 사용자 인사이트 분석 중...")
            user_insights = await self.user_insight.synthesize_user_needs(context)
            
            # Phase 3: 전략 설계 (Strategy Design)
            print("🎨 Phase 3: 전략 설계 중...")
            strategy = await self.strategy_designer.design_intervention_logic(
                context, user_insights
            )
            
            # Phase 4: 검증 체계 (Validation Framework)
            print("🔬 Phase 4: 검증 체계 구성 중...")
            validation = await self.validator.design_validation_framework(strategy)
            
            # Phase 5: 스토리텔링 (Visualization)
            print("📖 Phase 5: 스토리텔링 및 시각화 중...")
            visualization = await self.storyteller.create_theory_visualization({
                "context": context,
                "user_insights": user_insights,
                "strategy": strategy,
                "validation": validation
            })
            
            # Phase 6: 통합 & 품질 보장
            print("⚡ Phase 6: 최종 통합 중...")
            complete_theory = self._synthesize_complete_theory({
                "organization_name": organization_name,
                "impact_focus": impact_focus,
                "context": context,
                "user_insights": user_insights,
                "strategy": strategy,
                "validation": validation,
                "visualization": visualization
            })
            
            print("✅ 변화이론 생성 완료")
            return complete_theory
            
        except Exception as e:
            print(f"❌ 변화이론 생성 중 오류: {str(e)}")
            # 오류 시 기본 템플릿 반환
            return self._get_fallback_theory(organization_name, impact_focus)
    
    def _synthesize_complete_theory(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """모든 컴포넌트를 통합하여 완전한 변화이론 생성"""
        
        # 기본 구조 생성
        theory_data = {
            "reportInfo": {
                "title": f"{components['organization_name']} 변화이론",
                "organization": components['organization_name'],
                "period": str(datetime.now().year),
                "version": "1.0",
                "lastUpdated": datetime.now().isoformat(),
                "generated_by": "multi-agent-system"
            },
            "organizationProfile": {
                "name": components['organization_name'],
                "mission": components.get('context', {}).get('mission', f"{components['organization_name']}의 사회적 임팩트 창출"),
                "vision": components.get('context', {}).get('vision', "지속가능한 사회 변화 실현"),
                "establishedYear": datetime.now().year,
                "teamSize": components.get('context', {}).get('team_size', 10),
                "location": "대한민국",
                "impactFocus": components.get('impact_focus', '사회혁신')
            }
        }
        
        # 변화이론 구조 통합
        if components.get('visualization', {}).get('theory_structure'):
            theory_data["theoryOfChange"] = components['visualization']['theory_structure']
        else:
            theory_data["theoryOfChange"] = self._create_default_theory_structure(components)
        
        # 성공 메트릭 추가
        if components.get('validation', {}).get('success_metrics'):
            theory_data["keyMetrics"] = components['validation']['success_metrics']
        
        return theory_data
    
    def _create_default_theory_structure(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """기본 변화이론 구조 생성"""
        
        return {
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
                        "items": self._extract_inputs(components)
                    },
                    {
                        "id": "activities",
                        "name": "활동(Activities)",
                        "layer": 2,
                        "yPosition": 280,
                        "height": 120,
                        "backgroundColor": "#F3E5F5",
                        "borderColor": "#9C27B0",
                        "items": self._extract_activities(components)
                    },
                    {
                        "id": "outputs",
                        "name": "산출(Outputs)",
                        "layer": 3,
                        "yPosition": 460,
                        "height": 120,
                        "backgroundColor": "#E8F5E8",
                        "borderColor": "#4CAF50",
                        "items": self._extract_outputs(components)
                    },
                    {
                        "id": "outcomes",
                        "name": "성과(Outcomes)",
                        "layer": 4,
                        "yPosition": 640,
                        "height": 120,
                        "backgroundColor": "#FFF3E0",
                        "borderColor": "#FF9800",
                        "items": self._extract_outcomes(components)
                    },
                    {
                        "id": "impact",
                        "name": "임팩트(Impact)",
                        "layer": 5,
                        "yPosition": 820,
                        "height": 120,
                        "backgroundColor": "#FFEBEE",
                        "borderColor": "#F44336",
                        "items": self._extract_impact(components)
                    }
                ],
                "connections": self._create_connections()
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
        }
    
    def _extract_inputs(self, components: Dict[str, Any]) -> List[Dict[str, Any]]:
        """투입 요소 추출"""
        context = components.get('context', {})
        
        inputs = [
            {
                "id": "funding",
                "title": "자금",
                "value": context.get('funding', '분석 필요'),
                "description": context.get('funding_desc', '운영 자금 및 프로젝트 예산'),
                "position": {"x": 50, "y": 100, "width": 180, "height": 80},
                "icon": "💰"
            },
            {
                "id": "team",
                "title": "인력",
                "value": context.get('team_size', '분석 필요'),
                "description": context.get('team_desc', '전문 인력 및 자원봉사자'),
                "position": {"x": 250, "y": 100, "width": 180, "height": 80},
                "icon": "👥"
            },
            {
                "id": "technology",
                "title": "기술",
                "value": context.get('technology', '디지털 도구'),
                "description": context.get('tech_desc', '필요한 기술 인프라'),
                "position": {"x": 450, "y": 100, "width": 180, "height": 80},
                "icon": "💻"
            }
        ]
        
        return inputs
    
    def _extract_activities(self, components: Dict[str, Any]) -> List[Dict[str, Any]]:
        """활동 요소 추출"""
        strategy = components.get('strategy', {})
        
        activities = [
            {
                "id": "education",
                "title": "교육 프로그램",
                "value": strategy.get('education_programs', '계획 수립 필요'),
                "description": strategy.get('education_desc', '대상 그룹별 맞춤 교육'),
                "position": {"x": 50, "y": 280, "width": 180, "height": 80},
                "icon": "📚"
            },
            {
                "id": "platform",
                "title": "플랫폼 구축",
                "value": strategy.get('platform_dev', '개발 예정'),
                "description": strategy.get('platform_desc', '서비스 제공 플랫폼'),
                "position": {"x": 250, "y": 280, "width": 180, "height": 80},
                "icon": "🔧"
            },
            {
                "id": "outreach",
                "title": "아웃리치",
                "value": strategy.get('outreach', '커뮤니티 활동'),
                "description": strategy.get('outreach_desc', '지역사회 참여 확대'),
                "position": {"x": 450, "y": 280, "width": 180, "height": 80},
                "icon": "📢"
            }
        ]
        
        return activities
    
    def _extract_outputs(self, components: Dict[str, Any]) -> List[Dict[str, Any]]:
        """산출 요소 추출"""
        validation = components.get('validation', {})
        
        outputs = [
            {
                "id": "trained_participants",
                "title": "교육 이수자",
                "value": validation.get('target_participants', '목표 설정 필요'),
                "description": validation.get('participants_desc', '프로그램 완료자 수'),
                "position": {"x": 80, "y": 460, "width": 160, "height": 80},
                "icon": "🎓"
            },
            {
                "id": "services_provided",
                "title": "제공 서비스",
                "value": validation.get('service_count', '서비스 개수'),
                "description": validation.get('service_desc', '실제 제공된 서비스'),
                "position": {"x": 260, "y": 460, "width": 160, "height": 80},
                "icon": "🚀"
            },
            {
                "id": "partnerships",
                "title": "구축된 파트너십",
                "value": validation.get('partnerships', '파트너 수'),
                "description": validation.get('partnership_desc', '협력 관계 수'),
                "position": {"x": 440, "y": 460, "width": 160, "height": 80},
                "icon": "🤝"
            }
        ]
        
        return outputs
    
    def _extract_outcomes(self, components: Dict[str, Any]) -> List[Dict[str, Any]]:
        """성과 요소 추출"""
        user_insights = components.get('user_insights', {})
        
        outcomes = [
            {
                "id": "skill_improvement",
                "title": "역량 향상",
                "value": user_insights.get('skill_target', '75%'),
                "description": user_insights.get('skill_desc', '참여자 역량 향상도'),
                "position": {"x": 50, "y": 640, "width": 180, "height": 80},
                "icon": "🎯"
            },
            {
                "id": "behavior_change",
                "title": "행동 변화",
                "value": user_insights.get('behavior_target', '60%'),
                "description": user_insights.get('behavior_desc', '긍정적 행동 변화율'),
                "position": {"x": 250, "y": 640, "width": 180, "height": 80},
                "icon": "📈"
            },
            {
                "id": "network_expansion",
                "title": "네트워크 확장",
                "value": user_insights.get('network_target', '증가'),
                "description": user_insights.get('network_desc', '사회적 연결망 확대'),
                "position": {"x": 450, "y": 640, "width": 180, "height": 80},
                "icon": "🌐"
            }
        ]
        
        return outcomes
    
    def _extract_impact(self, components: Dict[str, Any]) -> List[Dict[str, Any]]:
        """임팩트 요소 추출"""
        impact_focus = components.get('impact_focus', '사회혁신')
        
        impacts = [
            {
                "id": "social_change",
                "title": "사회적 변화",
                "value": "장기적 변화",
                "description": f"{impact_focus} 영역의 지속가능한 사회 변화",
                "position": {"x": 150, "y": 820, "width": 250, "height": 80},
                "icon": "🌍"
            },
            {
                "id": "systemic_impact",
                "title": "시스템 개선",
                "value": "구조적 변화",
                "description": "기존 시스템의 긍정적 변화 유도",
                "position": {"x": 450, "y": 820, "width": 250, "height": 80},
                "icon": "⚡"
            }
        ]
        
        return impacts
    
    def _create_connections(self) -> List[Dict[str, Any]]:
        """단계별 연결 관계 생성"""
        return [
            {"from": "funding", "to": "education", "type": "arrow", "style": "solid"},
            {"from": "team", "to": "platform", "type": "arrow", "style": "solid"},
            {"from": "technology", "to": "outreach", "type": "arrow", "style": "solid"},
            {"from": "education", "to": "trained_participants", "type": "arrow", "style": "solid"},
            {"from": "platform", "to": "services_provided", "type": "arrow", "style": "solid"},
            {"from": "outreach", "to": "partnerships", "type": "arrow", "style": "solid"},
            {"from": "trained_participants", "to": "skill_improvement", "type": "arrow", "style": "solid"},
            {"from": "services_provided", "to": "behavior_change", "type": "arrow", "style": "solid"},
            {"from": "partnerships", "to": "network_expansion", "type": "arrow", "style": "solid"},
            {"from": "skill_improvement", "to": "social_change", "type": "arrow", "style": "solid"},
            {"from": "behavior_change", "to": "systemic_impact", "type": "arrow", "style": "solid"}
        ]
    
    def _get_fallback_theory(self, organization_name: str, impact_focus: Optional[str]) -> Dict[str, Any]:
        """오류 시 기본 변화이론 반환"""
        return {
            "reportInfo": {
                "title": f"{organization_name} 변화이론",
                "organization": organization_name,
                "period": str(datetime.now().year),
                "version": "1.0",
                "lastUpdated": datetime.now().isoformat(),
                "generated_by": "fallback-template"
            },
            "organizationProfile": {
                "name": organization_name,
                "mission": f"{organization_name}의 사회적 임팩트 창출",
                "vision": "지속가능한 사회 변화 실현",
                "establishedYear": datetime.now().year,
                "teamSize": 10,
                "location": "대한민국",
                "impactFocus": impact_focus or '사회혁신'
            },
            "theoryOfChange": {
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
                                    "value": "분석 필요",
                                    "description": "운영 자금 및 프로젝트 예산",
                                    "position": {"x": 50, "y": 100, "width": 180, "height": 80},
                                    "icon": "💰"
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
                    }
                }
            }
        }