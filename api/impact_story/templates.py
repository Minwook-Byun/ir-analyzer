"""
Story Templates - 임팩트 영역별 템플릿
"""

from typing import Dict, List, Any


class StoryTemplates:
    """임팩트 스토리 템플릿 관리"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """템플릿 로드"""
        return {
            "education": {
                "name": "교육/역량강화",
                "description": "교육과 역량 개발을 통한 임팩트",
                "headline_template": "우리는 {problem}을 {solution}으로 해결해서 {target}의 학습 역량을 {change} 향상시키고 싶습니다.",
                "key_questions": [
                    "어떤 교육 격차나 학습 문제를 해결하고 싶나요?",
                    "누구를 위한 교육 솔루션인가요?",
                    "어떤 방식으로 교육을 제공할 건가요?",
                    "학습자들에게 어떤 변화가 일어날까요?",
                    "그 변화를 어떻게 측정할 건가요?"
                ],
                "sample_metrics": [
                    {"name": "학습 완료율", "unit": "%", "example": "80%"},
                    {"name": "역량 향상도", "unit": "점", "example": "7.5/10점"},
                    {"name": "취업률 개선", "unit": "%", "example": "40% 증가"}
                ],
                "success_stories": [
                    "코딩 교육을 통해 청년 취업률 50% 향상",
                    "디지털 리터러시 교육으로 시니어 디지털 격차 해소"
                ]
            },
            
            "healthcare": {
                "name": "헬스케어/웰빙",
                "description": "건강과 웰빙 개선을 통한 임팩트",
                "headline_template": "우리는 {problem}을 {solution}으로 해결해서 {target}의 건강 상태를 {change} 개선하고 싶습니다.",
                "key_questions": [
                    "어떤 건강 문제나 의료 접근성 이슈를 해결하고 싶나요?",
                    "누구의 건강을 개선하고 싶나요?",
                    "어떤 헬스케어 솔루션을 제공할 건가요?",
                    "건강 상태에 어떤 개선이 일어날까요?",
                    "건강 개선을 어떻게 측정할 건가요?"
                ],
                "sample_metrics": [
                    {"name": "건강 지표 개선", "unit": "%", "example": "혈압 20% 개선"},
                    {"name": "의료 접근성", "unit": "배", "example": "2배 증가"},
                    {"name": "예방 행동 실천", "unit": "%", "example": "70% 실천율"}
                ],
                "success_stories": [
                    "당뇨 관리 앱으로 혈당 조절률 30% 향상",
                    "원격 진료로 농촌 지역 의료 접근성 3배 개선"
                ]
            },
            
            "environment": {
                "name": "환경/지속가능성",
                "description": "환경 보호와 지속가능성을 위한 임팩트",
                "headline_template": "우리는 {problem}을 {solution}으로 해결해서 {target}의 환경 영향을 {change} 줄이고 싶습니다.",
                "key_questions": [
                    "어떤 환경 문제를 해결하고 싶나요?",
                    "누구의 환경 행동을 바꾸고 싶나요?",
                    "어떤 친환경 솔루션을 제공할 건가요?",
                    "환경에 어떤 긍정적 변화가 일어날까요?",
                    "환경 개선을 어떻게 측정할 건가요?"
                ],
                "sample_metrics": [
                    {"name": "탄소 발자국 감소", "unit": "tCO2", "example": "100tCO2 절약"},
                    {"name": "재활용률 증가", "unit": "%", "example": "50% 증가"},
                    {"name": "친환경 행동 실천", "unit": "%", "example": "80% 참여율"}
                ],
                "success_stories": [
                    "플라스틱 대체재로 연간 50톤 플라스틱 절약",
                    "에너지 효율화로 탄소 배출 40% 감소"
                ]
            },
            
            "general": {
                "name": "일반/기타",
                "description": "다양한 사회 문제 해결을 위한 임팩트",
                "headline_template": "우리는 {problem}을 {solution}으로 해결해서 {target}의 삶을 {change} 개선하고 싶습니다.",
                "key_questions": [
                    "어떤 사회 문제를 해결하고 싶나요?",
                    "누구를 위한 솔루션인가요?",
                    "어떤 방식으로 문제를 해결할 건가요?",
                    "어떤 긍정적 변화가 일어날까요?",
                    "그 변화를 어떻게 측정할 건가요?"
                ],
                "sample_metrics": [
                    {"name": "문제 해결률", "unit": "%", "example": "60% 해결"},
                    {"name": "만족도 향상", "unit": "점", "example": "8/10점"},
                    {"name": "참여율 증가", "unit": "%", "example": "75% 참여"}
                ],
                "success_stories": [
                    "소상공인 디지털 전환으로 매출 25% 증가",
                    "커뮤니티 플랫폼으로 지역 소통 활성화"
                ]
            }
        }
    
    def get_template(self, template_type: str) -> Dict[str, Any]:
        """특정 템플릿 반환"""
        return self.templates.get(template_type, self.templates["general"])
    
    def get_all_templates(self) -> Dict[str, Dict[str, Any]]:
        """모든 템플릿 반환"""
        return self.templates
    
    def suggest_template(self, problem_text: str) -> str:
        """문제 설명에서 적합한 템플릿 제안"""
        problem_lower = problem_text.lower()
        
        # 키워드 기반 템플릿 매칭
        keyword_mapping = {
            "education": ["교육", "학습", "역량", "스킬", "교육과정", "강의", "학교", "대학"],
            "healthcare": ["건강", "의료", "치료", "병원", "약", "질병", "헬스케어", "웰빙"],
            "environment": ["환경", "기후", "탄소", "재활용", "친환경", "지속가능", "에너지"]
        }
        
        for template_type, keywords in keyword_mapping.items():
            if any(keyword in problem_lower for keyword in keywords):
                return template_type
        
        return "general"
    
    def get_sample_story(self, template_type: str) -> Dict[str, str]:
        """샘플 스토리 반환"""
        samples = {
            "education": {
                "problem": "청년들이 실무형 코딩 교육을 받기 어려워해요",
                "target": "취업 준비생 청년들",
                "solution": "1:1 멘토링이 포함된 온라인 코딩 부트캠프",
                "change": "취업률 50% 향상",
                "timeframe": "6개월",
                "measurement": "수료생 취업률 추적 조사"
            },
            "healthcare": {
                "problem": "고혈압 환자들이 약물 복용을 자주 놓쳐요",
                "target": "고혈압 환자 1000명",
                "solution": "AI 기반 복약 관리 앱",
                "change": "복약 순응도 80% 향상",
                "timeframe": "3개월",
                "measurement": "앱 로그 데이터와 혈압 측정 결과"
            },
            "environment": {
                "problem": "일회용 플라스틱 사용량이 너무 많아요",
                "target": "카페 이용 고객들",
                "solution": "리유저블 컵 공유 서비스",
                "change": "플라스틱 컵 사용량 70% 감소",
                "timeframe": "1년",
                "measurement": "참여 카페의 일회용 컵 구매량 비교"
            }
        }
        
        return samples.get(template_type, samples["education"])
    
    def get_inspiration_prompts(self, template_type: str) -> List[str]:
        """영감을 주는 질문들"""
        prompts = {
            "education": [
                "어떤 기술이나 지식을 배우고 싶어하는 사람들을 보셨나요?",
                "기존 교육 방식에서 아쉬웠던 점은 무엇인가요?",
                "만약 누구나 쉽게 배울 수 있다면 어떤 변화가 생길까요?"
            ],
            "healthcare": [
                "주변에서 의료/건강 관련해서 불편함을 느낀 경험이 있나요?",
                "예방 가능한 질병이나 건강 문제가 있다고 생각하시나요?",
                "건강 관리가 더 쉬워진다면 어떤 변화가 생길까요?"
            ],
            "environment": [
                "일상에서 환경에 부담을 주는 것들을 발견한 적 있나요?",
                "친환경적인 행동을 하고 싶지만 어려웠던 이유는 무엇인가요?",
                "환경 문제가 해결된다면 미래 세대에게 어떤 의미일까요?"
            ]
        }
        
        return prompts.get(template_type, [
            "어떤 문제를 해결하고 싶으신가요?",
            "그 문제로 누가 어려움을 겪고 있나요?",
            "해결되면 어떤 변화가 생길까요?"
        ])