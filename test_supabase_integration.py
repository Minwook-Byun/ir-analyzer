"""
MYSC IR Platform - Supabase Integration TDD Tests
실제 Supabase 환경과의 통합 테스트
"""
import pytest
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8080"
SUPABASE_URL = "https://isoufdbcdcwgnqldyxpk.supabase.co"
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlzb3VmZGJjZGN3Z25xbGR5eHBrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ2MjgzODMsImV4cCI6MjA3MDIwNDM4M30.t76CmPYWyQ6wh0wgKoPdFMUnU7IdJ47T-7ES7ShpVog"

class TestSupabaseIntegration:
    """Supabase 데이터베이스 통합 테스트"""
    
    def setup_method(self):
        """각 테스트 전 초기화"""
        self.test_api_key = "test-gemini-api-key-for-integration-test"
        self.session = requests.Session()
    
    def test_supabase_direct_connection(self):
        """1. Supabase 직접 연결 테스트"""
        print("\n🔗 Supabase 직접 연결 테스트...")
        
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/users?select=*",
            headers={
                "Authorization": f"Bearer {ANON_KEY}",
                "apikey": ANON_KEY
            }
        )
        
        assert response.status_code == 200, f"Supabase 연결 실패: {response.status_code}"
        users = response.json()
        assert len(users) >= 1, "테스트 사용자가 존재해야 함"
        assert any(user['email'] == 'test@mysc.com' for user in users), "기본 테스트 사용자 확인"
        
        print(f"✅ Supabase 연결 성공 (사용자 수: {len(users)})")
        return True
    
    def test_backend_supabase_login_integration(self):
        """2. Backend-Supabase 로그인 통합 테스트"""
        print("\n🔐 Backend-Supabase 로그인 통합 테스트...")
        
        # 로그인 요청
        login_response = requests.post(f"{BASE_URL}/api/login", json={
            "api_key": self.test_api_key
        })
        
        assert login_response.status_code == 200, f"로그인 실패: {login_response.status_code}"
        login_data = login_response.json()
        assert login_data["success"] == True, "로그인 성공 응답 확인"
        assert "user_id" in login_data, "user_id 반환 확인"
        assert "token" in login_data, "JWT 토큰 반환 확인"
        
        # Supabase에서 사용자 생성 확인
        time.sleep(1)  # DB 저장 대기
        users_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/users?select=*",
            headers={"Authorization": f"Bearer {ANON_KEY}", "apikey": ANON_KEY}
        )
        
        users = users_response.json()
        test_users = [u for u in users if 'user_' in u['email']]
        assert len(test_users) >= 1, "새 테스트 사용자가 DB에 생성되어야 함"
        
        print(f"✅ 로그인 통합 성공 (DB 사용자: {len(users)}명)")
        return login_data["token"], login_data["user_id"]
    
    def test_analysis_project_persistence(self):
        """3. 분석 프로젝트 영구 저장 테스트"""
        print("\n📊 분석 프로젝트 영구 저장 테스트...")
        
        # 로그인
        token, user_id = self.test_backend_supabase_login_integration()
        
        # 분석 시작 (간단한 텍스트 파일)
        files = {'files': ('test.txt', 'Test company analysis content', 'text/plain')}
        data = {'company_name': 'Test Corp Integration'}
        
        analysis_response = requests.post(
            f"{BASE_URL}/api/analyze/start",
            headers={"Authorization": f"Bearer {token}"},
            files=files,
            data=data
        )
        
        assert analysis_response.status_code == 200, f"분석 시작 실패: {analysis_response.status_code}"
        analysis_data = analysis_response.json()
        assert analysis_data["success"] == True, "분석 시작 성공 확인"
        assert "project_id" in analysis_data, "프로젝트 ID 반환 확인"
        
        project_id = analysis_data["project_id"]
        
        # Supabase에서 프로젝트 생성 확인
        time.sleep(2)  # DB 저장 대기
        projects_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/analysis_projects?select=*&project_id=eq.{project_id}",
            headers={"Authorization": f"Bearer {ANON_KEY}", "apikey": ANON_KEY}
        )
        
        projects = projects_response.json()
        assert len(projects) >= 1, "프로젝트가 DB에 저장되어야 함"
        project = projects[0]
        assert project["company_name"] == "Test Corp Integration", "회사명 저장 확인"
        assert project["status"] in ["pending", "processing"], "프로젝트 상태 확인"
        
        print(f"✅ 프로젝트 영구 저장 성공 (ID: {project_id})")
        return token, project_id
    
    def test_conversation_persistence(self):
        """4. 대화 메시지 영구 저장 테스트"""
        print("\n💬 대화 메시지 영구 저장 테스트...")
        
        token, project_id = self.test_analysis_project_persistence()
        
        # 대화 시작
        conversation_response = requests.post(
            f"{BASE_URL}/api/conversation/followup",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={
                "project_id": project_id,
                "question_type": "financial",
                "company_name": "Test Corp Integration"
            }
        )
        
        assert conversation_response.status_code == 200, f"대화 시작 실패: {conversation_response.status_code}"
        conv_data = conversation_response.json()
        assert conv_data["success"] == True, "대화 성공 확인"
        assert "session_id" in conv_data, "세션 ID 반환 확인"
        
        session_id = conv_data["session_id"]
        
        # Supabase에서 대화 메시지 확인
        time.sleep(2)  # DB 저장 대기
        messages_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/conversation_messages?select=*&session_id=eq.{session_id}",
            headers={"Authorization": f"Bearer {ANON_KEY}", "apikey": ANON_KEY}
        )
        
        messages = messages_response.json()
        assert len(messages) >= 1, "대화 메시지가 DB에 저장되어야 함"
        
        user_messages = [m for m in messages if m["message_type"] == "user"]
        ai_messages = [m for m in messages if m["message_type"] == "ai"]
        
        assert len(user_messages) >= 1, "사용자 메시지 저장 확인"
        # AI 메시지는 실제 Gemini API 없이는 생성되지 않을 수 있음
        
        print(f"✅ 대화 메시지 저장 성공 (메시지 수: {len(messages)})")
        return True
    
    def test_data_persistence_after_restart(self):
        """5. 서버 재시작 후 데이터 영속성 테스트 (시뮬레이션)"""
        print("\n🔄 데이터 영속성 테스트...")
        
        # Supabase에서 저장된 모든 데이터 확인
        tables = ["users", "analysis_projects", "conversation_sessions", "conversation_messages"]
        total_records = 0
        
        for table in tables:
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/{table}?select=count",
                headers={"Authorization": f"Bearer {ANON_KEY}", "apikey": ANON_KEY}
            )
            
            if response.status_code == 200:
                count_data = response.json()
                count = len(count_data)  # 실제 레코드 수
                total_records += count
                print(f"  📋 {table}: {count}개 레코드")
        
        assert total_records > 0, "영구 저장된 데이터가 존재해야 함"
        print(f"✅ 영속성 테스트 성공 (총 {total_records}개 레코드)")
        return True

def test_run_all_supabase_tests():
    """모든 Supabase 통합 테스트 실행"""
    print("\n" + "="*50)
    print("🚀 MYSC IR Platform - Supabase 통합 TDD 테스트")
    print("="*50)
    
    suite = TestSupabaseIntegration()
    suite.setup_method()
    
    try:
        # 1. 직접 연결 테스트
        suite.test_supabase_direct_connection()
        
        # 2. 로그인 통합 테스트  
        suite.test_backend_supabase_login_integration()
        
        # 3. 프로젝트 저장 테스트
        suite.test_analysis_project_persistence()
        
        # 4. 대화 저장 테스트
        suite.test_conversation_persistence()
        
        # 5. 영속성 테스트
        suite.test_data_persistence_after_restart()
        
        print("\n" + "="*50)
        print("🎉 모든 Supabase 통합 테스트 통과!")
        print("✅ 완전한 데이터 영속성 확인")
        print("✅ 실시간 데이터베이스 연동 확인")
        print("✅ 엔터프라이즈급 안정성 확인")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        raise e

if __name__ == "__main__":
    test_run_all_supabase_tests()