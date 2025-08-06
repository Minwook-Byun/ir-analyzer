# 🔧 Vercel 대시보드 수동 설정 가이드
## 401 오류 해결을 위한 완전한 단계별 가이드

### 🎯 목표
`mysc-production` 프로젝트의 401 오류를 해결하고 MYSC IR 플랫폼을 완전히 활성화

---

## 📋 Step 1: Vercel 대시보드 접속

1. **브라우저에서 접속**: https://vercel.com/dashboard
2. **로그인 확인**: 현재 계정이 `mwbyun1220-4951`인지 확인
3. **팀 선택**: `minwooks-projects-4c467b76` 선택

---

## 📋 Step 2: mysc-production 프로젝트 선택

1. **프로젝트 목록**에서 `mysc-production` 클릭
2. **현재 상태 확인**:
   - Production URL: `https://mysc-production-k8it7vtnc-minwooks-projects-4c467b76.vercel.app`
   - 배포 상태가 Ready인지 확인

---

## 📋 Step 3: Environment Variables 설정

### 3.1 Settings 탭 이동
1. 프로젝트 페이지에서 **"Settings"** 탭 클릭
2. 왼쪽 사이드바에서 **"Environment Variables"** 클릭

### 3.2 환경변수 추가

#### 변수 1: BLOB_READ_WRITE_TOKEN
```
Name: BLOB_READ_WRITE_TOKEN
Value: [Blob Store에서 자동 생성된 토큰 - 아래 Step 4에서 확인]
Environment: Production, Preview, Development
```

#### 변수 2: JWT_SECRET_KEY
```
Name: JWT_SECRET_KEY
Value: mysc-ir-production-secure-jwt-secret-2025
Environment: Production, Preview, Development
```

---

## 📋 Step 4: Blob Store 연결

### 4.1 Storage 탭 이동
1. 프로젝트 페이지에서 **"Storage"** 탭 클릭
2. **"Create Database"** 또는 **"Connect Store"** 버튼 클릭

### 4.2 Blob Store 생성/연결
1. **"Blob"** 옵션 선택
2. Store Name: `mysc-production-blob`
3. Region: `Washington, D.C. (iad1)` (기본값)
4. **"Create"** 클릭

### 4.3 토큰 복사
1. 생성된 Blob Store 클릭
2. **"BLOB_READ_WRITE_TOKEN"** 값 복사
3. Step 3.2로 돌아가서 환경변수에 붙여넣기

---

## 📋 Step 5: 배포 설정 확인

### 5.1 Functions 탭 이동
1. **"Functions"** 탭 클릭
2. **Configuration 확인**:
   - Runtime: Python 3.x
   - Memory: 1024 MB
   - Max Duration: 30s

### 5.2 도메인 설정 (선택사항)
1. **"Domains"** 탭 클릭
2. 원하는 커스텀 도메인 추가 가능

---

## 📋 Step 6: 재배포 실행

### 6.1 Deployments 탭 이동
1. **"Deployments"** 탭 클릭
2. 최신 배포 찾기: `Bhqb2UB2MtYEEwqBTNjKrA6GmoAg`

### 6.2 재배포 실행
1. 최신 배포 오른쪽 **"..."** 메뉴 클릭
2. **"Redeploy"** 선택
3. **"Use existing Build Cache"** 체크 해제
4. **"Redeploy"** 버튼 클릭

---

## 📋 Step 7: 테스트 및 확인

### 7.1 배포 완료 대기
- 배포 상태가 **"Ready"**가 될 때까지 대기 (보통 1-3분)

### 7.2 기능 테스트
1. **홈페이지 접속**: https://mysc-production-k8it7vtnc-minwooks-projects-4c467b76.vercel.app
   - 401 오류 없이 MYSC IR 플랫폼 페이지 표시되어야 함

2. **Health 체크**: `/health` 엔드포인트 접속
   - JSON 응답에서 `blob_token_configured: true` 확인

3. **API 테스트**: `/api/status` 엔드포인트 접속
   - `"status": "fully_operational"` 확인

---

## 🚨 문제 해결

### 여전히 401 오류가 발생하는 경우:

#### Option A: 프로젝트 보안 설정 확인
1. **Settings → General**
2. **"Password Protection"** 비활성화 확인
3. **"Vercel Authentication"** 설정 확인

#### Option B: 새로운 배포 트리거
```bash
# 터미널에서 실행 (새로운 커밋으로 강제 재배포)
cd mysc-production
echo "# Force redeploy $(date)" >> README.md
vercel --prod --yes
```

#### Option C: 지원팀 문의
1. Vercel 대시보드에서 **"Help"** 클릭
2. **"Contact Support"** 선택
3. 401 오류 및 `mysc-production` 프로젝트 관련 문의

---

## ✅ 성공 확인 체크리스트

- [ ] Environment Variables 2개 설정 완료
- [ ] Blob Store 생성 및 연결 완료  
- [ ] 재배포 실행 완료
- [ ] 홈페이지 401 오류 해결 확인
- [ ] /health 엔드포인트 정상 응답 확인
- [ ] Blob 업로드 기능 테스트 완료

---

## 📞 추가 지원

**문제 발생 시 연락처:**
- Vercel Support: https://vercel.com/help
- 프로젝트 URL: https://vercel.com/minwooks-projects-4c467b76/mysc-production
- 배포 ID: `Bhqb2UB2MtYEEwqBTNjKrA6GmoAg`

**완료 후 확인 URL:**
- 메인 사이트: https://mysc-production-k8it7vtnc-minwooks-projects-4c467b76.vercel.app
- 헬스 체크: https://mysc-production-k8it7vtnc-minwooks-projects-4c467b76.vercel.app/health
- 상태 확인: https://mysc-production-k8it7vtnc-minwooks-projects-4c467b76.vercel.app/api/status

---

**🎉 완료 시 MYSC IR 분석 플랫폼의 모든 기능이 정상 작동합니다!**
- 50MB+ 파일 업로드 (Vercel Blob)
- AI 기반 투자분석 (Google Gemini)  
- 실시간 진행률 추적
- 엔터프라이즈급 보안 (JWT)
- 한국어 최적화 UI