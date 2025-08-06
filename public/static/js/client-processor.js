// Client-side PDF processing with Web Workers
class ClientProcessor {
    constructor() {
        this.worker = null;
        this.initializeWorker();
    }

    initializeWorker() {
        // PDF.js를 사용한 클라이언트 사이드 PDF 파싱
        const workerCode = `
            importScripts('https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js');

            self.onmessage = async function(e) {
                const { file, type } = e.data;
                
                try {
                    if (type === 'pdf') {
                        const text = await extractPDFText(file);
                        self.postMessage({ success: true, text });
                    }
                } catch (error) {
                    self.postMessage({ success: false, error: error.message });
                }
            };

            async function extractPDFText(arrayBuffer) {
                const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
                let fullText = '';
                
                for (let i = 1; i <= pdf.numPages; i++) {
                    const page = await pdf.getPage(i);
                    const textContent = await page.getTextContent();
                    const pageText = textContent.items.map(item => item.str).join(' ');
                    fullText += pageText + '\\n';
                }
                
                return fullText;
            }
        `;

        const blob = new Blob([workerCode], { type: 'application/javascript' });
        this.worker = new Worker(URL.createObjectURL(blob));
    }

    async processFile(file) {
        return new Promise((resolve, reject) => {
            this.worker.onmessage = (e) => {
                if (e.data.success) {
                    resolve(e.data.text);
                } else {
                    reject(new Error(e.data.error));
                }
            };

            // 파일을 ArrayBuffer로 변환하여 워커에 전송
            const reader = new FileReader();
            reader.onload = () => {
                this.worker.postMessage({
                    file: reader.result,
                    type: file.type.includes('pdf') ? 'pdf' : 'other'
                });
            };
            reader.readAsArrayBuffer(file);
        });
    }

    async analyzeWithGemini(text, apiKey, companyName) {
        // 클라이언트에서 직접 Gemini API 호출 (CORS 허용 시)
        const response = await fetch('https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=' + apiKey, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                contents: [{
                    parts: [{
                        text: `VC 파트너로서 ${companyName}의 Investment Thesis Memo 작성:
                        
다음 문서를 분석해주세요:
${text.substring(0, 30000)}

# Executive Summary
## 1. 투자 개요  
## 2. 기업 현황
## 3. 시장 분석
## 4. 사업 분석
## 5. 투자적합성과 임팩트
## 6. 종합결론`
                    }]
                }],
                generationConfig: {
                    temperature: 0.7,
                    topK: 40,
                    topP: 0.95,
                    maxOutputTokens: 8192,
                }
            })
        });

        const result = await response.json();
        return result.candidates[0].content.parts[0].text;
    }
}