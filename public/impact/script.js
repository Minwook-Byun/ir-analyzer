// Impact Story Builder - JavaScript
// 완전 독립적인 클라이언트 사이드 로직

class ImpactStoryBuilder {
    constructor() {
        this.currentStep = 1;
        this.maxSteps = 5;
        this.storyData = {
            problem: '',
            target: '',
            solution: '',
            change: '',
            measurement: '',
            timeframe: ''
        };
        
        this.init();
    }
    
    init() {
        // 초기 미리보기 업데이트
        this.updateLivePreview();
        
        // 키보드 이벤트 리스너
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                this.nextStep();
            }
        });
    }
    
    nextStep() {
        const currentCard = document.querySelector(`[data-step="${this.currentStep}"]`);
        const currentInput = currentCard.querySelector('textarea, input');
        
        // 현재 입력값 검증
        if (!this.validateCurrentStep()) {
            this.showValidationError(currentInput);
            return;
        }
        
        // 다음 단계로 이동
        if (this.currentStep < this.maxSteps) {
            this.hideCard(this.currentStep);
            this.currentStep++;
            this.showCard(this.currentStep);
            this.updateProgress();
            
            // 다음 입력 필드에 포커스
            setTimeout(() => {
                const nextCard = document.querySelector(`[data-step="${this.currentStep}"]`);
                const nextInput = nextCard.querySelector('textarea, input');
                if (nextInput) nextInput.focus();
            }, 300);
        }
    }
    
    prevStep() {
        if (this.currentStep > 1) {
            this.hideCard(this.currentStep);
            this.currentStep--;
            this.showCard(this.currentStep);
            this.updateProgress();
        }
    }
    
    showCard(step) {
        const card = document.querySelector(`[data-step="${step}"]`);
        card.style.display = 'block';
        setTimeout(() => {
            card.classList.add('active');
        }, 50);
    }
    
    hideCard(step) {
        const card = document.querySelector(`[data-step="${step}"]`);
        card.classList.remove('active');
        setTimeout(() => {
            card.style.display = 'none';
        }, 300);
    }
    
    updateProgress() {
        const progressFill = document.getElementById('progressFill');
        const currentStepSpan = document.getElementById('currentStep');
        
        const progressPercent = (this.currentStep / this.maxSteps) * 100;
        progressFill.style.width = `${progressPercent}%`;
        currentStepSpan.textContent = this.currentStep;
    }
    
    validateCurrentStep() {
        const currentCard = document.querySelector(`[data-step="${this.currentStep}"]`);
        const textarea = currentCard.querySelector('textarea');
        const input = currentCard.querySelector('input');
        
        if (textarea && textarea.value.trim().length < 5) {
            return false;
        }
        
        if (input && this.currentStep === 5 && input.value.trim().length === 0) {
            // 5단계의 timeframe은 선택사항이므로 검증하지 않음
        }
        
        return true;
    }
    
    showValidationError(input) {
        input.style.borderColor = '#ff4757';
        input.placeholder = '최소 5글자 이상 입력해주세요';
        
        setTimeout(() => {
            input.style.borderColor = '#e0e6ed';
        }, 2000);
    }
    
    updateLivePreview() {
        // 현재 입력값들 수집
        this.storyData = {
            problem: document.getElementById('problem')?.value || '___',
            target: document.getElementById('target')?.value || '___',
            solution: document.getElementById('solution')?.value || '___',
            change: document.getElementById('change')?.value || '___',
            measurement: document.getElementById('measurement')?.value || '___',
            timeframe: document.getElementById('timeframe')?.value || '___'
        };
        
        // 미리보기 업데이트 (즉시 처리, API 호출 없음)
        const preview = document.getElementById('storyPreview');
        const template = `우리는 <mark class="problem-mark">${this.storyData.problem}</mark>을 <mark class="solution-mark">${this.storyData.solution}</mark>으로 해결해서 <mark class="target-mark">${this.storyData.target}</mark>의 <mark class="change-mark">${this.storyData.change}</mark>을 <mark class="change-mark">${this.storyData.timeframe}</mark> 안에 달성하고 싶습니다.`;
        
        preview.innerHTML = template;
        
        // 부드러운 업데이트 애니메이션
        preview.classList.add('updating');
        setTimeout(() => {
            preview.classList.remove('updating');
        }, 300);
    }
    
    async generateStory() {
        // 로딩 상태 표시
        this.showLoading();
        
        try {
            // 토큰 확인
            const token = this.getToken();
            if (!token) {
                throw new Error('로그인이 필요합니다. 메인 페이지에서 로그인해주세요.');
            }
            
            // API 호출
            const response = await fetch('/api/impact-story/build', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    problem: this.storyData.problem,
                    target: this.storyData.target,
                    solution: this.storyData.solution,
                    change: this.storyData.change,
                    measurement: this.storyData.measurement,
                    timeframe: this.storyData.timeframe
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || '스토리 생성에 실패했습니다.');
            }
            
            const result = await response.json();
            this.hideLoading();
            this.showResult(result.story);
            
        } catch (error) {
            console.error('Story generation error:', error);
            this.hideLoading();
            this.showError(error.message);
        }
    }
    
    showLoading() {
        document.getElementById('loadingContainer').style.display = 'block';
        // 현재 카드 숨기기
        const currentCard = document.querySelector(`[data-step="${this.currentStep}"]`);
        currentCard.style.display = 'none';
    }
    
    hideLoading() {
        document.getElementById('loadingContainer').style.display = 'none';
    }
    
    showResult(storyData) {
        const resultContainer = document.getElementById('resultContainer');
        
        const resultHTML = `
            <div class="final-story">
                <h2>🎉 임팩트 스토리가 완성되었어요!</h2>
                
                <div class="impact-headline">
                    <h3>${storyData.headline}</h3>
                </div>
                
                <div class="key-metrics">
                    ${storyData.key_metrics.map(metric => `
                        <div class="metric">
                            <span class="metric-icon">${metric.icon}</span>
                            <span class="metric-value">${metric.value}</span>
                            <span class="metric-label">${metric.label}</span>
                        </div>
                    `).join('')}
                </div>
                
                <div class="story-details">
                    <div class="detail-section">
                        <h4>📋 문제 맥락</h4>
                        <p>${storyData.problem_context.current_situation}</p>
                    </div>
                    
                    <div class="detail-section">
                        <h4>💡 솔루션 접근법</h4>
                        <p>${storyData.solution_approach.approach_summary}</p>
                    </div>
                    
                    <div class="detail-section">
                        <h4>🎯 기대 임팩트</h4>
                        <p>${storyData.expected_impact.beneficiary_change}</p>
                    </div>
                    
                    <div class="detail-section">
                        <h4>📊 측정 계획</h4>
                        <p>${storyData.measurement_plan.success_criteria}</p>
                    </div>
                </div>
                
                <div class="story-actions">
                    <button class="primary" onclick="downloadPDF()">
                        📄 PDF 다운로드
                    </button>
                    <button class="secondary" onclick="copyToClipboard()">
                        📋 텍스트 복사
                    </button>
                    <button class="tertiary" onclick="startOver()">
                        🔄 다시 만들기
                    </button>
                </div>
            </div>
            
            ${storyData.suggestions && storyData.suggestions.length > 0 ? `
                <div class="suggestions">
                    <h4>💡 개선 제안</h4>
                    <ul>
                        ${storyData.suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        `;
        
        resultContainer.innerHTML = resultHTML;
        resultContainer.style.display = 'block';
        
        // 부드러운 스크롤
        resultContainer.scrollIntoView({ behavior: 'smooth' });
    }
    
    showError(message) {
        const errorHTML = `
            <div class="error-message">
                <h3>❌ 오류가 발생했습니다</h3>
                <p>${message}</p>
                <button onclick="location.reload()" class="retry-btn">다시 시도</button>
            </div>
        `;
        
        document.getElementById('resultContainer').innerHTML = errorHTML;
        document.getElementById('resultContainer').style.display = 'block';
    }
    
    getToken() {
        // 로컬 스토리지에서 토큰 가져오기 (메인 페이지에서 설정)
        return localStorage.getItem('access_token');
    }
}

// 전역 함수들
function nextStep() {
    window.storyBuilder.nextStep();
}

function prevStep() {
    window.storyBuilder.prevStep();
}

function updateLivePreview() {
    window.storyBuilder.updateLivePreview();
}

function generateStory() {
    window.storyBuilder.generateStory();
}

function downloadPDF() {
    // PDF 다운로드 기능 (추후 구현)
    alert('PDF 다운로드 기능은 준비 중입니다!');
}

function copyToClipboard() {
    const headline = document.querySelector('.impact-headline h3').textContent;
    navigator.clipboard.writeText(headline).then(() => {
        alert('스토리가 클립보드에 복사되었습니다!');
    });
}

function startOver() {
    location.reload();
}

// 초기화
document.addEventListener('DOMContentLoaded', () => {
    window.storyBuilder = new ImpactStoryBuilder();
    
    // 토큰 확인
    const token = localStorage.getItem('access_token');
    if (!token) {
        document.body.innerHTML = `
            <div style="text-align: center; padding: 100px 20px; color: white;">
                <h2>🔐 로그인이 필요합니다</h2>
                <p>임팩트 스토리를 생성하려면 먼저 로그인해주세요.</p>
                <button onclick="location.href='/'" style="padding: 12px 24px; margin-top: 20px; background: white; color: #667eea; border: none; border-radius: 8px; cursor: pointer;">
                    메인 페이지로 이동
                </button>
            </div>
        `;
    }
});