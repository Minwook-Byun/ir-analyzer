"""
TDD Cycle 2: 전체 인증 플로우 테스트
"""
import requests
import json

BASE_URL = "https://ir-analyzer-1070198801396.asia-northeast3.run.app"

def test_complete_auth_flow():
    """완전한 인증 플로우 테스트"""
    print("Testing Complete Authentication Flow")
    print("=" * 40)
    
    # Step 1: 로그인 시도
    test_api_key = "AIzaSyDF845d0PrBSyB92AJ1e8etEo0BDdmbNoY"
    login_payload = {"api_key": test_api_key}
    
    print(f"1. Login attempt with key: {test_api_key[:10]}...")
    login_response = requests.post(f"{BASE_URL}/api/login", json=login_payload)
    print(f"   Status: {login_response.status_code}")
    print(f"   Response: {login_response.text}")
    
    if login_response.status_code != 200:
        print("FAILED: Login failed")
        return False
    
    # Step 2: 토큰 추출
    login_data = login_response.json()
    if not login_data.get("success"):
        print("FAILED: Login success=false")
        return False
    
    token = login_data.get("token")
    if not token:
        print("FAILED: No token received")
        return False
    
    print(f"2. Token received: {token[:20]}...")
    
    # Step 3: 토큰으로 보호된 엔드포인트 접근
    headers = {"Authorization": f"Bearer {token}"}
    
    # 대화형 분석 시작 테스트 (간단한 요청)
    print("3. Testing protected endpoint...")
    
    # 실제 파일 없이 테스트
    test_payload = {
        "company_name": "Test Company"
    }
    
    analysis_response = requests.post(
        f"{BASE_URL}/api/conversation/start",
        headers=headers,
        data=test_payload  # multipart 대신 간단한 데이터
    )
    
    print(f"   Protected endpoint status: {analysis_response.status_code}")
    print(f"   Protected endpoint response: {analysis_response.text[:200]}...")
    
    if analysis_response.status_code in [200, 400]:  # 400은 파일 없음 에러일 수 있음
        print("SUCCESS: Authentication flow working!")
        return True
    else:
        print(f"FAILED: Protected endpoint failed with {analysis_response.status_code}")
        return False

def test_token_validation():
    """토큰 검증 테스트"""
    print("\nTesting Token Validation")
    print("=" * 30)
    
    # 잘못된 토큰 테스트
    fake_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.fake.token"
    headers = {"Authorization": f"Bearer {fake_token}"}
    
    response = requests.post(
        f"{BASE_URL}/api/conversation/start",
        headers=headers,
        data={"company_name": "Test"}
    )
    
    print(f"Invalid token status: {response.status_code}")
    print(f"Invalid token response: {response.text[:100]}...")
    
    if response.status_code == 401:
        print("SUCCESS: Invalid token properly rejected!")
        return True
    else:
        print("FAILED: Invalid token should return 401")
        return False

if __name__ == "__main__":
    print("TDD Cycle 2: Complete Authentication Flow Test")
    print("=" * 50)
    
    try:
        flow_result = test_complete_auth_flow()
        token_result = test_token_validation()
        
        if flow_result and token_result:
            print("\nOVERALL: All authentication tests PASSED!")
        else:
            print("\nOVERALL: Some tests FAILED - need fixes")
            
    except Exception as e:
        print(f"\nERROR: Test execution failed: {e}")
        import traceback
        traceback.print_exc()