/**
 * App.js Integration with Vercel Blob Upload System
 * 
 * This file contains the integration code that should be added to the existing app.js
 * to enable Vercel Blob uploads with seamless Korean UX
 */

// Add these functions to your existing app.js

/**
 * Enhanced file upload initialization with Blob support
 */
function initBlobFileUpload() {
    // Check if blob uploader is available
    if (!window.blobUploader) {
        console.error('❌ Vercel Blob Uploader not available');
        return;
    }

    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const fileValidation = document.getElementById('fileValidation');

    if (!uploadArea || !fileInput) {
        console.error('❌ Upload elements not found');
        return;
    }

    // Enhanced drag and drop handlers
    uploadArea.addEventListener('click', () => fileInput.click());
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        
        const files = Array.from(e.dataTransfer.files);
        handleBlobFileSelection(files);
    });

    fileInput.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        handleBlobFileSelection(files);
    });
}

/**
 * Handle file selection with Blob validation
 */
function handleBlobFileSelection(files) {
    const companyName = document.getElementById('companyName')?.value || '';
    
    // Clear previous validation
    clearFileValidation();
    
    if (files.length === 0) {
        updateFileValidation('파일을 선택해주세요.', 'error');
        return;
    }

    // Validate files using Blob uploader
    let allValid = true;
    let totalSize = 0;
    const validationResults = [];

    files.forEach(file => {
        const validation = window.blobUploader.validateFile(file, companyName);
        totalSize += file.size;
        
        if (!validation.valid) {
            allValid = false;
            validationResults.push({
                filename: file.name,
                errors: validation.errors
            });
        }
    });

    // Update UI with validation results
    if (allValid) {
        updateFileValidation(
            `${files.length}개 파일 선택됨 (총 ${window.blobUploader.formatFileSize(totalSize)})`, 
            'success'
        );
        currentFiles = files; // Update global state
        updateUploadButton(true);
    } else {
        const errorMessage = validationResults
            .map(r => `${r.filename}: ${r.errors.join(', ')}`)
            .join('\n');
        updateFileValidation(errorMessage, 'error');
        updateUploadButton(false);
    }
}

/**
 * Enhanced form submission with Blob upload
 */
function handleBlobFormSubmission(e) {
    e.preventDefault();
    
    if (analysisInProgress) {
        showNotification('분석이 이미 진행 중입니다.', 'warning');
        return;
    }

    const companyName = document.getElementById('companyName')?.value?.trim();
    const activeTab = document.querySelector('.tab-button.active')?.dataset.tab;

    if (!companyName) {
        showNotification('회사명을 입력해주세요.', 'error');
        return;
    }

    if (activeTab === 'file') {
        if (currentFiles.length === 0) {
            showNotification('업로드할 파일을 선택해주세요.', 'error');
            return;
        }
        startBlobAnalysis(companyName, currentFiles);
    } else if (activeTab === 'url') {
        const irUrl = document.getElementById('irUrl')?.value?.trim();
        if (!irUrl) {
            showNotification('IR 자료 URL을 입력해주세요.', 'error');
            return;
        }
        startUrlAnalysis(companyName, irUrl);
    }
}

/**
 * Start analysis with Blob upload
 */
async function startBlobAnalysis(companyName, files) {
    try {
        analysisInProgress = true;
        showProgressContainer();
        updateAnalysisProgress(0, 'Vercel Blob에 파일을 업로드하는 중...');
        updateUploadButton(false, '업로드 중...');

        // Show debug log container
        const debugContainer = document.getElementById('debugLogContainer');
        if (debugContainer) {
            debugContainer.style.display = 'block';
            addDebugLog('🚀 Vercel Blob 업로드 시작', 'info');
        }

        // Upload files using Blob uploader
        const uploadResults = await window.blobUploader.uploadFiles(files, companyName, (progressInfo) => {
            // Update progress for individual files
            if (progressInfo.fileIndex !== undefined) {
                const overallProgress = Math.round((progressInfo.fileIndex * 100 + progressInfo.progress) / files.length);
                updateAnalysisProgress(overallProgress, 
                    `${progressInfo.filename} 업로드 중... ${Math.round(progressInfo.progress)}%`);
                
                addDebugLog(`📁 ${progressInfo.filename}: ${Math.round(progressInfo.progress)}% 완료`, 'info');
            }
        });

        addDebugLog('✅ 모든 파일 업로드 완료', 'success');
        updateAnalysisProgress(100, '업로드 완료, IR 분석 시작 중...');

        // Simulate IR analysis (replace with actual analysis call)
        await simulateIRAnalysis(companyName, uploadResults);

        // Show success
        showSuccessNotification('IR 분석이 완료되었습니다!');
        showResultsContainer();

    } catch (error) {
        console.error('❌ Blob 업로드 분석 실패:', error);
        addDebugLog(`❌ 오류: ${error.message}`, 'error');
        showNotification(`업로드 실패: ${error.message}`, 'error');
    } finally {
        analysisInProgress = false;
        updateUploadButton(true);
        hideProgressContainer();
    }
}

/**
 * Simulate IR analysis process
 */
async function simulateIRAnalysis(companyName, uploadResults) {
    const steps = [
        '파일 내용 추출 중...',
        'AI 모델로 데이터 분석 중...',
        '투자심사보고서 생성 중...',
        '최종 검토 및 완료...'
    ];

    for (let i = 0; i < steps.length; i++) {
        updateAnalysisProgress(25 + (i * 18.75), steps[i]);
        addDebugLog(`🔄 ${steps[i]}`, 'info');
        await new Promise(resolve => setTimeout(resolve, 1500 + Math.random() * 1000));
    }

    updateAnalysisProgress(100, '분석 완료!');
    addDebugLog('🎉 IR 분석이 성공적으로 완료되었습니다', 'success');

    // Update results with mock data
    updateAnalysisResults(companyName, uploadResults);
}

/**
 * Update analysis results display
 */
function updateAnalysisResults(companyName, uploadResults) {
    // Update executive summary
    const executiveSummary = document.getElementById('executiveSummary');
    if (executiveSummary) {
        executiveSummary.innerHTML = `
            <div class="analysis-summary">
                <h4>${companyName} 투자심사보고서</h4>
                <p class="summary-highlight">
                    🚀 Vercel Blob을 통해 ${uploadResults.length}개 파일이 성공적으로 분석되었습니다.
                    AI 기반 분석 결과, 이 회사는 높은 성장 잠재력을 보여줍니다.
                </p>
                <div class="summary-metrics">
                    <div class="metric">
                        <span class="metric-label">분석 파일 수</span>
                        <span class="metric-value">${uploadResults.length}개</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">업로드 방식</span>
                        <span class="metric-value">Vercel Blob Direct</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">분석 정확도</span>
                        <span class="metric-value">98.5%</span>
                    </div>
                </div>
            </div>
        `;
    }

    // Update investment report
    const investmentReport = document.getElementById('investmentReport');
    if (investmentReport) {
        investmentReport.innerHTML = `
            <div class="report-section">
                <h5>투자 추천</h5>
                <div class="recommendation-badge positive">강력 추천</div>
                <p>AI 분석 결과, ${companyName}은 다음과 같은 강점을 보입니다:</p>
                <ul>
                    <li>안정적인 재무구조와 지속적인 성장세</li>
                    <li>혁신적인 비즈니스 모델과 시장 경쟁력</li>
                    <li>우수한 경영진과 명확한 사업 전략</li>
                </ul>
                <div class="tech-note">
                    <strong>기술 혁신:</strong> Vercel Blob 직접 업로드를 통해 50MB+ 대용량 파일도 
                    신속하고 안전하게 처리할 수 있습니다.
                </div>
            </div>
        `;
    }

    // Update recommendations
    const recommendationsReport = document.getElementById('recommendationsReport');
    if (recommendationsReport) {
        recommendationsReport.innerHTML = `
            <div class="report-section">
                <h5>핵심 권고사항</h5>
                <div class="recommendation-list">
                    <div class="recommendation-item">
                        <strong>즉시 실행:</strong> ${companyName}의 지분 확보를 적극 추진하십시오.
                    </div>
                    <div class="recommendation-item">
                        <strong>리스크 관리:</strong> 시장 변동성에 대한 모니터링을 강화하십시오.
                    </div>
                    <div class="recommendation-item">
                        <strong>장기 전략:</strong> ESG 요소를 고려한 지속가능한 투자 계획을 수립하십시오.
                    </div>
                </div>
            </div>
        `;
    }
}

/**
 * Enhanced progress update with Blob-specific features
 */
function updateAnalysisProgress(percentage, message) {
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    
    if (progressFill) {
        progressFill.style.width = `${percentage}%`;
    }
    
    if (progressText) {
        progressText.textContent = message;
    }

    // Update step indicators
    const steps = ['step1', 'step2', 'step3', 'step4'];
    const currentStep = Math.floor((percentage / 100) * steps.length);
    
    steps.forEach((stepId, index) => {
        const stepElement = document.getElementById(stepId);
        if (stepElement) {
            if (index < currentStep) {
                stepElement.classList.add('completed');
                stepElement.classList.remove('active');
            } else if (index === currentStep) {
                stepElement.classList.add('active');
                stepElement.classList.remove('completed');
            } else {
                stepElement.classList.remove('active', 'completed');
            }
        }
    });
}

/**
 * Debug log management
 */
function addDebugLog(message, type = 'info') {
    const debugLogContent = document.getElementById('debugLogContent');
    if (!debugLogContent) return;

    const timestamp = new Date().toLocaleTimeString('ko-KR');
    const logEntry = document.createElement('div');
    logEntry.className = `debug-log-entry ${type}`;
    
    const icon = type === 'success' ? '✅' : 
                type === 'error' ? '❌' : 
                type === 'warning' ? '⚠️' : '🔄';
    
    logEntry.innerHTML = `
        <span class="log-timestamp">${timestamp}</span>
        <span class="log-icon">${icon}</span>
        <span class="log-message">${message}</span>
    `;

    debugLogContent.appendChild(logEntry);
    debugLogContent.scrollTop = debugLogContent.scrollHeight;
}

/**
 * Utility functions for UI updates
 */
function updateUploadButton(enabled, text = '투자심사보고서 생성하기') {
    const analyzeBtn = document.getElementById('analyzeBtn');
    if (analyzeBtn) {
        analyzeBtn.disabled = !enabled;
        analyzeBtn.innerHTML = enabled ? 
            `<i data-lucide="sparkles" style="width: 20px; height: 20px; margin-right: 8px;"></i>${text}` :
            `<i data-lucide="loader" class="spinning" style="width: 20px; height: 20px; margin-right: 8px;"></i>${text}`;
        
        // Re-initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
}

function updateFileValidation(message, type) {
    const fileValidation = document.getElementById('fileValidation');
    if (!fileValidation) return;

    fileValidation.innerHTML = `
        <div class="validation-message ${type}">
            <i data-lucide="${type === 'success' ? 'check-circle' : 'alert-circle'}" 
               style="width: 16px; height: 16px; margin-right: 8px;"></i>
            <span>${message}</span>
        </div>
    `;

    // Re-initialize Lucide icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

function clearFileValidation() {
    const fileValidation = document.getElementById('fileValidation');
    if (fileValidation) {
        fileValidation.innerHTML = `
            <div id="formatValidation" class="validation-item">
                <i data-lucide="file-check" style="width: 16px; height: 16px;"></i>
                <span>파일 형식 확인</span>
            </div>
            <div id="sizeValidation" class="validation-item">
                <i data-lucide="hard-drive" style="width: 16px; height: 16px;"></i>
                <span>파일 크기 확인</span>
            </div>
        `;
        
        // Re-initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
}

function showProgressContainer() {
    const progressContainer = document.getElementById('progressContainer');
    if (progressContainer) {
        progressContainer.style.display = 'block';
        progressContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function hideProgressContainer() {
    const progressContainer = document.getElementById('progressContainer');
    if (progressContainer) {
        progressContainer.style.display = 'none';
    }
}

function showResultsContainer() {
    const resultsContainer = document.getElementById('resultsContainer');
    if (resultsContainer) {
        resultsContainer.style.display = 'block';
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i data-lucide="${type === 'success' ? 'check-circle' : 
                              type === 'error' ? 'x-circle' : 
                              type === 'warning' ? 'alert-circle' : 'info'}" 
               style="width: 20px; height: 20px; margin-right: 12px;"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close">
            <i data-lucide="x" style="width: 16px; height: 16px;"></i>
        </button>
    `;

    // Add to page
    document.body.appendChild(notification);

    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);

    // Manual close
    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.remove();
    });

    // Re-initialize Lucide icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
}

function showSuccessNotification(message) {
    showNotification(message, 'success');
}

// Export functions for integration
window.BlobIntegration = {
    initBlobFileUpload,
    handleBlobFileSelection,
    handleBlobFormSubmission,
    startBlobAnalysis,
    updateAnalysisProgress,
    addDebugLog,
    updateUploadButton,
    showNotification,
    showSuccessNotification
};