/**
 * Vercel Blob Upload Manager - Championship Edition
 * 
 * This module handles secure client-side direct uploads to Vercel Blob
 * with real-time progress tracking and Korean UX optimization
 */

class VercelBlobUploader {
    constructor() {
        this.config = null;
        this.currentUploads = new Map(); // Track multiple concurrent uploads
        this.maxConcurrentUploads = 3;
        this.uploadQueue = [];
        
        // Initialize configuration
        this.initializeConfig();
    }

    /**
     * Initialize client configuration from server
     */
    async initializeConfig() {
        try {
            const response = await fetch('/api/blob/client-config');
            const result = await response.json();
            
            if (result.success) {
                this.config = result.data;
                console.log('🚀 Vercel Blob 설정 초기화 완료:', this.config);
            } else {
                throw new Error('Failed to load blob configuration');
            }
        } catch (error) {
            console.error('❌ Blob 설정 로드 실패:', error);
            this.fallbackConfig();
        }
    }

    /**
     * Fallback configuration if server config fails
     */
    fallbackConfig() {
        this.config = {
            api_endpoint: '/api/blob/upload-token',
            chunk_size: 1024 * 1024, // 1MB
            max_file_size: 50 * 1024 * 1024, // 50MB
            allowed_extensions: ['.pdf', '.xlsx', '.xls', '.docx', '.doc'],
            timeout: 300000, // 5 minutes
            retry_attempts: 3
        };
    }

    /**
     * Validate file before upload
     */
    validateFile(file, companyName) {
        const errors = [];

        // File size validation
        if (file.size > this.config.max_file_size) {
            errors.push(`파일 크기가 너무 큽니다: ${this.formatFileSize(file.size)}. 최대 ${this.formatFileSize(this.config.max_file_size)}`);
        }

        // File type validation
        const fileExtension = this.getFileExtension(file.name);
        if (!this.config.allowed_extensions.includes(fileExtension)) {
            errors.push(`지원하지 않는 파일 형식: ${fileExtension}. 허용된 형식: ${this.config.allowed_extensions.join(', ')}`);
        }

        // Company name validation
        if (!companyName || companyName.trim().length < 2) {
            errors.push('회사명은 최소 2자 이상 입력해야 합니다.');
        }

        return {
            valid: errors.length === 0,
            errors: errors
        };
    }

    /**
     * Generate upload token from server
     */
    async generateUploadToken(file, companyName) {
        const formData = new FormData();
        formData.append('filename', file.name);
        formData.append('file_size', file.size.toString());
        formData.append('company_name', companyName);

        const response = await fetch(this.config.api_endpoint, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (!result.success) {
            throw new Error(result.message || 'Failed to generate upload token');
        }

        return result.data;
    }

    /**
     * Upload file directly to Vercel Blob
     */
    async uploadToBlob(file, uploadData, progressCallback) {
        const uploadId = this.generateUploadId();
        
        try {
            // Start progress tracking
            this.startProgressTracking(uploadId, uploadData.upload_token, progressCallback);

            // For demo purposes, simulate upload to Vercel Blob
            // In production, you would use the actual Vercel Blob SDK
            const blobUrl = await this.simulateVercelBlobUpload(file, uploadData, progressCallback);

            // Complete upload
            await this.completeUpload(uploadData.upload_token, blobUrl, file);

            return {
                success: true,
                blobUrl: blobUrl,
                uploadId: uploadId
            };

        } catch (error) {
            console.error('❌ Blob 업로드 실패:', error);
            throw error;
        } finally {
            this.currentUploads.delete(uploadId);
        }
    }

    /**
     * Simulate Vercel Blob upload (replace with actual Vercel Blob SDK)
     */
    async simulateVercelBlobUpload(file, uploadData, progressCallback) {
        const chunks = Math.ceil(file.size / this.config.chunk_size);
        let uploadedChunks = 0;

        // Simulate chunked upload
        for (let i = 0; i < chunks; i++) {
            await this.delay(100 + Math.random() * 200); // Simulate network delay
            
            uploadedChunks++;
            const progress = (uploadedChunks / chunks) * 100;
            
            if (progressCallback) {
                progressCallback({
                    progress: progress,
                    uploaded: uploadedChunks * this.config.chunk_size,
                    total: file.size,
                    status: 'uploading'
                });
            }
        }

        // Generate mock blob URL
        const timestamp = Date.now();
        const hash = this.generateFileHash(file.name + timestamp);
        return `https://blob.vercel-storage.com/ir-files/${hash}-${uploadData.secure_filename}`;
    }

    /**
     * Start real-time progress tracking
     */
    startProgressTracking(uploadId, token, progressCallback) {
        this.currentUploads.set(uploadId, {
            token: token,
            startTime: Date.now(),
            progressCallback: progressCallback
        });
    }

    /**
     * Complete upload and notify server
     */
    async completeUpload(token, blobUrl, file) {
        const formData = new FormData();
        formData.append('token', token);
        formData.append('blob_url', blobUrl);
        formData.append('file_hash', this.generateFileHash(file.name));

        const response = await fetch('/api/blob/upload-complete', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (!result.success) {
            throw new Error(result.message || 'Failed to complete upload');
        }

        return result.data;
    }

    /**
     * Upload multiple files with queue management
     */
    async uploadFiles(files, companyName, progressCallback) {
        const results = [];
        const errors = [];

        // Validate all files first
        for (const file of files) {
            const validation = this.validateFile(file, companyName);
            if (!validation.valid) {
                errors.push({
                    filename: file.name,
                    errors: validation.errors
                });
                continue;
            }
        }

        if (errors.length > 0) {
            throw new Error(`파일 검증 실패:\n${errors.map(e => `${e.filename}: ${e.errors.join(', ')}`).join('\n')}`);
        }

        // Process uploads with concurrency limit
        const uploadPromises = Array.from(files).map((file, index) => 
            this.queueUpload(file, companyName, (progress) => {
                if (progressCallback) {
                    progressCallback({
                        fileIndex: index,
                        filename: file.name,
                        ...progress
                    });
                }
            })
        );

        try {
            const uploadResults = await Promise.all(uploadPromises);
            return uploadResults;
        } catch (error) {
            console.error('❌ 다중 파일 업로드 실패:', error);
            throw error;
        }
    }

    /**
     * Queue upload with concurrency control
     */
    async queueUpload(file, companyName, progressCallback) {
        return new Promise((resolve, reject) => {
            this.uploadQueue.push({
                file,
                companyName,
                progressCallback,
                resolve,
                reject
            });
            
            this.processUploadQueue();
        });
    }

    /**
     * Process upload queue with concurrency limit
     */
    async processUploadQueue() {
        if (this.currentUploads.size >= this.maxConcurrentUploads || this.uploadQueue.length === 0) {
            return;
        }

        const uploadTask = this.uploadQueue.shift();
        
        try {
            // Generate upload token
            const uploadData = await this.generateUploadToken(uploadTask.file, uploadTask.companyName);
            
            // Upload to blob
            const result = await this.uploadToBlob(uploadTask.file, uploadData, uploadTask.progressCallback);
            
            uploadTask.resolve(result);
        } catch (error) {
            uploadTask.reject(error);
        }

        // Continue processing queue
        setTimeout(() => this.processUploadQueue(), 100);
    }

    /**
     * Utility functions
     */
    generateUploadId() {
        return 'upload_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    getFileExtension(filename) {
        return filename.toLowerCase().substring(filename.lastIndexOf('.'));
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    generateFileHash(input) {
        let hash = 0;
        for (let i = 0; i < input.length; i++) {
            const char = input.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        return Math.abs(hash).toString(36);
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Get current upload statistics
     */
    getUploadStats() {
        return {
            activeUploads: this.currentUploads.size,
            queuedUploads: this.uploadQueue.length,
            maxConcurrent: this.maxConcurrentUploads
        };
    }
}

// Global instance
window.blobUploader = new VercelBlobUploader();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VercelBlobUploader;
}