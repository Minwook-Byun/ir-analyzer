# 🗑️ Vercel 프로젝트 정리 가이드
## 불필요한 테스트 프로젝트 삭제

### 🎯 목표
- 테스트 프로젝트들을 모두 삭제하여 계정 정리
- 핵심 프로젝트만 유지하여 관리 효율성 향상

---

## 📋 삭제 대상 프로젝트 목록

**확인된 테스트/불필요 프로젝트들:**
- `mysc-fresh` - 테스트용 최소 구현
- `ai-agent-mysc` - 401 오류 발생 프로젝트  
- `ir-analyzer-pro` - 중복 프로젝트
- `ir-analyzer-app` - 중복 프로젝트
- `isr-blog-nextjs-wordpress` - 관련 없는 프로젝트
- `nextjs-ai-chatbot` - 관련 없는 프로젝트

**유지할 핵심 프로젝트:**
- `ir-analyzer` - 메인 MYSC IR 플랫폼 (현재 작동 중)

---

## 📋 Step 1: Vercel 대시보드 접속

1. **브라우저에서 접속**: https://vercel.com/dashboard
2. **팀 선택**: `minwooks-projects-4c467b76`
3. **프로젝트 목록 확인**

---

## 📋 Step 2: 각 프로젝트 삭제

### 2.1 mysc-fresh 삭제
1. **프로젝트 클릭**: `mysc-fresh`
2. **Settings 탭** → **Advanced** 섹션
3. **Delete Project** 클릭
4. **프로젝트명 입력**: `mysc-fresh`
5. **Delete** 버튼 클릭

### 2.2 ai-agent-mysc 삭제
1. **프로젝트 클릭**: `ai-agent-mysc`
2. **Settings 탭** → **Advanced** 섹션
3. **Delete Project** 클릭
4. **프로젝트명 입력**: `ai-agent-mysc`
5. **Delete** 버튼 클릭

### 2.3 ir-analyzer-pro 삭제
1. **프로젝트 클릭**: `ir-analyzer-pro`
2. **Settings 탭** → **Advanced** 섹션
3. **Delete Project** 클릭
4. **프로젝트명 입력**: `ir-analyzer-pro`
5. **Delete** 버튼 클릭

### 2.4 ir-analyzer-app 삭제
1. **프로젝트 클릭**: `ir-analyzer-app`
2. **Settings 탭** → **Advanced** 섹션
3. **Delete Project** 클릭
4. **프로젝트명 입력**: `ir-analyzer-app`
5. **Delete** 버튼 클릭

### 2.5 isr-blog-nextjs-wordpress 삭제
1. **프로젝트 클릭**: `isr-blog-nextjs-wordpress`
2. **Settings 탭** → **Advanced** 섹션
3. **Delete Project** 클릭
4. **프로젝트명 입력**: `isr-blog-nextjs-wordpress`
5. **Delete** 버튼 클릭

### 2.6 nextjs-ai-chatbot 삭제
1. **프로젝트 클릭**: `nextjs-ai-chatbot`
2. **Settings 탭** → **Advanced** 섹션
3. **Delete Project** 클릭
4. **프로젝트명 입력**: `nextjs-ai-chatbot`
5. **Delete** 버튼 클릭

---

## 📋 Step 3: Blob Store 정리

### 3.1 사용하지 않는 Blob Store 삭제
1. **각 삭제된 프로젝트의 Blob Store들**:
   - `mysc-ir-fresh` (mysc-fresh 프로젝트)
   - `mysc-ir-platform` (ai-agent-mysc 프로젝트)
   
2. **Storage 대시보드**에서 연결되지 않은 Store 삭제
3. **비용 절약**을 위한 정리

---

## 📋 Step 4: Domain/Alias 정리

### 4.1 불필요한 Alias 삭제
**현재 Alias 상태:**
```
mysc-fresh.vercel.app → 삭제 예정
ir-analyzer-50mb-test.vercel.app → 삭제 예정
ir-analyzer-pro.vercel.app → 삭제 예정
ir-analyzer-app.vercel.app → 삭제 예정
```

**유지할 Alias:**
```
ir-analyzer-zwao.vercel.app → 메인 사이트 (유지)
```

### 4.2 Alias 정리 방법
1. **Vercel 대시보드** → **Domains** 섹션
2. **불필요한 도메인들 삭제**
3. **메인 도메인만 유지**

---

## ⚠️ 주의사항

### 삭제 전 확인사항
- [ ] **데이터 백업**: 중요한 데이터가 있는지 확인
- [ ] **도메인 의존성**: 외부에서 참조하는 URL이 있는지 확인
- [ ] **Environment Variables**: 중요한 설정이 있는지 확인

### 삭제할 수 없는 경우
1. **Dependencies 확인**: 다른 서비스에서 사용 중인지 확인
2. **Payment Issues**: 결제 관련 문제가 있는지 확인
3. **Team Permissions**: 삭제 권한이 있는지 확인

---

## 📋 Step 5: 최종 확인

### 5.1 정리 완료 후 상태
**남은 프로젝트:**
- `ir-analyzer` (메인 MYSC IR 플랫폼)

**남은 도메인:**
- `ir-analyzer-zwao.vercel.app` (작동 중인 메인 사이트)

**남은 Blob Store:**
- 메인 프로젝트 연결된 Store만 유지

### 5.2 성공 확인
1. **대시보드에서 프로젝트 목록 확인**
2. **불필요한 프로젝트들이 모두 삭제되었는지 확인**
3. **메인 사이트 정상 작동 확인**

---

## 🎉 정리 완료 후 혜택

1. **계정 관리 효율성 향상**
   - 단순화된 프로젝트 목록
   - 명확한 책임 구조

2. **비용 절약**
   - 불필요한 Blob Storage 비용 절약
   - 사용하지 않는 도메인 비용 절약

3. **보안 향상**
   - 공격 표면 축소
   - 관리 포인트 감소

4. **개발 효율성**
   - 혼동 요소 제거
   - 집중할 프로젝트 명확화

---

## 🔧 CLI를 통한 삭제 (고급 사용자)

**Vercel CLI 로그인 후:**
```bash
# 프로젝트 목록 확인
vercel projects ls

# 개별 프로젝트 삭제 (조심스럽게 사용)
vercel projects rm mysc-fresh
vercel projects rm ai-agent-mysc
vercel projects rm ir-analyzer-pro
vercel projects rm ir-analyzer-app
vercel projects rm isr-blog-nextjs-wordpress
vercel projects rm nextjs-ai-chatbot
```

**⚠️ 주의**: CLI 삭제는 되돌릴 수 없으므로 대시보드 사용 권장

---

**완료 후**: 깔끔하게 정리된 Vercel 계정에서 `ir-analyzer` 프로젝트에만 집중하여 MYSC IR 플랫폼을 완성할 수 있습니다.