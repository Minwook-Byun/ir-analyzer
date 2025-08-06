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
        
        // Hide form, show progress
        document.querySelector('.upload-section').style.display = 'none';
        document.getElementById('progressSection').style.display = 'block';
        
        // Simulate progress steps
        await this.simulateProgress();
        
        // Show results
        this.showResults();
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

    showResults() {
        document.getElementById('progressSection').style.display = 'none';
        document.getElementById('resultsSection').style.display = 'block';
        
        // Populate with sample data (in real implementation, this would come from API)
        this.populateResults();
        
        this.analysisInProgress = false;
    }

    populateResults() {
        // Sample executive summary
        document.getElementById('summaryContent').innerHTML = `
            <div class="prose">
                <h3>Key Findings</h3>
                <p>Based on our comprehensive analysis of the provided investment documents, we have identified several key opportunities and considerations for this investment.</p>
                
                <h4>Strengths</h4>
                <ul>
                    <li>Strong market position with 23% market share</li>
                    <li>Consistent revenue growth of 15% YoY</li>
                    <li>Experienced management team with proven track record</li>
                    <li>Innovative product pipeline with 5 products in late-stage development</li>
                </ul>
                
                <h4>Areas of Concern</h4>
                <ul>
                    <li>Increasing competition from emerging market players</li>
                    <li>Regulatory changes may impact profit margins</li>
                    <li>High dependency on key customers (top 3 = 45% of revenue)</li>
                </ul>
                
                <h4>Investment Recommendation</h4>
                <p>We recommend proceeding with the investment with a target valuation of $450-500M, contingent on successful due diligence of the technology stack and customer contracts.</p>
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
}

// Initialize platform when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.platform = new MYSCPlatform();
});