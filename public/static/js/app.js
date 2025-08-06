// MYSC IR Platform - Main Application JavaScript

class MYSCPlatform {
    constructor() {
        this.currentSection = 'analysis';
        this.selectedFiles = [];
        this.analysisInProgress = false;
        
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
            
            // JWT 토큰 가져오기
            const token = localStorage.getItem('auth_token');
            if (!token) {
                window.location.href = '/login';
                return;
            }
            
            // Progress simulation
            await this.simulateProgress();
            
            // API 호출
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showResults(result.analysis);
            } else {
                if (response.status === 401) {
                    localStorage.removeItem('auth_token');
                    window.location.href = '/login';
                } else {
                    this.showError(result.error || 'Analysis failed');
                }
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
                    ${data.key_strengths.map(strength => `<li>${strength}</li>`).join('')}
                </ul>
                
                <h4>Areas of Concern</h4>
                <ul>
                    ${data.key_concerns.map(concern => `<li>${concern}</li>`).join('')}
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