# IR Analyzer - Error Report & Solutions

## 배포 관련 에러 (2025-08-05)

### 🚨 Error 1: 500 INTERNAL_SERVER_ERROR - Module Import 실패
**발생 시점:** Vercel 서버리스 함수 첫 배포 후  
**에러 코드:** `FUNCTION_INVOCATION_FAILED`

**원인:**
- `api/index.py`에서 `pdf_processor`, `jsonl_processor` 모듈을 import하려 했으나
- 해당 파일들이 루트 디렉토리(`C:\Users\USER\Desktop\IR\`)에 있어서 서버리스 함수에서 접근 불가
- Vercel 서버리스 함수는 `api/` 폴더 내의 파일만 접근 가능

**해결책:**
```bash
# 필요한 모듈들을 api/ 폴더로 복사
cp pdf_processor.py api/pdf_processor.py
cp jsonl_processor.py api/jsonl_processor.py  
cp -r jsonl_data/ api/jsonl_data/
```

**참고 코드 위치:**
- `api/index.py:279` - `from pdf_processor import PDFProcessor`
- `api/index.py:442` - `from jsonl_processor import JSONLProcessor`

---

### 🚨 Error 2: 500 INTERNAL_SERVER_ERROR - Static Directory 없음
**발생 시점:** 모듈 import 수정 후  
**에러 메시지:** `RuntimeError: Directory '/var/task/api/public/static' does not exist`

**원인:**
- `api/index.py:47`에서 `StaticFiles`를 마운트하려 했으나 `public/static` 디렉토리가 존재하지 않음
- 서버리스 함수 시작 시 static files 마운팅에서 크래시 발생

**해결책:**
1. `public` 폴더를 `api/` 디렉토리로 복사:
```bash
cp -r public/ api/public/
```

2. Static files 마운팅에 에러 핸들링 추가:
```python
# Before (크래시 발생)
app.mount("/static", StaticFiles(directory=PUBLIC_DIR / "static"), name="static")

# After (안전한 처리)
try:
    if (PUBLIC_DIR / "static").exists():
        app.mount("/static", StaticFiles(directory=PUBLIC_DIR / "static"), name="static")
    else:
        print(f"⚠️ Static directory not found: {PUBLIC_DIR / 'static'}")
except Exception as e:
    print(f"⚠️ Failed to mount static files: {e}")
```

**참고 코드 위치:**
- `api/index.py:45-53` - Static files 마운팅 부분

---

## 학습된 패턴 & 베스트 프랙티스

### 📋 Vercel 서버리스 함수 배포 체크리스트
1. **의존성 파일 위치 확인**
   - [ ] 모든 import되는 Python 모듈이 `api/` 폴더 내에 있는가?
   - [ ] 데이터 파일들(`jsonl_data/` 등)이 `api/` 폴더 내에 있는가?

2. **정적 파일 처리**
   - [ ] `public/` 폴더가 `api/public/`로 복사되었는가?
   - [ ] Static files 마운팅에 에러 핸들링이 있는가?

3. **환경 변수 & 설정**
   - [ ] 필요한 환경변수들이 Vercel에 설정되었는가?
   - [ ] `requirements.txt`에 모든 의존성이 명시되었는가?

### 🔧 디버깅 팁
1. **Vercel 로그 확인 방법:**
   ```bash
   vercel logs  # 로그인 필요: vercel login
   ```

2. **로컬 테스트:**
   ```bash
   cd api/
   python index.py  # 로컬에서 FastAPI 서버 실행
   ```

3. **파일 구조 검증:**
   ```bash
   tree api/  # api/ 폴더 구조 확인
   ```

### ⚠️ 주의사항
- Vercel 서버리스 함수는 **`api/` 폴더 기준**으로 파일 접근
- 루트 디렉토리의 파일들은 서버리스 환경에서 접근 불가
- Static files 마운팅은 **반드시 try-catch로 감싸기**
- 환경변수 없을 때 기본값 설정하기

---

## 해결된 에러 요약
| 에러 | 원인 | 해결 | 커밋 |
|------|------|------|------|
| FUNCTION_INVOCATION_FAILED | 모듈 import 실패 | 파일을 api/로 이동 | `200738c` |
| Static Directory 없음 | public/ 폴더 누락 | public/ 복사 + 에러핸들링 | `911279b` |

## 다음 배포 시 참고사항
- 새로운 Python 모듈 추가 시 반드시 `api/` 폴더에 배치
- 정적 자원 추가 시 `api/public/` 구조 유지
- 배포 전 로컬에서 `api/` 폴더 기준으로 테스트 실행