// MYSC IR Platform - Main Application JavaScript

class MYSCPlatform {
    constructor() {
        this.currentSection = 'analysis';
        this.selectedFiles = [];
        this.analysisInProgress = false;
        this.currentConversationId = null;
        this.currentCompanyName = null;
        
        // 토큰 확인 및 인증 검증
        this.checkAuthentication();
        this.init();
    }

    init() {
        this.setupThemeToggle();
        this.setupNavigation();
        this.setupFileUpload();
        this.setupFormSubmission();
        this.setupTabNavigation();
        this.setupExportButtons();
        this.setupLogout();
    }

    // 인증 확인
    checkAuthentication() {
        const token = localStorage.getItem('auth_token');
        if (!token) {
            window.location.href = '/login';
            return false;
        }
        
        // 토큰 만료 확인
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            const exp = new Date(payload.exp * 1000);
            if (exp < new Date()) {
                localStorage.removeItem('auth_token');
                window.location.href = '/login';
                return false;
            }
        } catch (e) {
            localStorage.removeItem('auth_token');
            window.location.href = '/login';
            return false;
        }
        
        return true;
    }

    // Theme Management
    setupThemeToggle() {
        const toggle = document.getElementById('themeToggle');
        const html = document.documentElement;
        
        // Check for saved theme preference or default to 'light'
        const currentTheme = localStorage.getItem('theme') || 'light';
        html.setAttribute('data-theme', currentTheme);
        this.updateThemeIcon(currentTheme);
        
        toggle.addEventListener('click', () => {
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            this.updateThemeIcon(newTheme);
        });
    }

    updateThemeIcon(theme) {
        const toggle = document.getElementById('themeToggle');
        const icon = toggle.querySelector('svg');
        
        if (theme === 'dark') {
            icon.setAttribute('data-feather', 'sun');
        } else {
            icon.setAttribute('data-feather', 'moon');
        }
        
        feather.replace();
    }

    // Navigation
    setupNavigation() {
        const navItems = document.querySelectorAll('.nav-item');
        
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const section = item.getAttribute('href').substring(1);
                this.switchSection(section);
            });
        });
    }

    switchSection(section) {
        // Update nav active state
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('href') === `#${section}`) {
                item.classList.add('active');
            }
        });
        
        // Update section visibility
        document.querySelectorAll('.section').forEach(sect => {
            sect.style.display = 'none';
        });
        
        const targetSection = document.getElementById(section);
        if (targetSection) {
            targetSection.style.display = 'block';
            targetSection.classList.add('fade-in');
        }
        
        this.currentSection = section;
    }

    // File Upload
    setupFileUpload() {
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const fileList = document.getElementById('fileList');
        
        // Click to upload
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });
        
        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragging');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragging');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragging');
            this.handleFiles(e.dataTransfer.files);
        });
        
        // File input change
        fileInput.addEventListener('change', (e) => {
            this.handleFiles(e.target.files);
        });
    }

    handleFiles(files) {
        this.selectedFiles = Array.from(files);
        this.displayFiles();
    }

    displayFiles() {
        const fileList = document.getElementById('fileList');
        
        if (this.selectedFiles.length === 0) {
            fileList.style.display = 'none';
            return;
        }
        
        fileList.style.display = 'block';
        fileList.innerHTML = this.selectedFiles.map((file, index) => `
            <div class="file-item fade-in">
                <div class="file-info">
                    <div class="file-icon">
                        <i data-feather="file-text"></i>
                    </div>
                    <div class="file-details">
                        <div class="file-name">${this.escapeHtml(file.name)}</div>
                        <div class="file-size">${this.formatFileSize(file.size)}</div>
                    </div>
                </div>
                <button class="btn btn-ghost btn-sm" onclick="platform.removeFile(${index})">
                    <i data-feather="x" width="16" height="16"></i>
                </button>
            </div>
        `).join('');
        
        feather.replace();
    }

    removeFile(index) {
        this.selectedFiles.splice(index, 1);
        this.displayFiles();
    }

    // Form Submission
    setupFormSubmission() {
        const form = document.getElementById('analysisForm');
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            if (this.analysisInProgress) return;
            
            const companyName = document.getElementById('companyName').value;
            
            if (!companyName || this.selectedFiles.length === 0) {
                this.showError('Please enter company name and select files');
                return;
            }
            
            await this.startAnalysis(companyName);
        });
    }

    async startAnalysis(companyName) {
        this.analysisInProgress = true;
        
        // Hide form, show conversation
        document.querySelector('.upload-section').style.display = 'none';
        document.getElementById('conversationSection').style.display = 'block';
        
        // Initialize conversation
        this.initializeConversation(companyName);
        
        try {
            // 실제 API 분석 호출
            const formData = new FormData();
            formData.append('company_name', companyName);
            
            // 선택된 파일들 추가
            this.selectedFiles.forEach(file => {
                formData.append('files', file);
            });
            
            // JWT 토큰 가져오기 - localStorage에서
            const token = localStorage.getItem('auth_token');
            if (!token) {
                console.error('No auth token found');
                window.location.href = '/login';
                return;
            }
            
            // Progress simulation
            await this.simulateProgress();
            
            // API 호출 - 대화형 분석 시작
            const response = await fetch('/api/conversation/start', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });
            
            // 응답 상태 확인
            if (!response.ok) {
                if (response.status === 401) {
                    console.error('Authentication failed');
                    localStorage.removeItem('auth_token');
                    window.location.href = '/login';
                    return;
                }
                const errorResult = await response.json();
                this.showError(errorResult.error || 'Analysis failed');
                return;
            }
            
            const result = await response.json();
            
            if (result.success) {
                this.currentConversationId = result.conversation_id;
                this.currentCompanyName = companyName;
                this.showResults(result.analysis);
                
                // 후속 질문 옵션 표시
                // Follow-up options (to be implemented)
                // if (result.next_options) {
                //     this.showFollowUpOptions(result.next_options);
                // }
            } else {
                this.showError(result.error || 'Analysis failed');
            }
            
        } catch (error) {
            console.error('Analysis error:', error);
            this.showError('Network error occurred');
        } finally {
            this.analysisInProgress = false;
        }
    }

    async simulateProgress() {
        const steps = ['step1', 'step2', 'step3', 'step4'];
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        const messages = [
            'Uploading files to secure cloud storage...',
            'Extracting text and data from documents...',
            'Analyzing with AI algorithms...',
            'Generating comprehensive report...'
        ];
        
        for (let i = 0; i < steps.length; i++) {
            // Update step
            document.getElementById(steps[i]).classList.add('active');
            
            // Update progress
            progressBar.style.width = `${(i + 1) * 25}%`;
            progressText.textContent = messages[i];
            
            // Wait before next step
            await this.sleep(1500);
            
            // Mark as completed
            document.getElementById(steps[i]).classList.add('completed');
        }
    }

    showResults(analysisData) {
        document.getElementById('progressSection').style.display = 'none';
        document.getElementById('resultsSection').style.display = 'block';
        
        // Populate with real analysis data
        this.populateResults(analysisData);
        
        this.analysisInProgress = false;
    }

    populateResults(data) {
        if (!data) {
            data = {
                investment_score: 7.5,
                market_position: "#2",
                risk_level: "Medium",
                growth_trend: "Positive",
                key_strengths: ["기본 분석 결과"],
                key_concerns: ["데이터 부족"],
                recommendation: "Hold"
            };
        }

        // Update stat cards with real data
        const statCards = document.querySelectorAll('.stat-card');
        if (statCards.length >= 3) {
            // Investment Score
            statCards[0].querySelector('.stat-value').innerHTML = 
                `${data.investment_score}<span class="text-secondary">/10</span>`;
            statCards[0].querySelector('.stat-change').textContent = 
                data.ai_powered ? 'AI Powered' : 'Calculated';
            
            // Market Position
            statCards[1].querySelector('.stat-value').textContent = data.market_position;
            statCards[1].querySelector('.stat-change').textContent = data.growth_trend;
            
            // Risk Level
            statCards[2].querySelector('.stat-value').textContent = data.risk_level;
            statCards[2].querySelector('.stat-change').textContent = 
                data.recommendation || 'Hold';
        }

        // Update executive summary with real analysis
        document.getElementById('summaryContent').innerHTML = `
            <div class="prose">
                <h3>AI Analysis Results</h3>
                <p>Based on our comprehensive AI analysis of the provided investment documents using Gemini AI, here are the key findings:</p>
                
                <div class="analysis-meta">
                    <p><strong>Analysis Date:</strong> ${new Date(data.analysis_date || Date.now()).toLocaleDateString('ko-KR')}</p>
                    <p><strong>AI Engine:</strong> ${data.ai_powered ? 'Gemini Pro' : 'Fallback Analysis'}</p>
                    <p><strong>Confidence Level:</strong> ${data.confidence || '85%'}</p>
                </div>
                
                <h4>Key Strengths</h4>
                <ul>
                    ${data.key_strengths && Array.isArray(data.key_strengths) ? 
                      data.key_strengths.map(strength => `<li>${strength}</li>`).join('') : 
                      '<li>분석 중...</li>'}
                </ul>
                
                <h4>Areas of Concern</h4>
                <ul>
                    ${data.key_concerns && Array.isArray(data.key_concerns) ? 
                      data.key_concerns.map(concern => `<li>${concern}</li>`).join('') : 
                      '<li>분석 중...</li>'}
                </ul>
                
                <h4>Investment Recommendation</h4>
                <div class="recommendation-badge ${data.recommendation.toLowerCase()}">
                    ${data.recommendation.toUpperCase()}
                </div>
                <p>투자 점수: <strong>${data.investment_score}/10</strong> | 시장 포지션: <strong>${data.market_position}</strong> | 리스크: <strong>${data.risk_level}</strong></p>
                
                ${data.error ? `<div class="error-notice">Note: ${data.error}</div>` : ''}
            </div>
        `;
    }

    // Tab Navigation
    setupTabNavigation() {
        const tabButtons = document.querySelectorAll('.tab-button');
        
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const targetTab = button.getAttribute('data-tab');
                this.switchTab(targetTab);
            });
        });
    }

    switchTab(tab) {
        // Update button states
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
            if (btn.getAttribute('data-tab') === tab) {
                btn.classList.add('active');
            }
        });
        
        // Update content visibility
        document.querySelectorAll('.tab-content').forEach(content => {
            content.style.display = 'none';
        });
        
        const targetContent = document.getElementById(tab);
        if (targetContent) {
            targetContent.style.display = 'block';
            targetContent.classList.add('fade-in');
        }
    }

    // Export Functions
    setupExportButtons() {
        document.getElementById('exportPdf').addEventListener('click', () => {
            this.showNotification('Preparing PDF export...');
            // Implement PDF export
        });
        
        document.getElementById('exportWord').addEventListener('click', () => {
            this.showNotification('Preparing Word export...');
            // Implement Word export
        });
        
        document.getElementById('shareReport').addEventListener('click', () => {
            this.showShareDialog();
        });
    }

    // Utility Functions
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    showError(message) {
        // Implement error notification
        console.error(message);
    }

    showNotification(message) {
        // Implement notification system
        console.log(message);
    }

    showShareDialog() {
        // Implement share dialog
        console.log('Share dialog');
    }

    // Initialize conversation
    initializeConversation(companyName) {
        this.currentCompanyName = companyName;
        const messagesContainer = document.getElementById('conversationMessages');
        
        // Add welcome message
        const welcomeMessage = this.createMessage('ai', `안녕하세요! ${companyName}의 투자 분석을 시작하겠습니다.`);
        messagesContainer.appendChild(welcomeMessage);
        
        // Add typing indicator
        const typingIndicator = this.createTypingIndicator();
        messagesContainer.appendChild(typingIndicator);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Start basic analysis immediately
        this.performBasicAnalysis(companyName);
    }
    
    createMessage(type, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                ${type === 'ai' ? '🤖' : 'U'}
            </div>
            <div class="message-content">
                <div class="message-bubble">
                    <div class="message-text">${content}</div>
                    <div class="message-time">${new Date().toLocaleTimeString('ko-KR')}</div>
                </div>
            </div>
        `;
        
        return messageDiv;
    }
    
    createTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message ai typing-message';
        typingDiv.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <div class="typing-indicator">
                    <div class="typing-dots">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                    <span class="typing-text">분석 중...</span>
                </div>
            </div>
        `;
        return typingDiv;
    }
    
    async performBasicAnalysis(companyName) {
        try {
            const formData = new FormData();
            formData.append('company_name', companyName);
            
            // Add selected files
            this.selectedFiles.forEach(file => {
                formData.append('files', file);
            });
            
            const token = localStorage.getItem('auth_token');
            
            // 1. 분석 시작
            const startResponse = await fetch('/api/analyze/start', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });
            
            const startResult = await startResponse.json();
            
            if (!startResult.success) {
                this.displayError(startResult.error);
                return;
            }
            
            // 2. 상태 폴링
            this.currentJobId = startResult.job_id;
            this.pollAnalysisStatus();
            
        } catch (error) {
            console.error('Analysis error:', error);
            this.displayError('분석 중 오류가 발생했습니다.');
        }
    }
    
    async pollAnalysisStatus() {
        try {
            const response = await fetch(`/api/analyze/status/${this.currentJobId}`);
            const result = await response.json();
            
            if (!result.success) {
                this.displayError(result.error);
                return;
            }
            
            // 진행률 업데이트
            this.updateProgress(result.progress, result.status);
            
            if (result.status === 'completed') {
                // Remove typing indicator
                const typingMessage = document.querySelector('.typing-message');
                if (typingMessage) {
                    typingMessage.remove();
                }
                
                // 완료된 결과 표시
                this.displayCompletedAnalysis(result.result);
                
            } else if (result.status === 'error') {
                this.displayError(result.error);
                
            } else {
                // 2초 후 다시 확인
                setTimeout(() => this.pollAnalysisStatus(), 2000);
            }
            
        } catch (error) {
            console.error('Polling error:', error);
            setTimeout(() => this.pollAnalysisStatus(), 3000); // 재시도
        }
    }
    
    updateProgress(progress, status) {
        const typingMessage = document.querySelector('.typing-message .typing-text');
        if (typingMessage) {
            const messages = {
                'started': '분석을 시작합니다...',
                'processing': `분석 진행 중... ${progress}%`
            };
            typingMessage.textContent = messages[status] || `처리 중... ${progress}%`;
        }
    }
    
    displayCompletedAnalysis(result) {
        const messagesContainer = document.getElementById('conversationMessages');
        
        // 전체 보고서 표시
        const reportContent = `
            <div class="analysis-card">
                <div class="analysis-card-header">
                    <i data-feather="file-text" class="analysis-card-icon"></i>
                    <span class="analysis-card-title">완전한 투자 분석 보고서</span>
                </div>
                <div class="full-report">
                    ${result.full_report.replace(/\n/g, '<br>').replace(/#{2,3}/g, '<strong>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}
                </div>
            </div>
        `;
        
        const resultMessage = this.createMessage('ai', reportContent);
        messagesContainer.appendChild(resultMessage);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        feather.replace();
    }
    
    displayAnalysisResult(result) {
        const messagesContainer = document.getElementById('conversationMessages');
        
        // Create analysis result message
        const analysisContent = `
            <div class="analysis-card">
                <div class="analysis-card-header">
                    <i data-feather="trending-up" class="analysis-card-icon"></i>
                    <span class="analysis-card-title">기본 분석 완료</span>
                </div>
                <div class="analysis-metrics">
                    <div class="metric-item">
                        <div class="metric-value">${result.analysis.investment_score}/10</div>
                        <div class="metric-label">투자 점수</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value">${result.analysis.recommendation}</div>
                        <div class="metric-label">추천</div>
                    </div>
                </div>
                <p>${result.analysis.key_insight}</p>
            </div>
            
            <div class="followup-options">
                <div class="followup-title">추가로 어떤 분석이 필요하신가요?</div>
                <div class="followup-grid">
                    ${result.next_options && Array.isArray(result.next_options) ? 
                      result.next_options.map(option => `
                        <button class="followup-card" data-type="${option.id}">
                            <div class="followup-card-icon">
                                <i data-feather="${option.icon || 'file-text'}"></i>
                            </div>
                            <div class="followup-card-content">
                                <div class="followup-card-title">${option.title}</div>
                                <div class="followup-card-desc">${option.description || ''}</div>
                            </div>
                        </button>
                    `).join('') : '<p>추가 분석 옵션을 불러오는 중...</p>'}
                </div>
            </div>
        `;
        
        const resultMessage = this.createMessage('ai', analysisContent);
        messagesContainer.appendChild(resultMessage);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Replace feather icons
        feather.replace();
        
        // Add event listeners to followup buttons
        document.querySelectorAll('.followup-card').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const questionType = e.currentTarget.getAttribute('data-type');
                this.handleFollowupQuestion(questionType);
            });
        });
    }
    
    displayError(error) {
        const messagesContainer = document.getElementById('conversationMessages');
        const errorMessage = this.createMessage('ai', `❌ 오류: ${error}`);
        messagesContainer.appendChild(errorMessage);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    async handleFollowupQuestion(questionType) {
        const messagesContainer = document.getElementById('conversationMessages');
        
        // Add user question message
        const questionTexts = {
            'financial': '재무 상세 분석을 요청합니다',
            'market': '시장 경쟁 분석을 요청합니다', 
            'risk': '리스크 심화 분석을 요청합니다',
            'team': '팀 및 조직 분석을 요청합니다',
            'product': '제품/서비스 분석을 요청합니다',
            'exit': 'Exit 전략 분석을 요청합니다',
            'custom': '직접 질문하기'
        };
        
        if (questionType !== 'custom') {
            const userMessage = this.createMessage('user', questionTexts[questionType]);
            messagesContainer.appendChild(userMessage);
        }
        
        // Add typing indicator
        const typingIndicator = this.createTypingIndicator();
        messagesContainer.appendChild(typingIndicator);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        try {
            const token = localStorage.getItem('auth_token');
            const response = await fetch('/api/conversation/followup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    conversation_id: this.currentConversationId,
                    question_type: questionType,
                    company_name: this.currentCompanyName
                })
            });
            
            const result = await response.json();
            
            // Remove typing indicator
            const typingMessage = document.querySelector('.typing-message');
            if (typingMessage) {
                typingMessage.remove();
            }
            
            if (result.success) {
                this.displayFollowupResult(result);
            } else {
                this.displayError(result.error);
            }
            
        } catch (error) {
            console.error('Followup error:', error);
            this.displayError('추가 분석 중 오류가 발생했습니다.');
        }
    }
    
    displayFollowupResult(result) {
        const messagesContainer = document.getElementById('conversationMessages');
        
        const followupContent = `
            <div class="analysis-card">
                <div class="analysis-card-header">
                    <i data-feather="info" class="analysis-card-icon"></i>
                    <span class="analysis-card-title">${this.getFollowupTitle(result.question_type)}</span>
                </div>
                <div class="message-text">${result.analysis.analysis_text}</div>
                ${result.analysis.metrics ? this.renderMetrics(result.analysis.metrics) : ''}
            </div>
        `;
        
        const resultMessage = this.createMessage('ai', followupContent);
        messagesContainer.appendChild(resultMessage);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        feather.replace();
    }
    
    getFollowupTitle(questionType) {
        const titles = {
            'financial': '재무 상세 분석 결과',
            'market': '시장 경쟁 분석 결과', 
            'risk': '리스크 심화 분석 결과',
            'team': '팀 및 조직 분석 결과',
            'product': '제품/서비스 분석 결과',
            'exit': 'Exit 전략 분석 결과',
            'custom': '추가 분석 결과'
        };
        return titles[questionType] || '분석 결과';
    }
    
    renderMetrics(metrics) {
        return `
            <div class="analysis-metrics">
                ${Object.entries(metrics).map(([key, value]) => `
                    <div class="metric-item">
                        <div class="metric-value">${value}</div>
                        <div class="metric-label">${key}</div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    // Logout functionality
    setupLogout() {
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                if (confirm('정말로 로그아웃 하시겠습니까?')) {
                    localStorage.removeItem('auth_token');
                    window.location.href = '/login';
                }
            });
        }
    }
}

// Initialize platform when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.platform = new MYSCPlatform();
});