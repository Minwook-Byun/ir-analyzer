// MYSC AI Agent - Linear-Inspired Investment Report Analysis Platform JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // 로그인 상태 확인
    checkAuthStatus();
    
    // Initialize theme
    initTheme();
    // Initialize Lucide icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }

    // Global state
    let currentFile = null;
    let currentImpactFile = null;
    let analysisInProgress = false;
    let theoryGenerationInProgress = false;
    let theoryData = null;

    // DOM elements
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const fileValidation = document.getElementById('fileValidation');
    const progressContainer = document.getElementById('progressContainer');
    const resultsContainer = document.getElementById('resultsContainer');
    const analysisForm = document.getElementById('analysisForm');
    const analyzeBtn = document.getElementById('analyzeBtn');

    // Impact/Theory elements
    const impactUploadArea = document.getElementById('impactUploadArea');
    const impactFileInput = document.getElementById('impactFileInput');
    const impactProgressContainer = document.getElementById('impactProgressContainer');
    const theoryResultsContainer = document.getElementById('theoryResultsContainer');
    const impactForm = document.getElementById('impactForm');
    const generateTheoryBtn = document.getElementById('generateTheoryBtn');

    // Navigation - wait for DOM to be fully loaded
    const navItems = document.querySelectorAll('.nav-item[data-section]');
    const sections = document.querySelectorAll('.section-content[id$="-section"]');

    // Tab functionality
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    // Initialize navigation
    initNavigation();
    initFileUpload();
    initImpactFileUpload();
    initTabs();
    initForm();
    initImpactForm();
    initTheoryDownloads();
    initThemeToggle();
    updateUsageStats();

    function initNavigation() {
        console.log('Initializing navigation...', { navItems: navItems.length, sections: sections.length });
        
        navItems.forEach(item => {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                const sectionId = this.dataset.section;
                console.log('Nav clicked:', sectionId);
                
                // Update active nav item
                navItems.forEach(nav => nav.classList.remove('active'));
                this.classList.add('active');
                
                // Show corresponding section
                const targetSectionId = `${sectionId}-section`;
                console.log('Looking for section:', targetSectionId);
                
                sections.forEach(section => {
                    section.classList.remove('active');
                    if (section.id === targetSectionId) {
                        section.classList.add('active');
                        console.log('Activated section:', section.id);
                    }
                });
                
                // Re-initialize Lucide icons for newly visible content
                if (typeof lucide !== 'undefined') {
                    lucide.createIcons();
                }
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
        const token = sessionStorage.getItem('auth_token');
        const formData = new FormData();
        formData.append('company_name', companyName);
        
        if (currentFile) {
            formData.append('file', currentFile);
        }
        
        if (irUrl) {
            formData.append('ir_url', irUrl);
        }

        const endpoint = currentFile ? '/api/analyze-ir-file' : '/api/analyze-ir';
        const options = {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        };

        if (currentFile) {
            options.body = formData;
        } else {
            options.headers['Content-Type'] = 'application/json';
            options.body = JSON.stringify({
                company_name: companyName,
                ir_url: irUrl
            });
        }

        fetch(endpoint, options)
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

    // Theory of Change functionality
    function initImpactFileUpload() {
        if (!impactUploadArea || !impactFileInput) return;

        // Click to upload
        impactUploadArea.addEventListener('click', () => {
            impactFileInput.click();
        });

        // Drag and drop
        impactUploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('dragover');
        });

        impactUploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
        });

        impactUploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleImpactFileSelect(files[0]);
            }
        });

        // File input change
        impactFileInput.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                handleImpactFileSelect(e.target.files[0]);
            }
        });
    }

    function handleImpactFileSelect(file) {
        currentImpactFile = file;
        updateImpactUploadArea(file);
    }

    function updateImpactUploadArea(file) {
        if (!impactUploadArea) return;

        const uploadContent = impactUploadArea.querySelector('.upload-content');
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

    function initImpactForm() {
        if (!impactForm) return;

        impactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (theoryGenerationInProgress) return;
            
            const organizationName = document.getElementById('organizationName').value.trim();
            const impactFocus = document.getElementById('impactFocus').value;
            
            if (!organizationName) {
                alert('조직/기업명을 입력해주세요.');
                return;
            }

            startTheoryGeneration(organizationName, impactFocus);
        });
    }

    function startTheoryGeneration(organizationName, impactFocus) {
        theoryGenerationInProgress = true;
        
        // Show progress
        if (impactProgressContainer) {
            impactProgressContainer.classList.add('show');
        }

        // Disable form
        setImpactFormDisabled(true);

        // Simulate theory generation progress
        simulateTheoryProgress();

        // Generate theory (simulate with demo data)
        generateTheoryOfChange(organizationName, impactFocus);
    }

    function simulateTheoryProgress() {
        const steps = ['impactStep1', 'impactStep2', 'impactStep3', 'impactStep4'];
        const progressFill = document.getElementById('impactProgressFill');
        const progressText = document.getElementById('impactProgressText');
        
        let currentStep = 0;
        
        const stepTexts = [
            '파일을 업로드하고 있습니다...',
            'IR 자료에서 데이터를 추출하고 있습니다...',
            'AI가 변화이론을 분석하고 생성하고 있습니다...',
            '변화이론 다이어그램이 완성되었습니다!'
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
                    setTimeout(updateStep, 1500);
                }
            }
        }

        updateStep();
    }

    function generateTheoryOfChange(organizationName, impactFocus) {
        // Simulate API call with demo data
        setTimeout(() => {
            // Load demo data
            loadDemoTheoryData(organizationName, impactFocus)
                .then(data => {
                    theoryData = data;
                    showTheoryResults(data);
                })
                .catch(error => {
                    console.error('Theory generation error:', error);
                    showTheoryError('변화이론 생성 중 오류가 발생했습니다.');
                })
                .finally(() => {
                    theoryGenerationInProgress = false;
                    setImpactFormDisabled(false);
                });
        }, 6000);
    }

    async function loadDemoTheoryData(organizationName, impactFocus) {
        // Load the JSON data we created
        try {
            const response = await fetch('/impact-report-data.json');
            const data = await response.json();
            
            // Customize data based on input
            data.organizationProfile.name = organizationName;
            if (impactFocus) {
                data.reportInfo.focus = impactFocus;
            }
            
            return data;
        } catch (error) {
            // Fallback to inline demo data
            return {
                theoryOfChange: {
                    structure: {
                        layers: [
                            {
                                id: "inputs",
                                name: "투입(Inputs)",
                                yPosition: 100,
                                backgroundColor: "#E8F4FD",
                                items: [
                                    { id: "funding", title: "자금", value: "5천만원", icon: "💰" },
                                    { id: "team", title: "인력", value: "10명", icon: "👥" },
                                    { id: "technology", title: "기술", value: "디지털 플랫폼", icon: "💻" }
                                ]
                            },
                            {
                                id: "activities",
                                name: "활동(Activities)",
                                yPosition: 280,
                                backgroundColor: "#F3E5F5",
                                items: [
                                    { id: "education", title: "디지털 교육", value: "8개 과정", icon: "📚" },
                                    { id: "platform", title: "플랫폼 구축", value: "3개 플랫폼", icon: "🔧" },
                                    { id: "campaign", title: "인식개선 캠페인", value: "15회", icon: "📢" }
                                ]
                            },
                            {
                                id: "outputs",
                                name: "산출(Outputs)",
                                yPosition: 460,
                                backgroundColor: "#E8F5E8",
                                items: [
                                    { id: "trained_people", title: "교육 이수자", value: "400명", icon: "🎓" },
                                    { id: "businesses_supported", title: "지원 사업체", value: "150개", icon: "🏪" },
                                    { id: "platforms_launched", title: "구축 플랫폼", value: "3개", icon: "🚀" }
                                ]
                            },
                            {
                                id: "outcomes",
                                name: "성과(Outcomes)",
                                yPosition: 640,
                                backgroundColor: "#FFF3E0",
                                items: [
                                    { id: "employment_increase", title: "취업률 향상", value: "75%", icon: "💼" },
                                    { id: "sales_increase", title: "매출 증가", value: "35%", icon: "📈" },
                                    { id: "digital_literacy", title: "디지털 역량 강화", value: "85%", icon: "🎯" }
                                ]
                            },
                            {
                                id: "impact",
                                name: "임팩트(Impact)",
                                yPosition: 820,
                                backgroundColor: "#FFEBEE",
                                items: [
                                    { id: "social_cohesion", title: "사회적 결속력 강화", value: "장기적 변화", icon: "🤲" },
                                    { id: "economic_sustainability", title: "경제적 지속가능성", value: "생태계 구축", icon: "♻️" }
                                ]
                            }
                        ]
                    }
                },
                organizationProfile: {
                    name: organizationName
                }
            };
        }
    }

    function showTheoryResults(data) {
        if (!theoryResultsContainer) return;

        // Update results title
        const resultsTitle = document.getElementById('theoryResultsTitle');
        if (resultsTitle) {
            resultsTitle.textContent = `${data.organizationProfile.name} 변화이론 다이어그램 완성`;
        }

        // Generate visualization
        generateTheoryVisualization(data.theoryOfChange);

        // Update tab contents
        updateTheoryTabContents(data);

        // Show results
        theoryResultsContainer.classList.add('show');
        
        // Scroll to results
        theoryResultsContainer.scrollIntoView({ behavior: 'smooth' });
    }

    function generateTheoryVisualization(theoryOfChange) {
        const svg = document.getElementById('theoryChart');
        if (!svg || !theoryOfChange.structure) return;

        // Clear existing content
        svg.innerHTML = '';

        const layers = theoryOfChange.structure.layers;
        const svgWidth = 1200;
        const svgHeight = 1000;

        // Set SVG dimensions
        svg.setAttribute('viewBox', `0 0 ${svgWidth} ${svgHeight}`);

        // Create background gradient
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        const gradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
        gradient.setAttribute('id', 'backgroundGradient');
        gradient.setAttribute('x1', '0%');
        gradient.setAttribute('y1', '0%');
        gradient.setAttribute('x2', '0%');
        gradient.setAttribute('y2', '100%');

        const stop1 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
        stop1.setAttribute('offset', '0%');
        stop1.setAttribute('stop-color', '#f8fafc');

        const stop2 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
        stop2.setAttribute('offset', '100%');
        stop2.setAttribute('stop-color', '#e2e8f0');

        gradient.appendChild(stop1);
        gradient.appendChild(stop2);
        defs.appendChild(gradient);
        svg.appendChild(defs);

        // Background rectangle
        const bgRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        bgRect.setAttribute('width', '100%');
        bgRect.setAttribute('height', '100%');
        bgRect.setAttribute('fill', 'url(#backgroundGradient)');
        svg.appendChild(bgRect);

        // Draw layers
        layers.forEach((layer, layerIndex) => {
            drawLayer(svg, layer, layerIndex, svgWidth);
        });

        // Draw connections
        drawConnections(svg, layers);
    }

    function drawLayer(svg, layer, layerIndex, svgWidth) {
        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        g.setAttribute('class', 'theory-layer');

        // Layer header
        const headerRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        headerRect.setAttribute('x', svgWidth/2 - 100);
        headerRect.setAttribute('y', layer.yPosition - 30);
        headerRect.setAttribute('width', 200);
        headerRect.setAttribute('height', 25);
        headerRect.setAttribute('rx', 12);
        headerRect.setAttribute('fill', getLayerColor(layer.id));
        g.appendChild(headerRect);

        const headerText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        headerText.setAttribute('x', svgWidth/2);
        headerText.setAttribute('y', layer.yPosition - 12);
        headerText.setAttribute('text-anchor', 'middle');
        headerText.setAttribute('fill', 'white');
        headerText.setAttribute('font-size', '12');
        headerText.setAttribute('font-weight', '600');
        headerText.textContent = layer.name;
        g.appendChild(headerText);

        // Layer items
        const itemsPerRow = layer.items.length;
        const itemWidth = 180;
        const itemHeight = 80;
        const spacing = 20;
        const totalWidth = itemsPerRow * itemWidth + (itemsPerRow - 1) * spacing;
        const startX = (svgWidth - totalWidth) / 2;

        layer.items.forEach((item, index) => {
            const x = startX + index * (itemWidth + spacing);
            const y = layer.yPosition;

            // Item background
            const itemRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            itemRect.setAttribute('x', x);
            itemRect.setAttribute('y', y);
            itemRect.setAttribute('width', itemWidth);
            itemRect.setAttribute('height', itemHeight);
            itemRect.setAttribute('rx', 8);
            itemRect.setAttribute('fill', 'white');
            itemRect.setAttribute('stroke', getLayerColor(layer.id));
            itemRect.setAttribute('stroke-width', 2);
            itemRect.setAttribute('class', 'theory-svg-item');
            g.appendChild(itemRect);

            // Item icon (as text for now)
            const iconText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            iconText.setAttribute('x', x + itemWidth/2);
            iconText.setAttribute('y', y + 20);
            iconText.setAttribute('text-anchor', 'middle');
            iconText.setAttribute('font-size', '20');
            iconText.textContent = item.icon;
            g.appendChild(iconText);

            // Item title
            const titleText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            titleText.setAttribute('x', x + itemWidth/2);
            titleText.setAttribute('y', y + 40);
            titleText.setAttribute('text-anchor', 'middle');
            titleText.setAttribute('font-size', '11');
            titleText.setAttribute('font-weight', '600');
            titleText.setAttribute('fill', '#1f2937');
            titleText.textContent = item.title;
            g.appendChild(titleText);

            // Item value
            const valueText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            valueText.setAttribute('x', x + itemWidth/2);
            valueText.setAttribute('y', y + 55);
            valueText.setAttribute('text-anchor', 'middle');
            valueText.setAttribute('font-size', '12');
            valueText.setAttribute('font-weight', '700');
            valueText.setAttribute('fill', '#3b82f6');
            valueText.textContent = item.value;
            g.appendChild(valueText);

            // Store item position for connections
            item._position = { x: x + itemWidth/2, y: y + itemHeight };
        });

        svg.appendChild(g);
    }

    function drawConnections(svg, layers) {
        for (let i = 0; i < layers.length - 1; i++) {
            const currentLayer = layers[i];
            const nextLayer = layers[i + 1];

            currentLayer.items.forEach((currentItem, currentIndex) => {
                nextLayer.items.forEach((nextItem, nextIndex) => {
                    // Draw connection line
                    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                    line.setAttribute('x1', currentItem._position.x);
                    line.setAttribute('y1', currentItem._position.y);
                    line.setAttribute('x2', nextItem._position.x);
                    line.setAttribute('y2', nextLayer.yPosition);
                    line.setAttribute('stroke', '#cbd5e1');
                    line.setAttribute('stroke-width', 1.5);
                    line.setAttribute('opacity', 0.6);
                    svg.appendChild(line);
                });
            });
        }
    }

    function getLayerColor(layerId) {
        const colors = {
            'inputs': '#2196F3',
            'activities': '#9C27B0',
            'outputs': '#4CAF50',
            'outcomes': '#FF9800',
            'impact': '#F44336'
        };
        return colors[layerId] || '#6b7280';
    }

    function updateTheoryTabContents(data) {
        // Update overview tab
        const theoryOverview = document.getElementById('theoryOverview');
        if (theoryOverview) {
            theoryOverview.innerHTML = `
                <div class="theory-summary-card">
                    <div class="theory-summary-title">
                        <i data-lucide="lightbulb" style="width: 20px; height: 20px;"></i>
                        변화이론 개요
                    </div>
                    <div class="theory-summary-content">
                        <p><strong>${data.organizationProfile.name}</strong>의 변화이론은 5단계 구조로 설계되었습니다.</p>
                        <p>투입된 자원을 통해 다양한 활동을 수행하고, 이를 통해 구체적인 산출물을 생성하여 
                        궁극적으로 사회적 임팩트를 창출하는 논리적 연결구조를 보여줍니다.</p>
                    </div>
                </div>
                <div class="data-grid">
                    <div class="data-card">
                        <div class="data-card-title">
                            <i data-lucide="users" style="width: 16px; height: 16px;"></i>
                            총 수혜자
                        </div>
                        <div class="data-card-value">1,500명</div>
                        <div class="data-card-description">직간접적으로 혜택을 받은 총 인원</div>
                    </div>
                    <div class="data-card">
                        <div class="data-card-title">
                            <i data-lucide="folder" style="width: 16px; height: 16px;"></i>
                            완료 프로젝트
                        </div>
                        <div class="data-card-value">8개</div>
                        <div class="data-card-description">성공적으로 완료된 프로젝트 수</div>
                    </div>
                    <div class="data-card">
                        <div class="data-card-title">
                            <i data-lucide="handshake" style="width: 16px; height: 16px;"></i>
                            파트너십
                        </div>
                        <div class="data-card-value">12개</div>
                        <div class="data-card-description">협력 기관 및 파트너 조직</div>
                    </div>
                    <div class="data-card">
                        <div class="data-card-title">
                            <i data-lucide="target" style="width: 16px; height: 16px;"></i>
                            임팩트 영역
                        </div>
                        <div class="data-card-value">3개</div>
                        <div class="data-card-description">사회적, 경제적, 환경적 임팩트</div>
                    </div>
                </div>
            `;
        }

        // Update data tab
        const theoryData = document.getElementById('theoryData');
        if (theoryData) {
            theoryData.innerHTML = `
                <h4>추출된 핵심 데이터</h4>
                <div class="data-grid">
                    <div class="data-card">
                        <div class="data-card-title">투입 자원</div>
                        <div class="data-card-value">5천만원</div>
                        <div class="data-card-description">정부지원금, 기부금, 파트너십 자금</div>
                    </div>
                    <div class="data-card">
                        <div class="data-card-title">참여 인력</div>
                        <div class="data-card-value">10명</div>
                        <div class="data-card-description">전문가 팀 및 자원봉사자</div>
                    </div>
                    <div class="data-card">
                        <div class="data-card-title">디지털 교육</div>
                        <div class="data-card-value">8개 과정</div>
                        <div class="data-card-description">코딩, 디지털 리터러시 교육</div>
                    </div>
                    <div class="data-card">
                        <div class="data-card-title">취업률 향상</div>
                        <div class="data-card-value">75%</div>
                        <div class="data-card-description">교육 참여자 취업 성공률</div>
                    </div>
                </div>
            `;
        }

        // Update insights tab
        const theoryInsights = document.getElementById('theoryInsights');
        if (theoryInsights) {
            theoryInsights.innerHTML = `
                <div class="insight-item">
                    <div class="insight-header">
                        <i data-lucide="trending-up" style="width: 16px; height: 16px;"></i>
                        핵심 성과 요인
                        <span class="insight-priority high">높음</span>
                    </div>
                    <div class="insight-content">
                        디지털 교육과 플랫폼 구축을 통한 체계적 접근이 75%의 높은 취업률 달성에 기여했습니다.
                    </div>
                </div>
                <div class="insight-item">
                    <div class="insight-header">
                        <i data-lucide="network" style="width: 16px; height: 16px;"></i>
                        연결성 분석
                        <span class="insight-priority medium">중간</span>
                    </div>
                    <div class="insight-content">
                        투입-활동-산출-성과-임팩트 간의 논리적 연결구조가 명확하게 설계되어 있어 효과적인 성과 창출이 가능합니다.
                    </div>
                </div>
                <div class="insight-item">
                    <div class="insight-header">
                        <i data-lucide="lightbulb" style="width: 16px; height: 16px;"></i>
                        개선 제안
                        <span class="insight-priority low">낮음</span>
                    </div>
                    <div class="insight-content">
                        환경적 임팩트 측정 지표를 추가하여 지속가능성 관점에서의 성과를 더욱 강화할 수 있습니다.
                    </div>
                </div>
            `;
        }

        // Re-initialize icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    function showTheoryError(message) {
        alert(`오류: ${message}`);
        
        // Hide progress
        if (impactProgressContainer) {
            impactProgressContainer.classList.remove('show');
        }
    }

    function setImpactFormDisabled(disabled) {
        if (!impactForm) return;

        const inputs = impactForm.querySelectorAll('input, select, button');
        inputs.forEach(input => {
            input.disabled = disabled;
        });

        if (generateTheoryBtn) {
            if (disabled) {
                generateTheoryBtn.innerHTML = `
                    <i data-lucide="loader" style="width: 20px; height: 20px; margin-right: 8px; animation: spin 1s linear infinite;"></i>
                    생성 중...
                `;
            } else {
                generateTheoryBtn.innerHTML = `
                    <i data-lucide="sparkles" style="width: 20px; height: 20px; margin-right: 8px;"></i>
                    변화이론 다이어그램 생성하기
                `;
            }
            
            // Re-initialize icons
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
        }
    }

    function initTheoryDownloads() {
        // Download functionality
        document.addEventListener('click', function(e) {
            if (e.target.id === 'downloadSvg') {
                downloadTheoryAsSvg();
            } else if (e.target.id === 'downloadPng') {
                downloadTheoryAsPng();
            } else if (e.target.id === 'downloadJson') {
                downloadTheoryAsJson();
            }
        });
    }

    function downloadTheoryAsSvg() {
        const svg = document.getElementById('theoryChart');
        if (!svg) return;

        const svgData = new XMLSerializer().serializeToString(svg);
        const svgBlob = new Blob([svgData], {type: 'image/svg+xml;charset=utf-8'});
        const svgUrl = URL.createObjectURL(svgBlob);
        
        const downloadLink = document.createElement('a');
        downloadLink.href = svgUrl;
        downloadLink.download = 'theory-of-change.svg';
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
        URL.revokeObjectURL(svgUrl);
    }

    function downloadTheoryAsPng() {
        const svg = document.getElementById('theoryChart');
        if (!svg) return;

        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();
        
        canvas.width = 1200;
        canvas.height = 1000;
        
        const svgData = new XMLSerializer().serializeToString(svg);
        const svgBlob = new Blob([svgData], {type: 'image/svg+xml;charset=utf-8'});
        const url = URL.createObjectURL(svgBlob);
        
        img.onload = function() {
            ctx.drawImage(img, 0, 0);
            
            canvas.toBlob(function(blob) {
                const pngUrl = URL.createObjectURL(blob);
                const downloadLink = document.createElement('a');
                downloadLink.href = pngUrl;
                downloadLink.download = 'theory-of-change.png';
                document.body.appendChild(downloadLink);
                downloadLink.click();
                document.body.removeChild(downloadLink);
                URL.revokeObjectURL(pngUrl);
            }, 'image/png');
            
            URL.revokeObjectURL(url);
        };
        
        img.src = url;
    }

    function downloadTheoryAsJson() {
        if (!theoryData) return;

        const jsonStr = JSON.stringify(theoryData, null, 2);
        const jsonBlob = new Blob([jsonStr], {type: 'application/json'});
        const jsonUrl = URL.createObjectURL(jsonBlob);
        
        const downloadLink = document.createElement('a');
        downloadLink.href = jsonUrl;
        downloadLink.download = 'theory-of-change-data.json';
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
        URL.revokeObjectURL(jsonUrl);
    }

    // Theme Management
    function initTheme() {
        const savedTheme = localStorage.getItem('theme');
        const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const theme = savedTheme || (systemDark ? 'dark' : 'light');
        
        setTheme(theme);
        
        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem('theme')) {
                setTheme(e.matches ? 'dark' : 'light');
            }
        });
    }
    
    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        // Update theme toggle icon
        updateThemeToggleIcon(theme);
    }
    
    function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    }
    
    function initThemeToggle() {
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', toggleTheme);
        }
    }
    
    function updateThemeToggleIcon(theme) {
        const themeToggle = document.getElementById('themeToggle');
        if (!themeToggle) return;
        
        const iconHtml = theme === 'dark' 
            ? '<i data-lucide="sun" style="width: 20px; height: 20px;"></i>'
            : '<i data-lucide="moon" style="width: 20px; height: 20px;"></i>';
        
        themeToggle.innerHTML = iconHtml;
        
        // Re-initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

// CSS for loading animation
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);

    // Initialize theme on page load
    initTheme();
    initThemeToggle();

    // 로그인 상태 확인 함수
    function checkAuthStatus() {
        const token = sessionStorage.getItem('auth_token');
        console.log('Checking auth status, token:', token); // 디버깅용
        
        if (!token) {
            console.log('No token found, redirecting to login'); // 디버깅용
            // 로그인되지 않았다면 로그인 페이지로 리다이렉트
            window.location.href = '/login';
            return;
        }

        // 토큰이 유효한지 확인 (만료 시간 체크)
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            const now = Math.floor(Date.now() / 1000);
            
            if (payload.exp < now) {
                // 토큰이 만료되었다면 로그인 페이지로 리다이렉트
                sessionStorage.removeItem('auth_token');
                sessionStorage.removeItem('api_key');
                window.location.href = '/login';
                return;
            }
        } catch (error) {
            // 토큰 파싱 실패 시 로그인 페이지로 리다이렉트
            sessionStorage.removeItem('auth_token');
            sessionStorage.removeItem('api_key');
            window.location.href = '/login';
            return;
        }

        // 로그아웃 버튼 추가
        addLogoutButton();
    }

    // 로그아웃 버튼 추가 함수
    function addLogoutButton() {
        // 기존 로그아웃 버튼이 있다면 제거
        const existingLogoutBtn = document.getElementById('logoutBtn');
        if (existingLogoutBtn) {
            existingLogoutBtn.remove();
        }

        // 네비게이션 바에 로그아웃 버튼 추가
        const nav = document.querySelector('.header-nav');
        if (nav) {
            const logoutBtn = document.createElement('button');
            logoutBtn.id = 'logoutBtn';
            logoutBtn.className = 'btn btn-secondary';
            logoutBtn.innerHTML = `
                <i data-lucide="log-out" style="width: 16px; height: 16px; margin-right: 8px;"></i>
                로그아웃
            `;
            logoutBtn.style.marginLeft = 'auto';
            logoutBtn.addEventListener('click', logout);
            nav.appendChild(logoutBtn);

            // 아이콘 초기화
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
        }
    }

    // 로그아웃 함수
    function logout() {
        // 세션 스토리지 클리어
        sessionStorage.removeItem('auth_token');
        sessionStorage.removeItem('api_key');
        
        // 로그인 페이지로 리다이렉트
        window.location.href = '/login';
    }

    // API 요청 시 에러 처리 개선
    function handleApiError(response) {
        if (response.status === 401) {
            // 인증 오류 시 로그인 페이지로 리다이렉트
            sessionStorage.removeItem('auth_token');
            sessionStorage.removeItem('api_key');
            window.location.href = '/login';
            return;
        }
        
        return response.json();
    }
});