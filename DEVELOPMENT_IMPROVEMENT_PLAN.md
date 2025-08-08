# MYSC IR Platform - 개선 및 개발 계획서

## 현재 상황 분석

### 0. 핵심 아키텍처 문제: 데이터베이스 부재 ⚠️

#### 0.1 현재 데이터 관리 방식
- **Frontend**: `localStorage`에 토큰 저장만
- **Backend**: 메모리 기반 임시 저장, 서버 재시작 시 모든 데이터 소실
- **문제점**: 분석 결과, 대화 내역, 사용자 세션이 영구 저장되지 않음

#### 0.2 DB 부재로 인한 치명적 문제들

**A. 분석 결과 손실**
- 사용자가 분석을 완료해도 브라우저 새로고침/종료 시 모든 결과 소실
- 비용이 발생하는 Gemini API 호출 결과를 재활용할 수 없음
- 과거 분석 데이터 비교/추적 불가능

**B. 대화 컨텍스트 손실**  
- 대화 중 연결이 끊어지면 이전 맥락 완전 소실
- `currentConversationId`가 메모리에만 존재하여 불안정
- 사용자가 여러 세션에서 연속적인 분석 불가능

**C. 사용자 관리 한계**
- JWT만으로 인증하지만 사용자 프로필/히스토리 없음  
- API 키 사용량 추적 불가능
- 다중 기기에서 동일한 분석 결과 접근 불가

**D. 확장성 문제**
- 서버 스케일링 시 상태 동기화 불가능
- 로드밸런싱 환경에서 세션 유지 어려움
- 백업/복구 전략 부재

### 1. 대화 기능 문제 분석

#### 1.1 현재 구조
- **Frontend**: `handleNotebookQuestion()` 함수가 `/api/conversation/followup` 엔드포인트 호출
- **Backend**: `perform_followup_analysis()` 함수가 Gemini API와 통신
- **문제점**: API 응답이 정상적으로 처리되지 않아 대화가 중단됨

#### 1.2 구체적 문제점들

**A. API 응답 처리 오류**
- `api/index.py:754-803`에서 응답 처리 로직 불완전
- 에러 핸들링이 제대로 구현되지 않음
- 응답 데이터가 UI에 제대로 렌더링되지 않음

**B. 상태 관리 문제**
- `currentConversationId`와 `currentAnalysisResult` 상태 동기화 이슈
- 이전 분석 컨텍스트가 후속 질문에 제대로 전달되지 않음

**C. UI 연결 문제**
- 응답 메시지가 대화창에 추가되지 않음
- 로딩 인디케이터가 제거되지 않는 경우 발생

### 2. UI 통합 문제 분석

#### 2.1 현재 구조
- **Analysis Complete 섹션**: 분석 결과를 카드 형태로 표시
- **대화창**: 별도의 영역에서 Q&A 처리
- **문제점**: 두 영역이 분리되어 있어 NotebookLM 스타일과 거리가 멀음

#### 2.2 NotebookLM 스타일 요구사항
- 단일 대화창에서 모든 상호작용 처리
- 분석 결과도 대화 메시지 형태로 표시
- 섹션별 탐색 버튼을 대화창 내 인라인으로 통합

## 해결 방안 및 개발 계획

### Phase 0: 데이터베이스 도입 (우선순위: 최고) 🔥

#### 0.1 데이터베이스 선택 기준
**추천: Supabase (PostgreSQL + REST API)** ⚡
- **즉시 사용 가능한 REST API**: SQL 없이 HTTP로 CRUD 가능
- **실시간 구독**: 대화 메시지 실시간 동기화
- **내장 인증**: JWT, OAuth 기본 지원  
- **Edge Functions**: 서버리스 로직 처리 가능
- **무료 티어**: 개발/초기 운영 비용 절약
- **벡터 검색**: pgvector 확장 지원
- **관리 편의성**: 웹 대시보드, 자동 백업

**Google Cloud SQL 대비 Supabase 장점**:
- ✅ API 개발 시간 **90% 단축** (ORM 설정 불필요)
- ✅ 실시간 기능 **기본 제공**
- ✅ 개발 복잡도 **대폭 감소**
- ✅ 운영 비용 **초기 무료**

#### 0.2 데이터 모델 설계

**테이블 구조**:
```sql
-- 사용자 테이블
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE,
    api_key_hash VARCHAR(255), -- 암호화된 API 키
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- 분석 프로젝트 테이블
CREATE TABLE analysis_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    company_name VARCHAR(255),
    file_names TEXT[], -- 업로드된 파일명들
    file_contents TEXT, -- 파일 내용 (암호화)
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);

-- 분석 결과 테이블  
CREATE TABLE analysis_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES analysis_projects(id),
    section_type VARCHAR(50), -- 'executive_summary', 'financial', etc.
    content JSONB, -- 분석 결과 JSON
    tokens_used INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 대화 세션 테이블
CREATE TABLE conversation_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES analysis_projects(id),
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    last_message_at TIMESTAMP DEFAULT NOW()
);

-- 대화 메시지 테이블
CREATE TABLE conversation_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES conversation_sessions(id),
    message_type VARCHAR(20), -- 'user', 'ai', 'system'
    content TEXT,
    metadata JSONB, -- 추가 정보 (토큰 수, 분석 타입 등)
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 0.3 구현 계획

**A. Supabase 프로젝트 설정** (5분 내 완료!)
- Supabase.com에서 새 프로젝트 생성
- 테이블 스키마를 SQL Editor에서 실행
- API URL과 anon key 환경변수 설정

**B. Backend 수정 (`api/index.py`)** - 극단적 단순화
```python
# Supabase 클라이언트만 추가
import httpx
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

# 예: 분석 결과 저장 (SQL 불필요!)
async def save_analysis_result(project_id, section_type, content):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SUPABASE_URL}/rest/v1/analysis_results",
            headers={"Authorization": f"Bearer {SUPABASE_KEY}"},
            json={
                "project_id": project_id,
                "section_type": section_type,
                "content": content
            }
        )
        return response.json()

# 예: 대화 메시지 저장
async def save_message(session_id, message_type, content):
    # 동일하게 간단한 HTTP POST
```

**C. Frontend도 직접 연결 가능** 
```javascript
// 프론트엔드에서 직접 Supabase 호출 가능
const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// 실시간 대화 구독
supabase
  .channel('conversations')
  .on('postgres_changes', { 
    event: 'INSERT', 
    schema: 'public', 
    table: 'conversation_messages' 
  }, (payload) => {
    // 새 메시지 실시간 표시
  })
  .subscribe();
```

**D. 주요 API 엔드포인트 변경**
- `/api/login`: Supabase Auth 또는 HTTP POST로 사용자 저장
- `/api/analyze/start`: HTTP POST로 프로젝트 생성
- `/api/conversation/followup`: HTTP POST로 메시지 저장
- 새로운 가능성: **Frontend에서 직접 히스토리 조회** 가능!

#### 0.4 예상 작업 시간 (Supabase로 대폭 단축!)
- Supabase 프로젝트 설정: **30분**
- 테이블 스키마 생성: **1시간**  
- Backend HTTP 클라이언트 연동: **4시간**
- Frontend 실시간 구독 설정: **3시간**
- 테스트 및 디버깅: **4시간**
- **총 예상 시간: 12.5시간** (기존 30시간 → **60% 단축**)

#### 0.5 Supabase의 즉각적인 이점
- 🔄 **분석 결과 영구 저장**: 새로고침해도 데이터 유지
- 📊 **사용량 추적**: API 비용 모니터링 가능
- 🔍 **히스토리 기능**: 과거 분석 재활용  
- 🛡️ **안정성 향상**: 서버 재시작에도 데이터 보존
- 📈 **확장성**: 다중 사용자 지원 기반 마련
- ⚡ **실시간 동기화**: 대화 메시지 즉시 반영
- 🎯 **개발 속도**: REST API로 빠른 프로토타이핑
- 💰 **비용 효율**: 무료 티어로 시작 가능
- 🔐 **보안**: Row Level Security 기본 지원
- 📊 **관리 편의**: 웹 대시보드에서 데이터 직접 확인

### Phase 1: 대화 기능 수정 (우선순위: 높음)

#### 1.1 Backend API 수정
**파일**: `api/index.py`
**수정 영역**: `line 1082-1111` (conversation/followup 엔드포인트)

```python
# 수정 예정 사항
1. 응답 형식 표준화
2. 에러 핸들링 강화
3. 응답 데이터 검증 추가
4. 로깅 시스템 추가
```

#### 1.2 Frontend 응답 처리 수정
**파일**: `public/static/js/app.js`
**수정 영역**: `line 754-820` (handleNotebookQuestion 함수)

```javascript
// 수정 예정 사항
1. 응답 데이터 파싱 로직 개선
2. 에러 처리 강화
3. 메시지 렌더링 로직 수정
4. 상태 관리 개선
```

#### 1.3 예상 작업 시간
- Backend 수정: 2시간
- Frontend 수정: 3시간
- 테스트 및 검증: 2시간
- **총 예상 시간: 7시간**

### Phase 2: UI 통합 (NotebookLM 스타일) (우선순위: 중간)

#### 2.1 아키텍처 변경 계획

**현재 구조**:
```
┌─────────────────────┐
│  Analysis Complete  │ ← 분석 결과 카드들
├─────────────────────┤
│    Conversation     │ ← 대화창
└─────────────────────┘
```

**목표 구조**:
```
┌─────────────────────┐
│                     │
│   Unified Chat      │ ← 모든 상호작용이 여기서
│                     │
│  - 분석 결과 메시지  │
│  - 섹션 탐색 버튼    │
│  - Q&A 대화         │
│                     │
└─────────────────────┘
```

#### 2.2 구체적 변경사항

**A. 분석 완료 후 처리 변경**
- 현재: 별도 섹션에 카드 표시
- 변경: 대화창에 분석 결과를 메시지로 표시

**B. 섹션 탐색 버튼 통합**
- 현재: Analysis Complete 섹션의 카드들
- 변경: 대화 메시지 하단에 인라인 버튼으로 표시

**C. 진행 흐름 개선**
```
1. 파일 업로드 → 분석 시작
2. Executive Summary를 첫 번째 메시지로 표시
3. 섹션 탐색 버튼들을 메시지 하단에 표시
4. 사용자가 섹션 클릭 시 해당 섹션 분석 결과를 새 메시지로 추가
5. 자유로운 Q&A 대화 가능
```

#### 2.3 수정 대상 파일들

**Frontend 주요 수정**:
- `public/static/js/app.js`:
  - `displayCompletedAnalysis()` 함수 제거/통합
  - `createMessage()` 함수 확장 (버튼 포함 메시지 지원)
  - `setupSectionExploration()` 로직 통합

**CSS 스타일 수정**:
- `public/static/css/app.css`:
  - Analysis Complete 섹션 스타일 제거
  - 인라인 버튼 스타일 추가
  - 메시지 내 버튼 그룹 스타일링

#### 2.4 예상 작업 시간
- 아키텍처 설계: 2시간
- Frontend 로직 변경: 6시간
- CSS 스타일링: 3시간
- 테스트 및 UX 조정: 4시간
- **총 예상 시간: 15시간**

### Phase 3: 추가 개선사항 (우선순위: 낮음)

#### 3.1 성능 최적화
- 메시지 가상화 (많은 대화 시)
- 이미지 lazy loading
- API 응답 캐싱

#### 3.2 UX 개선
- 타이핑 애니메이션 개선
- 메시지 검색 기능
- 대화 내역 저장/불러오기

## 구현 우선순위

### 🚨 Phase 0 (최우선 - 아키텍처 기반)
- [ ] Google Cloud SQL PostgreSQL 설정
- [ ] 데이터베이스 스키마 생성
- [ ] SQLAlchemy ORM 연동
- [ ] 사용자 인증 DB 마이그레이션
- [ ] 분석 결과 영구 저장 구현

### 🔥 Phase 1 (DB 연동 후 즉시 수정)
- [ ] Backend API 응답 처리 수정 (DB 기반)
- [ ] Frontend 에러 핸들링 개선
- [ ] 대화 기능 정상화 (DB 히스토리 포함)

### 📋 Phase 2 (주요 기능)
- [ ] UI 아키텍처 통합
- [ ] NotebookLM 스타일 구현
- [ ] 단일 대화창 통합
- [ ] 히스토리/검색 기능

### ⭐ Phase 3 (향후 개선)
- [ ] 성능 최적화 (DB 쿼리, 캐싱)
- [ ] 고급 분석 기능
- [ ] 사용자 대시보드

## 리스크 및 고려사항

### 기술적 리스크
1. **DB 마이그레이션 복잡성**: 기존 메모리 기반 → DB 기반 전환
2. **Cloud SQL 비용**: 관리형 DB 서비스 운영 비용 증가
3. **연결 관리**: Connection pool 설정 및 최적화 필요
4. **성능 이슈**: 단일 대화창에 많은 컨텐츠 로딩
5. **상태 관리**: 복잡한 대화 상태 동기화

### UX 리스크
1. **사용자 혼란**: 기존 UI에 익숙한 사용자
2. **가독성**: 긴 분석 결과의 대화창 표시
3. **접근성**: 모바일 환경에서의 사용성

## 성공 측정 지표

### 기능적 지표
- [ ] 대화 기능 정상 작동률 100%
- [ ] API 응답 시간 < 5초
- [ ] 에러 발생률 < 1%

### 사용자 경험 지표
- [ ] 사용자 작업 완료율 향상
- [ ] 평균 세션 시간 증가
- [ ] 사용자 만족도 개선

## 다음 단계

1. **Phase 1 즉시 착수**: 대화 기능 수정
2. **사용자 피드백 수집**: Phase 1 완료 후
3. **Phase 2 설계 검토**: 아키텍처 변경 전 상세 검토
4. **단계적 배포**: 기능별 점진적 롤아웃

---

*이 문서는 MYSC IR Platform의 핵심 개선사항을 다루며, 사용자 경험 향상과 기술적 안정성 확보를 목표로 합니다.*