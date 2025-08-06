"""
TDD 테스트 케이스 - Impact Story Builder
실패하는 테스트부터 시작해서 점진적으로 기능 구현
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from api.impact_story.builder import ImpactStoryBuilder
from api.impact_story.validator import StoryValidator  
from api.impact_story.templates import StoryTemplates


class TestImpactStoryBuilder:
    """Impact Story Builder 핵심 기능 테스트"""
    
    def setup_method(self):
        """각 테스트 전 실행"""
        self.builder = ImpactStoryBuilder()
        self.sample_steps = {
            "problem": "청년들이 정신건강 상담을 받기 어려워해요",
            "target": "20-30대 직장인 청년 1000명",
            "solution": "AI 기반 24시간 익명 심리상담 챗봇",
            "change": "우울증 지수(PHQ-9) 30% 개선",
            "measurement": "6개월 간격으로 PHQ-9 설문조사 실시",
            "timeframe": "6개월"
        }
    
    def test_build_story_success(self):
        """정상적인 스토리 생성 테스트"""
        result = self.builder.build_story_from_steps(self.sample_steps)
        
        assert result["success"] is True
        assert "story" in result
        assert "headline" in result["story"]
        assert "key_metrics" in result["story"]
        assert len(result["story"]["key_metrics"]) == 3
    
    def test_headline_generation(self):
        """헤드라인 생성 테스트"""
        result = self.builder.build_story_from_steps(self.sample_steps)
        headline = result["story"]["headline"]
        
        # 모든 핵심 요소가 포함되어야 함
        assert "청년들이 정신건강 상담을 받기 어려워해요" in headline
        assert "AI 기반 24시간 익명 심리상담 챗봇" in headline
        assert "20-30대 직장인 청년 1000명" in headline
        assert "우울증 지수(PHQ-9) 30% 개선" in headline
        assert "6개월" in headline
    
    def test_key_metrics_extraction(self):
        """핵심 지표 추출 테스트"""
        result = self.builder.build_story_from_steps(self.sample_steps)
        metrics = result["story"]["key_metrics"]
        
        # 3개 메트릭이 있어야 함
        assert len(metrics) == 3
        
        # 각 메트릭 타입 확인
        metric_types = [m["type"] for m in metrics]
        assert "reach" in metric_types
        assert "depth" in metric_types
        assert "speed" in metric_types
        
        # 수치 추출 확인
        depth_metric = next(m for m in metrics if m["type"] == "depth")
        assert "30%" in depth_metric["value"] or "측정 필요" in depth_metric["value"]
    
    def test_empty_input_validation(self):
        """빈 입력에 대한 검증 테스트"""
        empty_steps = {
            "problem": "",
            "target": "",
            "solution": "",
            "change": "",
            "measurement": ""
        }
        
        result = self.builder.build_story_from_steps(empty_steps)
        assert result["success"] is False
        assert "error" in result
    
    def test_partial_input_handling(self):
        """부분 입력 처리 테스트"""
        partial_steps = {
            "problem": "청년 정신건강 문제",
            "target": "청년들",
            "solution": "AI 상담",
            "change": "",  # 빈 값
            "measurement": ""
        }
        
        result = self.builder.build_story_from_steps(partial_steps)
        # 검증 실패해야 함
        assert result["success"] is False


class TestStoryValidator:
    """Story Validator 테스트"""
    
    def setup_method(self):
        self.validator = StoryValidator()
        self.valid_steps = {
            "problem": "청년들이 정신건강 상담을 받기 어려워해요",
            "target": "20-30대 직장인 청년 1000명", 
            "solution": "AI 기반 24시간 익명 심리상담 챗봇",
            "change": "우울증 지수(PHQ-9) 30% 개선",
            "measurement": "6개월 간격으로 PHQ-9 설문조사 실시"
        }
    
    def test_valid_input_validation(self):
        """유효한 입력 검증 테스트"""
        result = self.validator.validate_steps(self.valid_steps)
        
        assert result["valid"] is True
        assert len(result["errors"]) == 0
        assert result["quality_score"] > 70
    
    def test_missing_fields_validation(self):
        """필수 필드 누락 검증 테스트"""
        invalid_steps = self.valid_steps.copy()
        invalid_steps["problem"] = ""  # 필수 필드 비움
        
        result = self.validator.validate_steps(invalid_steps)
        
        assert result["valid"] is False
        assert len(result["errors"]) > 0
        assert "해결하고 싶은 문제" in str(result["errors"])
    
    def test_short_input_warning(self):
        """짧은 입력에 대한 경고 테스트"""
        short_steps = self.valid_steps.copy()
        short_steps["problem"] = "문제"  # 너무 짧음
        
        result = self.validator.validate_steps(short_steps)
        
        assert len(result["warnings"]) > 0
        assert result["quality_score"] < 100
    
    def test_numeric_validation(self):
        """수치 포함 검증 테스트"""
        no_number_steps = self.valid_steps.copy()
        no_number_steps["change"] = "많이 개선"  # 수치 없음
        
        result = self.validator.validate_steps(no_number_steps)
        
        assert len(result["warnings"]) > 0
        assert any("수치" in warning for warning in result["warnings"])


class TestStoryTemplates:
    """Story Templates 테스트"""
    
    def setup_method(self):
        self.templates = StoryTemplates()
    
    def test_template_loading(self):
        """템플릿 로딩 테스트"""
        all_templates = self.templates.get_all_templates()
        
        assert "education" in all_templates
        assert "healthcare" in all_templates
        assert "environment" in all_templates
        assert "general" in all_templates
    
    def test_template_suggestion(self):
        """템플릿 제안 테스트"""
        education_text = "청년들이 코딩 교육을 받기 어려워해요"
        suggested = self.templates.suggest_template(education_text)
        assert suggested == "education"
        
        healthcare_text = "고혈압 환자들이 약물 복용을 놓쳐요"
        suggested = self.templates.suggest_template(healthcare_text)
        assert suggested == "healthcare"
        
        unknown_text = "알 수 없는 문제입니다"
        suggested = self.templates.suggest_template(unknown_text)
        assert suggested == "general"
    
    def test_sample_story_generation(self):
        """샘플 스토리 생성 테스트"""
        sample = self.templates.get_sample_story("education")
        
        assert "problem" in sample
        assert "target" in sample
        assert "solution" in sample
        assert "change" in sample
        assert len(sample["problem"]) > 10


class TestAPIEndpoints:
    """API 엔드포인트 테스트"""
    
    @pytest.fixture
    def client(self):
        """테스트 클라이언트 생성"""
        from main import app
        return TestClient(app)
    
    @pytest.fixture  
    def auth_token(self):
        """테스트용 JWT 토큰 생성"""
        from main import create_access_token
        return create_access_token({"api_key": "test_key", "sub": "test_user"})
    
    def test_impact_page_access(self, client):
        """임팩트 페이지 접근 테스트"""
        response = client.get("/impact")
        assert response.status_code == 200
    
    def test_story_build_api_without_auth(self, client):
        """인증 없이 스토리 생성 API 호출 테스트"""
        story_data = {
            "problem": "테스트 문제",
            "target": "테스트 대상",
            "solution": "테스트 솔루션",
            "change": "테스트 변화",
            "measurement": "테스트 측정"
        }
        
        response = client.post("/api/impact-story/build", json=story_data)
        assert response.status_code == 401  # 인증 오류
    
    def test_story_build_api_with_auth(self, client, auth_token):
        """인증 후 스토리 생성 API 호출 테스트"""
        story_data = {
            "problem": "청년들이 정신건강 상담을 받기 어려워해요",
            "target": "20-30대 직장인 청년 1000명",
            "solution": "AI 기반 24시간 익명 심리상담 챗봇", 
            "change": "우울증 지수(PHQ-9) 30% 개선",
            "measurement": "6개월 간격으로 PHQ-9 설문조사 실시",
            "timeframe": "6개월"
        }
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.post("/api/impact-story/build", json=story_data, headers=headers)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "story" in result
    
    def test_templates_api(self, client):
        """템플릿 API 테스트"""
        response = client.get("/api/impact-story/templates")
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] is True
        assert "templates" in result


class TestAdvancedFeatures:
    """고급 기능 테스트"""
    
    def setup_method(self):
        self.builder = ImpactStoryBuilder()
    
    def test_story_component_update(self):
        """스토리 컴포넌트 업데이트 테스트"""
        initial_story = {
            "headline": "초기 헤드라인",
            "problem_context": {"problem_statement": "초기 문제"},
            "key_metrics": []
        }
        
        updated_story = self.builder.update_story_component(
            initial_story, "problem", "새로운 문제 설명"
        )
        
        assert updated_story is not None
        # 실제 업데이트 로직은 구현에 따라 달라짐
    
    def test_quality_score_calculation(self):
        """품질 점수 계산 테스트"""
        validator = StoryValidator()
        
        high_quality_steps = {
            "problem": "청년들이 정신건강 상담을 받기 어려워하는 문제가 심각합니다. 특히 직장인들은 시간과 비용 부담으로 상담을 기피합니다.",
            "target": "20-30대 직장인 청년 1000명을 대상으로 합니다",
            "solution": "AI 기반 24시간 접근 가능한 익명 심리상담 챗봇을 개발하여 언제든지 상담받을 수 있게 합니다",
            "change": "우울증 지수(PHQ-9) 점수를 30% 개선하여 정상 범위로 회복시킵니다",
            "measurement": "6개월 간격으로 표준화된 PHQ-9 설문조사를 실시하고 전후 비교 분석합니다"
        }
        
        result = validator.validate_steps(high_quality_steps)
        assert result["quality_score"] > 80
    
    def test_error_handling(self):
        """에러 처리 테스트"""
        builder = ImpactStoryBuilder()
        
        # None 입력 테스트
        result = builder.build_story_from_steps(None)
        assert result["success"] is False
        
        # 잘못된 형식 입력 테스트
        result = builder.build_story_from_steps("invalid_input")
        assert result["success"] is False


# 통합 테스트
class TestIntegration:
    """전체 플로우 통합 테스트"""
    
    def test_complete_story_generation_flow(self):
        """완전한 스토리 생성 플로우 테스트"""
        # 1. 템플릿 선택
        templates = StoryTemplates()
        suggested_template = templates.suggest_template("청년 정신건강 문제")
        assert suggested_template in ["healthcare", "general"]
        
        # 2. 입력 검증
        validator = StoryValidator()
        steps = {
            "problem": "청년들이 정신건강 상담을 받기 어려워해요",
            "target": "20-30대 직장인 청년 1000명",
            "solution": "AI 기반 24시간 익명 심리상담 챗봇",
            "change": "우울증 지수(PHQ-9) 30% 개선", 
            "measurement": "6개월 간격으로 PHQ-9 설문조사 실시"
        }
        
        validation_result = validator.validate_steps(steps)
        assert validation_result["valid"] is True
        
        # 3. 스토리 생성
        builder = ImpactStoryBuilder()
        story_result = builder.build_story_from_steps(steps)
        
        assert story_result["success"] is True
        assert len(story_result["story"]["key_metrics"]) == 3
        assert story_result["story"]["headline"] is not None
        
        # 4. 품질 확인
        assert validation_result["quality_score"] > 50


if __name__ == "__main__":
    # 간단한 테스트 실행
    pytest.main([__file__, "-v"])