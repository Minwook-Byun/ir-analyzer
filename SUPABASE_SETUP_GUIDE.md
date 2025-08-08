# 🚀 MYSC IR Platform - Supabase 연동 가이드

## 1단계: Supabase 프로젝트 생성 (5분)

### A. Supabase 계정 생성
1. https://supabase.com 방문
2. "Start your project" 클릭
3. GitHub/Google 계정으로 로그인

### B. 새 프로젝트 생성
1. "New project" 클릭
2. **Organization**: 기본값 또는 새로 생성
3. **Project name**: `mysc-ir-platform`
4. **Database Password**: 강력한 패스워드 생성 (저장해두세요!)
5. **Region**: `Northeast Asia (Seoul)` 선택 (한국 서버)
6. **Pricing Plan**: `Free tier` 선택
7. "Create new project" 클릭

### C. 프로젝트 생성 완료 대기
- 약 2-3분 소요
- 완료되면 프로젝트 대시보드 접근 가능

## 2단계: 데이터베이스 스키마 생성 (2분)

### A. SQL Editor 접근
1. 좌측 메뉴에서 **"SQL Editor"** 클릭
2. "New query" 버튼 클릭

### B. 스키마 실행
1. `supabase_setup.sql` 파일 내용을 복사
2. SQL Editor에 붙여넣기
3. **"RUN"** 버튼 클릭 (Ctrl+Enter)
4. 성공 메시지 확인: "Success. No rows returned"

### C. 테이블 생성 확인
1. 좌측 메뉴에서 **"Table Editor"** 클릭
2. 다음 테이블들이 생성되었는지 확인:
   - ✅ `users`
   - ✅ `analysis_projects` 
   - ✅ `analysis_results`
   - ✅ `conversation_sessions`
   - ✅ `conversation_messages`
   - ✅ `api_usage`

## 3단계: API 키 및 환경변수 설정 (1분)

### A. API 키 복사
1. 좌측 메뉴에서 **"Settings"** → **"API"** 클릭
2. 다음 정보를 복사해두세요:
   - **Project URL**: `https://your-project.supabase.co`
   - **anon public key**: `eyJhbG...` (매우 긴 문자열)
   - **service_role key**: `eyJhbG...` (보안용, 백엔드에서만 사용)

### B. 환경변수 파일 업데이트
`.env` 파일에 다음 추가:
```env
# Supabase 설정
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 4단계: 연결 테스트 (1분)

### A. 브라우저에서 직접 테스트
다음 URL을 브라우저에 입력:
```
https://your-project.supabase.co/rest/v1/users?select=*
```

### B. 예상 응답
```json
[
  {
    "id": "uuid-string",
    "email": "test@mysc.com", 
    "api_key_hash": "test_hash_placeholder",
    "created_at": "2025-08-08T..."
  }
]
```

## 5단계: 다음 작업 준비

### A. 필요한 Python 패키지 설치
```bash
pip install httpx python-dotenv
```

### B. Backend 코드 수정 준비
- `api/index.py`에 Supabase 클라이언트 코드 추가
- 기존 메모리 기반 저장을 Supabase HTTP API로 변경

### C. Frontend 실시간 구독 준비  
- Supabase JavaScript 클라이언트 라이브러리 추가
- 실시간 대화 메시지 구독 설정

## 🎯 완료 체크리스트

- [ ] Supabase 프로젝트 생성 완료
- [ ] 6개 테이블 정상 생성 확인
- [ ] API URL 및 키 복사 완료
- [ ] `.env` 파일 업데이트 완료
- [ ] REST API 테스트 성공
- [ ] 다음 단계 준비 완료

## 🔧 문제 해결

### 문제: 테이블 생성 실패
**해결**: SQL Editor에서 에러 메시지 확인 후 스키마 수정

### 문제: API 호출 실패 (401 Unauthorized)
**해결**: API 키가 올바른지, RLS 정책이 적용되었는지 확인

### 문제: 실시간 구독 안됨  
**해결**: Realtime 설정에서 테이블별 실시간 활성화 필요

---
**다음**: Backend API 연동 및 실시간 기능 구현 🚀