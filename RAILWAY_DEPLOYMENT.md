# 🚄 Railway 배포 가이드

## 🎯 Railway 장점
- ✅ **무제한 실행 시간** (서버리스 제약 완전 제거)
- ✅ **100MB 파일 처리** 가능
- ✅ **2GB RAM**, 더 강력한 성능
- ✅ **무료 플랜** 월 5달러 크레딧
- ✅ **실시간 로그** 모니터링

## 🚀 5분 완성 배포

### 1단계: Railway 계정 생성
1. https://railway.app 접속
2. "Login with GitHub" 클릭
3. GitHub 계정 연동

### 2단계: 프로젝트 배포
1. "New Project" 클릭
2. "Deploy from GitHub repo" 선택
3. `ir-analyzer` 저장소 선택
4. 자동으로 Python/FastAPI 감지

### 3단계: 환경 변수 설정 (필수!)
**Settings → Variables**에서 다음 설정:

```bash
# 필수 환경 변수
GEMINI_API_KEY=여기에_실제_API_키_입력
JWT_SECRET=mysc-railway-secret-2025
ENVIRONMENT=production

# 파일 처리 한도 (Railway는 100MB까지 가능!)
MAX_FILE_SIZE=104857600
MAX_TEXT_LENGTH=100000
PORT=8000
```

### 4단계: 배포 완료!
- 자동으로 빌드 시작
- 약 2-3분 후 배포 완료
- Railway에서 제공하는 URL 확인

## 💡 Railway vs Vercel 비교

| 기능 | Vercel (서버리스) | Railway (컨테이너) |
|------|-------------------|-------------------|
| 실행 시간 | 15초 제한 | **무제한** ✅ |
| 파일 크기 | 4.5MB 제한 | **100MB+** ✅ |
| 메모리 | 1GB | **2GB** ✅ |
| 동시 처리 | 제한적 | **워커 2개** ✅ |
| 비용 | $20/월 | **$5 크레딧/월** ✅ |

## 🔧 고급 설정

### railway.json 최적화
```json
{
  "deploy": {
    "startCommand": "uvicorn api.index:app --host 0.0.0.0 --port $PORT --workers 2",
    "healthcheckTimeout": 300
  }
}
```

### 커스텀 도메인 (선택)
- Railway Pro 플랜에서 커스텀 도메인 연결 가능
- 예: `ir-analyzer.yourdomain.com`

## 📊 성능 향상

### 1. 멀티워커 활용
```python
# Procfile
web: uvicorn api.index:app --host 0.0.0.0 --port $PORT --workers 2
```

### 2. 메모리 최적화
- Railway 2GB RAM 활용
- 대용량 파일 동시 처리

### 3. 로그 모니터링
- Railway 대시보드에서 실시간 로그 확인
- 성능 메트릭 추적

## ✨ 즉시 실행 명령어

```bash
# 로컬 테스트
uvicorn api.index:app --host 0.0.0.0 --port 8000

# Railway 자동 배포
git push origin main
```

## 🎉 완료!

배포 후 다음 기능들이 **무제한 시간**으로 실행됩니다:
- ✅ 10MB+ PDF 분석
- ✅ 1-2분 VC급 분석  
- ✅ 다중 파일 동시 처리
- ✅ 실시간 진행률 추적

**Railway URL이 생성되면 이것이 새로운 메인 서비스가 됩니다!**