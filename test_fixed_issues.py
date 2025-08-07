"""
Google Cloud Run 배포 전 문제 해결 테스트
1. 초기 화면이 로그인 페이지인지 확인
2. API 키 인증 후 세션 유지 테스트
"""

import requests
import json
import time

BASE_URL = "http://localhost:8080"

def test_initial_page():
    """초기 화면이 로그인 페이지로 리디렉션되는지 테스트"""
    print("1. 초기 화면 테스트...")
    response = requests.get(BASE_URL, allow_redirects=False)
    
    if response.status_code == 200:
        content = response.text
        if "/login" in content or "window.location.href = '/login'" in content:
            print("✓ 초기 화면이 로그인 페이지로 리디렉션됩니다.")
            return True
        else:
            print("✗ 초기 화면이 로그인 페이지로 리디렉션되지 않습니다.")
            return False
    else:
        print(f"✗ 예상치 못한 상태 코드: {response.status_code}")
        return False

def test_login_and_session():
    """API 키 로그인 및 세션 유지 테스트"""
    print("\n2. 로그인 및 세션 유지 테스트...")
    
    # 테스트용 API 키 (실제 키를 사용하세요)
    test_api_key = "AIzaSyC-test-key-please-replace-with-real"
    
    # 로그인 시도
    login_data = {"api_key": test_api_key}
    response = requests.post(
        f"{BASE_URL}/api/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            token = result.get("token")
            print(f"✓ 로그인 성공. 토큰 받음: {token[:20]}...")
            
            # 토큰으로 대화형 분석 시작 테스트
            print("\n3. 인증된 API 호출 테스트...")
            
            # FormData 준비
            files = {
                'company_name': (None, 'TestCompany'),
            }
            
            headers = {
                'Authorization': f'Bearer {token}'
            }
            
            response = requests.post(
                f"{BASE_URL}/api/conversation/start",
                files=files,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print("✓ API 호출 성공. 세션이 유지됩니다.")
                    print(f"  분석 ID: {result.get('conversation_id')}")
                    return True
                else:
                    print(f"✗ API 호출 실패: {result.get('error')}")
                    return False
            elif response.status_code == 401:
                print("✗ 인증 실패. 토큰이 유효하지 않습니다.")
                return False
            else:
                print(f"✗ API 호출 실패. 상태 코드: {response.status_code}")
                print(f"  응답: {response.text[:200]}")
                return False
        else:
            print(f"✗ 로그인 실패: {result.get('error')}")
            return False
    else:
        print(f"✗ 로그인 요청 실패. 상태 코드: {response.status_code}")
        return False

def test_cors_headers():
    """CORS 헤더 테스트"""
    print("\n4. CORS 헤더 테스트...")
    
    response = requests.options(
        f"{BASE_URL}/api/login",
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type, Authorization"
        }
    )
    
    cors_headers = response.headers
    if "Access-Control-Allow-Origin" in cors_headers:
        print(f"✓ CORS 헤더 존재: {cors_headers.get('Access-Control-Allow-Origin')}")
        return True
    else:
        print("✗ CORS 헤더가 없습니다.")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("MYSC IR Platform 문제 해결 테스트")
    print("=" * 50)
    
    print("\n서버가 실행 중인지 확인 중...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print("✓ 서버가 실행 중입니다.")
            print(f"  환경: {response.json().get('environment')}")
            print(f"  버전: {response.json().get('version')}")
        else:
            print("✗ 서버 응답이 비정상입니다.")
    except requests.exceptions.RequestException:
        print("✗ 서버에 연결할 수 없습니다. 먼저 서버를 실행하세요:")
        print("  python -m uvicorn api.index:app --host 0.0.0.0 --port 8080 --reload")
        exit(1)
    
    # 테스트 실행
    results = []
    results.append(test_initial_page())
    results.append(test_login_and_session())
    results.append(test_cors_headers())
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("테스트 결과 요약")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✓ 모든 테스트 통과 ({passed}/{total})")
        print("\n배포 준비 완료!")
        print("다음 명령으로 Google Cloud Run에 배포하세요:")
        print("  gcloud run deploy ir-analyzer --source . --region asia-northeast3")
    else:
        print(f"✗ 일부 테스트 실패 ({passed}/{total})")
        print("\n문제를 해결한 후 다시 테스트하세요.")