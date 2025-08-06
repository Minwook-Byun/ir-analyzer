"""
Vercel Blob Service - Secure Token Management
Elite implementation for client-side direct uploads
"""
import os
import time
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional
import hashlib

class VercelBlobService:
    """Championship-grade Vercel Blob service with security first approach"""
    
    def __init__(self):
        self.blob_read_write_token = os.getenv('BLOB_READ_WRITE_TOKEN')
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.allowed_extensions = {'.pdf', '.xlsx', '.xls', '.docx', '.doc'}
        
    def generate_upload_token(self, 
                            filename: str, 
                            file_size: int,
                            company_name: str,
                            user_session: Optional[str] = None) -> Dict:
        """
        Generate secure upload token with all validations
        
        Args:
            filename: Original filename
            file_size: File size in bytes
            company_name: Company name for analysis
            user_session: Optional user session ID
            
        Returns:
            Dict containing upload URL and metadata
        """
        
        # Validation 1: File size check
        if file_size > self.max_file_size:
            raise ValueError(f"File too large: {file_size:,} bytes. Maximum: {self.max_file_size:,} bytes")
        
        # Validation 2: File extension check
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in self.allowed_extensions:
            raise ValueError(f"Invalid file type: {file_ext}. Allowed: {', '.join(self.allowed_extensions)}")
        
        # Validation 3: Company name validation
        if not company_name or len(company_name.strip()) < 2:
            raise ValueError("Company name is required (minimum 2 characters)")
        
        # Generate secure filename with timestamp and hash
        timestamp = int(time.time())
        secure_hash = hashlib.sha256(f"{filename}{timestamp}{company_name}".encode()).hexdigest()[:12]
        secure_filename = f"ir-{timestamp}-{secure_hash}-{filename}"
        
        # Create JWT token with metadata
        payload = {
            'filename': secure_filename,
            'original_filename': filename,
            'file_size': file_size,
            'company_name': company_name,
            'user_session': user_session,
            'timestamp': timestamp,
            'exp': datetime.utcnow() + timedelta(minutes=30),  # Token expires in 30 minutes
            'iat': datetime.utcnow(),
            'purpose': 'blob_upload'
        }
        
        upload_token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        
        # Generate upload URL (this would be the actual Vercel Blob URL)
        upload_url = f"https://blob.vercel-storage.com/{secure_filename}"
        
        return {
            'upload_url': upload_url,
            'upload_token': upload_token,
            'secure_filename': secure_filename,
            'expires_at': (datetime.utcnow() + timedelta(minutes=30)).isoformat(),
            'max_file_size': self.max_file_size,
            'allowed_types': list(self.allowed_extensions)
        }
    
    def validate_upload_token(self, token: str) -> Dict:
        """
        Validate upload token and return metadata
        
        Args:
            token: JWT token to validate
            
        Returns:
            Dict containing token metadata
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # Additional validation
            if payload.get('purpose') != 'blob_upload':
                raise ValueError("Invalid token purpose")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise ValueError("Upload token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid upload token")
    
    def get_blob_client_config(self) -> Dict:
        """
        Get client-side configuration for Vercel Blob uploads
        
        Returns:
            Dict containing client configuration
        """
        return {
            'api_endpoint': '/api/blob/upload-token',
            'chunk_size': 1024 * 1024,  # 1MB chunks
            'max_file_size': self.max_file_size,
            'allowed_extensions': list(self.allowed_extensions),
            'timeout': 300000,  # 5 minutes
            'retry_attempts': 3
        }
    
    def calculate_estimated_cost(self, file_size: int) -> Dict:
        """
        Calculate estimated Vercel Blob storage cost
        
        Args:
            file_size: File size in bytes
            
        Returns:
            Dict with cost estimation
        """
        # Vercel Blob pricing (approximate)
        storage_cost_per_gb_month = 0.15  # $0.15 per GB per month
        bandwidth_cost_per_gb = 0.12      # $0.12 per GB bandwidth
        
        file_size_gb = file_size / (1024 ** 3)
        
        # Estimate monthly storage cost (assuming file stays for 1 month)
        storage_cost = file_size_gb * storage_cost_per_gb_month
        
        # Estimate bandwidth cost (download once)
        bandwidth_cost = file_size_gb * bandwidth_cost_per_gb
        
        total_estimated_cost = storage_cost + bandwidth_cost
        
        return {
            'file_size_mb': round(file_size / (1024 ** 2), 2),
            'file_size_gb': round(file_size_gb, 4),
            'storage_cost_monthly': round(storage_cost, 4),
            'bandwidth_cost': round(bandwidth_cost, 4),
            'total_estimated_cost': round(total_estimated_cost, 4),
            'currency': 'USD'
        }
    
    def get_upload_progress_webhook(self) -> str:
        """
        Get webhook URL for upload progress tracking
        
        Returns:
            Webhook URL string
        """
        return '/api/blob/upload-progress'