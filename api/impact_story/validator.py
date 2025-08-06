"""
Story Validator - 입력 검증 및 품질 확인
"""

from typing import Dict, List, Any
import re


class StoryValidator:
    """임팩트 스토리 입력 검증"""
    
    def __init__(self):
        self.min_length = 5  # 최소 글자 수
        self.required_fields = ["problem", "target", "solution", "change", "measurement"]
    
    def validate_steps(self, steps: Dict[str, str]) -> Dict[str, Any]:
        """5단계 입력 검증"""
        
        errors = []
        warnings = []
        
        # 필수 필드 확인
        for field in self.required_fields:
            if not steps.get(field, "").strip():
                errors.append(f"{self._get_field_korean_name(field)} 항목을 입력해주세요.")
            elif len(steps[field].strip()) < self.min_length:
                warnings.append(f"{self._get_field_korean_name(field)} 항목을 더 구체적으로 작성해주세요.")
        
        # 수치 포함 여부 확인
        if not self._contains_numbers(steps.get("change", "")):
            warnings.append("변화 정도에 구체적인 수치를 포함해보세요. (예: 30% 개선, 100명 증가)")
        
        if not self._contains_time_reference(steps.get("timeframe", "")):
            warnings.append("목표 기간을 구체적으로 명시해보세요. (예: 6개월, 1년)")
        
        # 측정 방법의 구체성 확인
        measurement = steps.get("measurement", "")
        if measurement and not self._is_specific_measurement(measurement):
            warnings.append("측정 방법을 더 구체적으로 설명해보세요. (예: 설문조사, 데이터 분석, 추적 조사)")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "quality_score": self._calculate_quality_score(steps, errors, warnings)
        }
    
    def validate_single_field(self, field_name: str, value: str) -> Dict[str, Any]:
        """개별 필드 실시간 검증"""
        
        errors = []
        warnings = []
        suggestions = []
        
        if not value.strip():
            errors.append(f"{self._get_field_korean_name(field_name)} 항목을 입력해주세요.")
            return {"valid": False, "errors": errors, "warnings": warnings, "suggestions": suggestions}
        
        # 필드별 특별 검증
        if field_name == "problem":
            suggestions.extend(self._get_problem_suggestions(value))
        elif field_name == "target":
            suggestions.extend(self._get_target_suggestions(value))
        elif field_name == "solution":
            suggestions.extend(self._get_solution_suggestions(value))
        elif field_name == "change":
            if not self._contains_numbers(value):
                warnings.append("구체적인 수치를 포함해보세요.")
            suggestions.extend(self._get_change_suggestions(value))
        elif field_name == "measurement":
            if not self._is_specific_measurement(value):
                warnings.append("측정 방법을 더 구체적으로 설명해보세요.")
            suggestions.extend(self._get_measurement_suggestions(value))
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "suggestions": suggestions
        }
    
    def _get_field_korean_name(self, field: str) -> str:
        """필드명의 한국어 이름 반환"""
        names = {
            "problem": "해결하고 싶은 문제",
            "target": "대상 그룹",
            "solution": "솔루션 방법",
            "change": "기대하는 변화",
            "measurement": "측정 방법",
            "timeframe": "목표 기간"
        }
        return names.get(field, field)
    
    def _contains_numbers(self, text: str) -> bool:
        """텍스트에 숫자 포함 여부 확인"""
        return bool(re.search(r'\d+', text))
    
    def _contains_time_reference(self, text: str) -> bool:
        """시간 참조 포함 여부 확인"""
        time_keywords = ["개월", "년", "주", "일", "분기", "월", "주간"]
        return any(keyword in text for keyword in time_keywords)
    
    def _is_specific_measurement(self, text: str) -> bool:
        """측정 방법의 구체성 확인"""
        specific_keywords = ["설문", "조사", "데이터", "분석", "추적", "모니터링", "평가", "측정", "지표"]
        return any(keyword in text for keyword in specific_keywords) and len(text) > 10
    
    def _calculate_quality_score(self, steps: Dict[str, str], errors: List[str], warnings: List[str]) -> int:
        """품질 점수 계산 (0-100)"""
        
        if errors:
            return 0
        
        score = 100
        
        # 경고 하나당 -10점
        score -= len(warnings) * 10
        
        # 각 필드 길이에 따른 점수 조정
        for field, value in steps.items():
            if field in self.required_fields:
                length = len(value.strip())
                if length < 10:
                    score -= 5
                elif length > 50:
                    score += 5
        
        # 수치 포함 보너스
        if self._contains_numbers(steps.get("change", "")):
            score += 10
        
        if self._contains_time_reference(steps.get("timeframe", "")):
            score += 10
        
        return max(0, min(100, score))
    
    def _get_problem_suggestions(self, text: str) -> List[str]:
        """문제 정의 개선 제안"""
        suggestions = []
        
        if len(text) < 20:
            suggestions.append("문제를 더 구체적으로 설명해보세요.")
        
        if "어려워" not in text and "힘들어" not in text and "문제" not in text:
            suggestions.append("구체적인 어려움이나 문제점을 언급해보세요.")
        
        if not any(word in text for word in ["사람", "고객", "사용자", "청년", "시니어"]):
            suggestions.append("영향받는 사람들을 구체적으로 언급해보세요.")
        
        return suggestions
    
    def _get_target_suggestions(self, text: str) -> List[str]:
        """대상 그룹 개선 제안"""
        suggestions = []
        
        if not self._contains_numbers(text):
            suggestions.append("대상 그룹의 규모를 수치로 표현해보세요. (예: 1000명, 100개 기업)")
        
        demographics = ["청년", "시니어", "학생", "직장인", "주부", "사업자"]
        if not any(demo in text for demo in demographics):
            suggestions.append("대상의 특성을 더 구체적으로 표현해보세요.")
        
        return suggestions
    
    def _get_solution_suggestions(self, text: str) -> List[str]:
        """솔루션 개선 제안"""
        suggestions = []
        
        tech_keywords = ["앱", "플랫폼", "AI", "서비스", "시스템"]
        if not any(keyword in text for keyword in tech_keywords):
            suggestions.append("솔루션의 형태나 방식을 더 구체적으로 설명해보세요.")
        
        if "통해" not in text and "으로" not in text:
            suggestions.append("솔루션이 문제를 해결하는 방식을 설명해보세요.")
        
        return suggestions
    
    def _get_change_suggestions(self, text: str) -> List[str]:
        """변화 개선 제안"""
        suggestions = []
        
        if not self._contains_numbers(text):
            suggestions.append("변화의 정도를 구체적인 수치로 표현해보세요. (예: 30% 개선, 2배 증가)")
        
        positive_keywords = ["개선", "향상", "증가", "감소", "해결"]
        if not any(keyword in text for keyword in positive_keywords):
            suggestions.append("긍정적인 변화의 방향을 명확히 해보세요.")
        
        return suggestions
    
    def _get_measurement_suggestions(self, text: str) -> List[str]:
        """측정 방법 개선 제안"""
        suggestions = []
        
        if len(text) < 15:
            suggestions.append("측정 방법을 더 구체적으로 설명해보세요.")
        
        measurement_methods = ["설문조사", "데이터 분석", "인터뷰", "관찰", "테스트", "평가"]
        if not any(method in text for method in measurement_methods):
            suggestions.append("구체적인 측정 방법을 언급해보세요. (예: 설문조사, 사용 데이터 분석)")
        
        return suggestions
    
    def check_story_completeness(self, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """완성된 스토리의 완성도 확인"""
        
        completeness_score = 0
        missing_elements = []
        
        # 필수 요소 확인
        required_elements = {
            "headline": "헤드라인",
            "key_metrics": "핵심 지표", 
            "problem_context": "문제 맥락",
            "solution_approach": "솔루션 접근법",
            "expected_impact": "기대 임팩트",
            "measurement_plan": "측정 계획"
        }
        
        for element, korean_name in required_elements.items():
            if element in story_data and story_data[element]:
                completeness_score += 16.67  # 100/6
            else:
                missing_elements.append(korean_name)
        
        return {
            "completeness_score": round(completeness_score, 1),
            "missing_elements": missing_elements,
            "is_complete": len(missing_elements) == 0,
            "quality_level": self._get_quality_level(completeness_score)
        }
    
    def _get_quality_level(self, score: float) -> str:
        """품질 수준 반환"""
        if score >= 90:
            return "우수"
        elif score >= 70:
            return "양호"
        elif score >= 50:
            return "보통"
        else:
            return "개선 필요"