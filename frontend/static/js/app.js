// MYSC AI Agent - Investment Report Analysis Platform JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Lucide icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    // Global state
    let currentFile = null;
    let analysisInProgress = false;

    // DOM elements
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const fileValidation = document.getElementById('fileValidation');
    const progressContainer = document.getElementById('progressContainer');
    const resultsContainer = document.getElementById('resultsContainer');
    const analysisForm = document.getElementById('analysisForm');
    const analyzeBtn = document.getElementById('analyzeBtn');

    // Navigation
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.section-content');

    // Tab functionality
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    // Initialize navigation
    initNavigation();
    initFileUpload();
    initTabs();
    initForm();
    updateUsageStats();

    function initNavigation() {
        navItems.forEach(item => {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                const sectionId = this.dataset.section;
                
                // Update active nav item
                navItems.forEach(nav => nav.classList.remove('active'));
                this.classList.add('active');
                
                // Show corresponding section
                sections.forEach(section => {
                    section.classList.remove('active');
                    if (section.id === `${sectionId}-section`) {
                        section.classList.add('active');
                    }
                });
            });
        });
    }

    function initFileUpload() {
        if (!uploadArea || !fileInput) return;

        // Click to upload
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });

        // Drag and drop
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileSelect(files[0]);
            }
        });

        // File input change
        fileInput.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                handleFileSelect(e.target.files[0]);
            }
        });
    }

    function handleFileSelect(file) {
        currentFile = file;
        
        // Show validation
        if (fileValidation) {
            fileValidation.classList.add('show');
            validateFile(file);
        }

        // Update upload area
        updateUploadArea(file);
    }

    function validateFile(file) {
        const formatValidation = document.getElementById('formatValidation');
        const sizeValidation = document.getElementById('sizeValidation');
        
        // Check format
        const validFormats = ['.pdf', '.xlsx', '.xls', '.docx', '.doc'];
        const fileExt = '.' + file.name.split('.').pop().toLowerCase();
        const isValidFormat = validFormats.includes(fileExt);
        
        if (formatValidation) {
            formatValidation.classList.toggle('success', isValidFormat);
            formatValidation.classList.toggle('error', !isValidFormat);
        }

        // Check size (50MB limit)
        const maxSize = 50 * 1024 * 1024; // 50MB in bytes
        const isValidSize = file.size <= maxSize;
        
        if (sizeValidation) {
            sizeValidation.classList.toggle('success', isValidSize);
            sizeValidation.classList.toggle('error', !isValidSize);
            
            const sizeText = formatFileSize(file.size);
            sizeValidation.querySelector('span').textContent = `파일 크기: ${sizeText} (최대 50MB)`;
        }

        // Enable/disable analyze button
        const canAnalyze = isValidFormat && isValidSize;
        if (analyzeBtn) {
            analyzeBtn.disabled = !canAnalyze;
        }

        return canAnalyze;
    }

    function updateUploadArea(file) {
        if (!uploadArea) return;

        const uploadContent = uploadArea.querySelector('.upload-content');
        if (!uploadContent) return;

        uploadContent.innerHTML = `
            <div class="upload-icon">
                <i data-lucide="file-check" style="width: 32px; height: 32px;"></i>
            </div>
            <div class="upload-text">파일이 선택되었습니다</div>
            <div class="upload-subtext">${file.name}</div>
            <div class="upload-subtext">${formatFileSize(file.size)}</div>
        `;

        // Re-initialize icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function initTabs() {
        tabButtons.forEach(button => {
            button.addEventListener('click', function() {
                const tabId = this.dataset.tab;
                
                // Update active tab button
                tabButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                // Show corresponding tab content
                tabContents.forEach(content => {
                    content.classList.remove('active');
                    if (content.id === `tab-${tabId}`) {
                        content.classList.add('active');
                    }
                });
            });
        });
    }

    function initForm() {
        if (!analysisForm) return;

        analysisForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (analysisInProgress) return;
            
            const companyName = document.getElementById('companyName').value.trim();
            const irUrl = document.getElementById('irUrl').value.trim();
            
            if (!companyName) {
                alert('회사명을 입력해주세요.');
                return;
            }

            if (!currentFile && !irUrl) {
                alert('IR 자료 파일을 업로드하거나 URL을 입력해주세요.');
                return;
            }

            startAnalysis(companyName, irUrl);
        });
    }

    function startAnalysis(companyName, irUrl) {
        analysisInProgress = true;
        
        // Show progress
        if (progressContainer) {
            progressContainer.classList.add('show');
        }

        // Hide validation
        if (fileValidation) {
            fileValidation.classList.remove('show');
        }

        // Disable form
        setFormDisabled(true);

        // Simulate analysis progress
        simulateProgress();

        // Make API call
        performAnalysis(companyName, irUrl);
    }

    function simulateProgress() {
        const steps = ['step1', 'step2', 'step3', 'step4'];
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        
        let currentStep = 0;
        
        const stepTexts = [
            '파일을 업로드하고 있습니다...',
            '문서를 처리하고 있습니다...',
            'AI가 투자심사보고서를 생성하고 있습니다...',
            '분석이 완료되었습니다!'
        ];

        function updateStep() {
            if (currentStep < steps.length) {
                // Update step visual
                const stepElement = document.getElementById(steps[currentStep]);
                if (stepElement) {
                    const circle = stepElement.querySelector('.step-circle');
                    if (currentStep < steps.length - 1) {
                        circle.classList.add('active');
                    } else {
                        circle.classList.add('completed');
                    }
                }

                // Update progress bar
                if (progressFill) {
                    const progress = ((currentStep + 1) / steps.length) * 100;
                    progressFill.style.width = `${progress}%`;
                }

                // Update text
                if (progressText) {
                    progressText.textContent = stepTexts[currentStep];
                }

                currentStep++;
                
                if (currentStep < steps.length) {
                    setTimeout(updateStep, 2000);
                }
            }
        }

        updateStep();
    }

    function performAnalysis(companyName, irUrl) {
        const formData = new FormData();
        formData.append('company_name', companyName);
        
        if (currentFile) {
            formData.append('file', currentFile);
        }
        
        if (irUrl) {
            formData.append('ir_url', irUrl);
        }

        fetch('/analyze', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showResults(data);
            } else {
                showError(data.error || '분석 중 오류가 발생했습니다.');
            }
        })
        .catch(error => {
            console.error('Analysis error:', error);
            showError('서버 연결 오류가 발생했습니다.');
        })
        .finally(() => {
            analysisInProgress = false;
            setFormDisabled(false);
        });
    }

    function showResults(data) {
        if (!resultsContainer) return;

        // Update results content
        const resultsTitle = document.getElementById('resultsTitle');
        if (resultsTitle) {
            resultsTitle.textContent = `${data.company_name} 투자심사보고서 완성`;
        }

        const executiveSummary = document.getElementById('executiveSummary');
        if (executiveSummary && data.executive_summary) {
            executiveSummary.textContent = data.executive_summary;
        }

        // Update tab contents
        const investmentReport = document.getElementById('investmentReport');
        const financialReport = document.getElementById('financialReport');
        const riskReport = document.getElementById('riskReport');
        const recommendationsReport = document.getElementById('recommendationsReport');

        if (investmentReport && data.investment_report) {
            investmentReport.innerHTML = formatReportContent(data.investment_report);
        }

        if (financialReport && data.financial_analysis) {
            financialReport.innerHTML = formatReportContent(data.financial_analysis);
        }

        if (riskReport && data.risk_assessment) {
            riskReport.innerHTML = formatReportContent(data.risk_assessment);
        }

        if (recommendationsReport && data.recommendations) {
            recommendationsReport.innerHTML = formatReportContent(data.recommendations);
        }

        // Show results
        resultsContainer.classList.add('show');
        
        // Scroll to results
        resultsContainer.scrollIntoView({ behavior: 'smooth' });

        // Update usage stats
        updateUsageStats();
    }

    function formatReportContent(content) {
        if (typeof content === 'string') {
            return content.replace(/\n/g, '<br>');
        }
        return JSON.stringify(content, null, 2);
    }

    function showError(message) {
        alert(`오류: ${message}`);
        
        // Hide progress
        if (progressContainer) {
            progressContainer.classList.remove('show');
        }
    }

    function setFormDisabled(disabled) {
        const inputs = analysisForm.querySelectorAll('input, button');
        inputs.forEach(input => {
            input.disabled = disabled;
        });

        if (analyzeBtn) {
            if (disabled) {
                analyzeBtn.innerHTML = `
                    <i data-lucide="loader" style="width: 20px; height: 20px; margin-right: 8px; animation: spin 1s linear infinite;"></i>
                    분석 중...
                `;
            } else {
                analyzeBtn.innerHTML = `
                    <i data-lucide="sparkles" style="width: 20px; height: 20px; margin-right: 8px;"></i>
                    투자심사보고서 생성하기
                `;
            }
            
            // Re-initialize icons
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
        }
    }

    function updateUsageStats() {
        // Simulate usage stats
        const todayUsage = document.getElementById('todayUsage');
        const monthlyUsage = document.getElementById('monthlyUsage');
        const totalAnalyses = document.getElementById('totalAnalyses');
        const usagePercent = document.getElementById('usagePercent');
        const usageProgress = document.getElementById('usageProgress');

        if (todayUsage) {
            todayUsage.textContent = '1,250 토큰';
        }

        if (monthlyUsage) {
            monthlyUsage.textContent = '15,430 토큰';
        }

        if (totalAnalyses) {
            totalAnalyses.textContent = '23회';
        }

        if (usagePercent) {
            usagePercent.textContent = '15%';
        }

        if (usageProgress) {
            usageProgress.style.width = '15%';
        }
    }

    // Export functionality
    document.addEventListener('click', function(e) {
        if (e.target.id === 'exportPdf') {
            exportReport('pdf');
        } else if (e.target.id === 'exportWord') {
            exportReport('word');
        } else if (e.target.id === 'shareReport') {
            shareReport();
        }
    });

    function exportReport(format) {
        alert(`${format.toUpperCase()} 내보내기 기능은 준비 중입니다.`);
    }

    function shareReport() {
        alert('공유하기 기능은 준비 중입니다.');
    }
});

// CSS for loading animation
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);