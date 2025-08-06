# Vercel 환경 변수 수동 설정 가이드

## 🎯 목표
401 권한 오류 해결을 위한 Vercel 환경 변수 설정

## 📋 설정 단계

### 1단계: Vercel 대시보드 접속
1. https://vercel.com 로그인
2. `ir-analyzer` 프로젝트 선택
3. **Settings** → **Environment Variables**

### 2단계: 환경 변수 추가

| 변수명 | 값 | 환경 | 설명 |
|--------|-----|------|------|
| `BLOB_READ_WRITE_TOKEN` | `vercel_blob_rw_...` | All | Blob 저장소 토큰 |
| `VERCEL_ENV` | `production` | Production | 운영 환경 설정 |
| `NODE_ENV` | `production` | Production | Node.js 환경 |
| `ALLOWED_ORIGINS` | `*` | All | CORS 허용 도메인 |
| `PLATFORM_NAME` | `MYSC IR Platform` | All | 플랫폼 이름 |
| `MAX_FILE_SIZE` | `52428800` | All | 최대 파일 크기 (50MB) |

### 3단계: Blob 토큰 생성

**CLI 방법:**
```bash
vercel login
vercel blob create-token --scope read,write
```

**대시보드 방법:**
1. Storage → Blob → Create Token
2. Read/Write 권한 선택
3. 토큰 복사하여 `BLOB_READ_WRITE_TOKEN`에 입력

### 4단계: 재배포
```bash
vercel --prod --yes
```

## 🔍 문제 해결

### 401 오류가 지속되는 경우:
1. **도메인 설정 확인**
   - Settings → Domains에서 커스텀 도메인 설정 확인

2. **프로젝트 권한 확인**
   - Settings → General → Project Settings
   - Public/Private 설정 확인

3. **팀 설정 확인**
   - Pro 플랜이 필요한 기능인지 확인
   - 팀 멤버 권한 설정 확인

### 대안 해결책:
1. **새 프로젝트 생성**
   ```bash
   vercel --name mysc-ir-platform-fresh
   ```

2. **Pro 플랜 업그레이드**
   ```bash
   vercel billing upgrade
   ```

## ⚠️ 주의사항
- 모든 환경 변수는 **모든 환경**에 적용해야 함
- 토큰은 절대 GitHub에 커밋하지 말 것
- 설정 후 반드시 재배포 필요

## 🎯 기대 결과
- 401 오류 해결
- Linear 스타일 MYSC IR Platform 정상 작동
- 50MB 파일 업로드 기능 활성화