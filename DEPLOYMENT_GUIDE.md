# Vercel 배포 가이드

## 환경변수 설정 (매우 중요!)

Vercel 대시보드의 프로젝트 설정에서 다음 환경변수들을 설정해야 합니다:

### 필수 환경변수

```
GEMINI_API_KEY=여기에_실제_Gemini_API_키_입력
BLOB_READ_WRITE_TOKEN=여기에_실제_Vercel_Blob_토큰_입력
JWT_SECRET_KEY=안전한_임의의_문자열_생성하여_입력
ENVIRONMENT=production
```

### 선택적 환경변수

```
MAX_FILE_SIZE=104857600
MAX_TEXT_LENGTH=15000
JSONL_DATA_PATH=./jsonl_data
```

## 배포 단계

1. **Vercel 대시보드 접속**: https://vercel.com
2. **프로젝트 생성**: 
   - "Add New Project" 클릭
   - GitHub 저장소 `ir-analyzer` 선택
3. **환경변수 설정**:
   - Settings → Environment Variables
   - 위의 환경변수들을 모두 추가
4. **배포 실행**: Deploy 버튼 클릭

## Vercel Blob 토큰 발급

1. Vercel 대시보드에서 Storage 탭으로 이동
2. "Create Database" → "Blob" 선택
3. Blob 스토리지 생성 후 API 토큰 복사
4. 환경변수 `BLOB_READ_WRITE_TOKEN`에 설정

## 주요 파일들

- `vercel.json`: Vercel 배포 설정
- `requirements.txt`: Python 의존성
- `api/index.py`: FastAPI 메인 애플리케이션
- `blob_processor.py`: Vercel Blob 통합 로직
- `.env.example`: 환경변수 예시 파일

## 배포 후 확인사항

1. 웹사이트 접속 가능 여부
2. API 엔드포인트 동작 확인
3. 파일 업로드 기능 테스트
4. Blob 스토리지 연동 확인

## 문제 해결

- **500 에러**: 환경변수 설정 확인
- **파일 업로드 실패**: BLOB_READ_WRITE_TOKEN 확인
- **API 인증 실패**: GEMINI_API_KEY 확인

## 지원 기능

✅ 투자심사보고서 자동 생성
✅ 변화이론 다이어그램 생성  
✅ Vercel Blob 파일 스토리지
✅ 다중 파일 업로드 (PDF, Excel, Word)
✅ 실시간 진행률 추적
✅ 모바일 반응형 UI