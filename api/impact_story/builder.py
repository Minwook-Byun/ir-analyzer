"""
Impact Story Builder - 핵심 로직
단순하고 빠른 임팩트 스토리 생성
"""

from typing import Dict, Any, Optional, List
from .templates import StoryTemplates
from .validator import StoryValidator


class ImpactStoryBuilder:
    """단순한 임팩트 스토리 생성기 - API 호출 최소화"""
    
    def __init__(self):
        self.templates = StoryTemplates()
        self.validator = StoryValidator()
        
    def build_story_from_steps(self, steps: Dict[str, str]) -> Dict[str, Any]:
        """5단계 입력으로 완전한 임팩트 스토리 생성"""
        
        # 입력 검증
        validation_result = self.validator.validate_steps(steps)
        if not validation_result["valid"]:
            return {
                "success": False,
                "error": validation_result["errors"],
                "story": None
            }
        
        # 스토리 생성 (즉시 처리, API 호출 없음)
        story_data = {
            "headline": self._create_headline(steps),
            "key_metrics": self._extract_key_metrics(steps),
            "problem_context": self._format_problem_context(steps),
            "solution_approach": self._format_solution_approach(steps),
            "expected_impact": self._format_expected_impact(steps),
            "measurement_plan": self._format_measurement_plan(steps),
            "story_template": self._select_story_template(steps),
            "generated_at": self._get_timestamp()
        }
        
        return {
            "success": True,
            "story": story_data,
            "suggestions": self._generate_improvement_suggestions(steps)
        }
    
    def _create_headline(self, steps: Dict[str, str]) -> str:
        """핵심 헤드라인 생성 (1문장)"""
        template = "우리는 {problem}을 {solution}으로 해결해서 {target}의 {change}을 {timeframe} 안에 달성하고 싶습니다."
        
        return template.format(
            problem=steps.get("problem", "___"),
            solution=steps.get("solution", "___"),
            target=steps.get("target", "___"),
            change=steps.get("change", "___"),
            timeframe=steps.get("timeframe", "___")
        )
    
    def _extract_key_metrics(self, steps: Dict[str, str]) -> List[Dict[str, str]]:
        """핵심 지표 3개 추출"""
        
        # 단순 키워드 매칭으로 수치 추출
        metrics = []
        
        # Reach (도달) 지표
        reach_keywords = ["명", "사람", "개", "곳", "지역", "가구"]
        reach_metric = self._extract_metric_from_text(steps.get("target", ""), reach_keywords)
        metrics.append({
            "type": "reach",
            "icon": "👥",
            "label": "대상 규모",
            "value": reach_metric or "측정 필요"
        })
        
        # Depth (깊이) 지표  
        depth_keywords = ["%", "배", "점", "등급", "개선", "증가", "감소"]
        depth_metric = self._extract_metric_from_text(steps.get("change", ""), depth_keywords)
        metrics.append({
            "type": "depth", 
            "icon": "📈",
            "label": "변화 정도",
            "value": depth_metric or "측정 필요"
        })
        
        # Speed (속도) 지표
        speed_keywords = ["개월", "년", "주", "일", "분기"]
        speed_metric = self._extract_metric_from_text(steps.get("timeframe", ""), speed_keywords)
        metrics.append({
            "type": "speed",
            "icon": "⚡", 
            "label": "목표 기간",
            "value": speed_metric or "측정 필요"
        })
        
        return metrics
    
    def _extract_metric_from_text(self, text: str, keywords: List[str]) -> Optional[str]:
        """텍스트에서 수치 추출"""
        import re
        
        for keyword in keywords:
            # 숫자 + 키워드 패턴 찾기
            pattern = r'(\d+(?:\.\d+)?)\s*' + re.escape(keyword)
            match = re.search(pattern, text)
            if match:
                return f"{match.group(1)}{keyword}"
        
        return None
    
    def _format_problem_context(self, steps: Dict[str, str]) -> Dict[str, str]:
        """문제 맥락 정리"""
        return {
            "problem_statement": steps.get("problem", ""),
            "affected_group": steps.get("target", ""),
            "current_situation": f"{steps.get('target', '')}이 {steps.get('problem', '')} 문제로 어려움을 겪고 있습니다."
        }
    
    def _format_solution_approach(self, steps: Dict[str, str]) -> Dict[str, str]:
        """솔루션 접근법 정리"""
        return {
            "solution_description": steps.get("solution", ""),
            "approach_summary": f"{steps.get('solution', '')}을 통해 문제를 해결합니다.",
            "unique_value": "기존 해결책과의 차별점을 추가해주세요."
        }
    
    def _format_expected_impact(self, steps: Dict[str, str]) -> Dict[str, str]:
        """기대 임팩트 정리"""
        return {
            "direct_impact": steps.get("change", ""),
            "beneficiary_change": f"{steps.get('target', '')}의 {steps.get('change', '')}",
            "broader_impact": "사회적 파급효과를 추가해주세요."
        }
    
    def _format_measurement_plan(self, steps: Dict[str, str]) -> Dict[str, str]:
        """측정 계획 정리"""
        return {
            "measurement_method": steps.get("measurement", ""),
            "success_criteria": f"{steps.get('change', '')}을 {steps.get('measurement', '')}로 측정",
            "timeline": steps.get("timeframe", "")
        }
    
    def _select_story_template(self, steps: Dict[str, str]) -> str:
        """적절한 스토리 템플릿 선택"""
        problem_text = steps.get("problem", "").lower()
        
        if any(keyword in problem_text for keyword in ["교육", "학습", "역량"]):
            return "education"
        elif any(keyword in problem_text for keyword in ["건강", "의료", "치료"]):
            return "healthcare"  
        elif any(keyword in problem_text for keyword in ["환경", "기후", "지속가능"]):
            return "environment"
        else:
            return "general"
    
    def _generate_improvement_suggestions(self, steps: Dict[str, str]) -> List[str]:
        """개선 제안 생성"""
        suggestions = []
        
        # 수치의 구체성 확인
        if not any(char.isdigit() for char in steps.get("change", "")):
            suggestions.append("변화 정도를 구체적인 숫자로 표현해보세요 (예: 30% 개선)")
        
        if not any(char.isdigit() for char in steps.get("timeframe", "")):
            suggestions.append("목표 기간을 구체적으로 설정해보세요 (예: 6개월)")
            
        # 측정 방법의 구체성 확인
        if len(steps.get("measurement", "")) < 10:
            suggestions.append("측정 방법을 더 구체적으로 설명해보세요")
        
        return suggestions
    
    def _get_timestamp(self) -> str:
        """현재 시간 반환"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def update_story_component(self, story_data: Dict[str, Any], component: str, new_value: str) -> Dict[str, Any]:
        """실시간 스토리 컴포넌트 업데이트"""
        
        if component == "headline":
            story_data["headline"] = new_value
        elif component in ["problem", "solution", "target", "change", "timeframe"]:
            # 헤드라인 재생성
            steps = {
                "problem": story_data.get("problem_context", {}).get("problem_statement", ""),
                "solution": story_data.get("solution_approach", {}).get("solution_description", ""),
                "target": story_data.get("problem_context", {}).get("affected_group", ""),
                "change": story_data.get("expected_impact", {}).get("direct_impact", ""),
                "timeframe": story_data.get("measurement_plan", {}).get("timeline", "")
            }
            steps[component] = new_value
            story_data["headline"] = self._create_headline(steps)
            story_data["key_metrics"] = self._extract_key_metrics(steps)
        
        return story_data