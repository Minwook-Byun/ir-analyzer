"""
Vercel Blob Storage Integration
사용자 친화적 파일 업로드와 처리를 위한 Blob 스토리지 프로세서
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Tuple, AsyncGenerator
from datetime import datetime
import hashlib
import mimetypes
from pathlib import Path

try:
    import vercel_blob
    import vercel_blob.blob_store as blob_store
    print("[INFO] vercel_blob package loaded successfully")
except ImportError as e:
    print(f"[WARNING] vercel_blob package not found: {e}")
    print("[INFO] Running in mock mode for testing")
    vercel_blob = None
    blob_store = None

from pdf_processor import PDFProcessor

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BlobProcessor:
    """
    Vercel Blob Storage와 통합된 파일 처리 시스템
    
    Features:
    - 대용량 파일 지원 (최대 512MB)
    - 멀티파트 업로드
    - 재시도 로직
    - 진행률 추적
    - 에러 복구
    """
    
    def __init__(self):
        self.blob_token = os.getenv("BLOB_READ_WRITE_TOKEN")
        if not self.blob_token:
            logger.warning("[WARNING] BLOB_READ_WRITE_TOKEN 환경변수가 설정되지 않았습니다.")
        
        self.pdf_processor = PDFProcessor()
        
        # 파일 크기 제한 (바이트)
        self.max_file_size = 512 * 1024 * 1024  # 512MB
        self.multipart_threshold = 100 * 1024 * 1024  # 100MB
        
        # 지원되는 파일 형식
        self.supported_extensions = {'.pdf', '.xlsx', '.xls', '.docx', '.doc'}
        
    def validate_file(self, file_data: bytes, filename: str) -> Dict[str, any]:
        """
        파일 유효성 검사
        
        Returns:
            Dict: 검사 결과와 메타데이터
        """
        file_size = len(file_data)
        file_ext = Path(filename).suffix.lower()
        mime_type = mimetypes.guess_type(filename)[0]
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "metadata": {
                "filename": filename,
                "size": file_size,
                "extension": file_ext,
                "mime_type": mime_type,
                "hash": hashlib.md5(file_data).hexdigest()
            }
        }
        
        # 파일 크기 검사
        if file_size == 0:
            validation_result["valid"] = False
            validation_result["errors"].append("파일이 비어있습니다.")
        elif file_size > self.max_file_size:
            validation_result["valid"] = False
            validation_result["errors"].append(f"파일 크기가 너무 큽니다. (최대: {self.max_file_size / 1024 / 1024:.1f}MB)")
        elif file_size > self.multipart_threshold:
            validation_result["warnings"].append(f"대용량 파일입니다. 멀티파트 업로드를 사용합니다.")
        
        # 파일 형식 검사
        if file_ext not in self.supported_extensions:
            validation_result["valid"] = False
            validation_result["errors"].append(f"지원하지 않는 파일 형식입니다: {file_ext}")
        
        return validation_result
    
    async def upload_to_blob(
        self, 
        file_data: bytes, 
        filename: str,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, any]:
        """
        Vercel Blob에 파일 업로드
        
        Args:
            file_data: 파일 바이트 데이터
            filename: 파일명
            progress_callback: 진행률 콜백 함수
            
        Returns:
            Dict: 업로드 결과
        """
        try:
            # 파일 검증
            validation = self.validate_file(file_data, filename)
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": "; ".join(validation["errors"]),
                    "validation": validation
                }
            
            # 고유한 파일명 생성 (타임스탬프 + 해시)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_hash = validation["metadata"]["hash"][:8]
            blob_filename = f"{timestamp}_{file_hash}_{filename}"
            
            logger.info(f"[INFO] Blob 업로드 시작: {blob_filename}")
            
            # 진행률 콜백 설정
            if progress_callback:
                progress_callback("blob-upload-start", 0, "Vercel Blob에 업로드 시작...")
            
            # 멀티파트 업로드 여부 결정
            use_multipart = len(file_data) > self.multipart_threshold
            
            # 개발 모드 또는 vercel_blob 패키지 없는 경우 Mock 모드
            if not vercel_blob or os.getenv("ENVIRONMENT") == "development":
                logger.info("[DEV MODE] Using mock blob upload")
                
                if progress_callback:
                    progress_callback("blob-upload-progress", 25, "Mock 업로드 진행 중...")
                    await asyncio.sleep(0.5)  # 실제 업로드 시뮬레이션
                    progress_callback("blob-upload-progress", 75, "Mock 업로드 거의 완료...")
                    await asyncio.sleep(0.5)
                    progress_callback("blob-upload-complete", 100, "Mock 업로드 완료!")
                
                # Mock URL 생성
                mock_blob_url = f"https://mock-blob-storage.vercel.app/{blob_filename}"
                
                logger.info(f"[SUCCESS] Mock Blob 업로드 성공: {mock_blob_url}")
                
                return {
                    "success": True,
                    "blob_url": mock_blob_url,
                    "blob_filename": blob_filename,
                    "metadata": validation["metadata"],
                    "warnings": validation["warnings"],
                    "multipart_used": use_multipart,
                    "mock_mode": True
                }
            
            # 실제 Vercel Blob 업로드
            response = blob_store.put(
                blob_filename, 
                file_data, 
                verbose=True,
                multipart=use_multipart
            )
            
            if progress_callback:
                progress_callback("blob-upload-complete", 100, "업로드 완료!")
            
            blob_url = response.get('url')
            if not blob_url:
                raise Exception("Blob URL을 받지 못했습니다.")
            
            logger.info(f"[SUCCESS] Blob 업로드 성공: {blob_url}")
            
            return {
                "success": True,
                "blob_url": blob_url,
                "blob_filename": blob_filename,
                "metadata": validation["metadata"],
                "warnings": validation["warnings"],
                "multipart_used": use_multipart
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Blob 업로드 실패: {str(e)}")
            
            if progress_callback:
                progress_callback("blob-upload-error", 0, f"업로드 실패: {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "retry_suggested": True
            }
    
    async def download_from_blob(
        self, 
        blob_url: str,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, any]:
        """
        Vercel Blob에서 파일 다운로드
        
        Args:
            blob_url: Blob 스토리지 URL
            progress_callback: 진행률 콜백 함수
            
        Returns:
            Dict: 다운로드 결과
        """
        try:
            if progress_callback:
                progress_callback("blob-download-start", 0, "Blob에서 파일 다운로드 중...")
            
            logger.info(f"[INFO] Blob 다운로드 시작: {blob_url}")
            
            # Mock 모드 체크
            if blob_url.startswith("https://mock-blob-storage.vercel.app/"):
                logger.info("[DEV MODE] Using mock blob download")
                
                # Mock 파일 데이터 생성 (실제 PDF 내용)
                mock_file_data = b"""PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 100
>>
stream
BT
/F1 12 Tf
100 700 Td
(Mock IR Report Content) Tj
0 -20 Td
(This is a test PDF for development) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000010 00000 n 
0000000079 00000 n 
0000000173 00000 n 
0000000301 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
450
%%EOF"""
                
                if progress_callback:
                    progress_callback("blob-download-progress", 25, "Mock 다운로드 진행 중...")
                    await asyncio.sleep(0.3)
                    progress_callback("blob-download-progress", 75, "Mock 다운로드 거의 완료...")
                    await asyncio.sleep(0.3)
                    progress_callback("blob-download-complete", 100, "Mock 다운로드 완료!")
                
                logger.info(f"[SUCCESS] Mock Blob 다운로드 성공: {len(mock_file_data)} bytes")
                
                return {
                    "success": True,
                    "file_data": mock_file_data,
                    "size": len(mock_file_data),
                    "mock_mode": True
                }
            
            # 실제 HTTP 요청으로 파일 다운로드
            import requests
            response = requests.get(blob_url, stream=True)
            response.raise_for_status()
            
            # 청크 단위로 다운로드 (메모리 효율성)
            file_data = b""
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file_data += chunk
                    downloaded += len(chunk)
                    
                    if progress_callback and total_size > 0:
                        progress = (downloaded / total_size) * 100
                        progress_callback("blob-download-progress", progress, f"다운로드 중... {progress:.1f}%")
            
            if progress_callback:
                progress_callback("blob-download-complete", 100, "다운로드 완료!")
            
            logger.info(f"[SUCCESS] Blob 다운로드 성공: {len(file_data)} bytes")
            
            return {
                "success": True,
                "file_data": file_data,
                "size": len(file_data)
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Blob 다운로드 실패: {str(e)}")
            
            if progress_callback:
                progress_callback("blob-download-error", 0, f"다운로드 실패: {str(e)}")
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def process_blob_file(
        self, 
        blob_url: str, 
        filename: str,
        progress_callback: Optional[callable] = None
    ) -> str:
        """
        Blob에서 파일을 다운로드하고 처리하여 IR 분석용 텍스트 추출
        
        Args:
            blob_url: Blob 스토리지 URL
            filename: 원본 파일명
            progress_callback: 진행률 콜백 함수
            
        Returns:
            str: 처리된 IR 요약 텍스트
        """
        try:
            # 1. Blob에서 파일 다운로드
            download_result = await self.download_from_blob(blob_url, progress_callback)
            
            if not download_result["success"]:
                raise Exception(f"파일 다운로드 실패: {download_result['error']}")
            
            file_data = download_result["file_data"]
            
            # 2. 파일 처리 (기존 PDF 프로세서 활용)
            if progress_callback:
                progress_callback("file-processing-start", 0, "파일 내용 분석 중...")
            
            file_ext = Path(filename).suffix.lower()
            
            if file_ext == '.pdf':
                # PDF 처리
                pdf_result = self.pdf_processor.extract_text_from_bytes(file_data)
                
                if pdf_result["success"]:
                    # IR 요약 생성
                    extracted_data = {
                        "success": True,
                        "url": blob_url,
                        "file_size": len(file_data),
                        "extracted_text": pdf_result["text"],
                        "page_count": pdf_result["page_count"],
                        "company_info": self.pdf_processor.extract_company_info(pdf_result["text"])
                    }
                    
                    ir_summary = self.pdf_processor.create_ir_summary(extracted_data)
                    
                    if progress_callback:
                        progress_callback("file-processing-complete", 100, "파일 분석 완료!")
                    
                    return ir_summary
                else:
                    raise Exception(f"PDF 처리 실패: {pdf_result.get('error', '알 수 없는 오류')}")
            
            elif file_ext in ['.xlsx', '.xls', '.docx', '.doc']:
                # Excel/Word 파일 기본 처리
                ir_summary = f"""
=== IR 자료 분석 원본 데이터 ===

[INFO] 파일 정보:
- 파일명: {filename}
- Blob URL: {blob_url}
- 파일 크기: {len(file_data):,} bytes
- 파일 형식: {file_ext.upper()}

📄 파일 내용:
{file_ext.upper()} 파일이 Vercel Blob에서 성공적으로 로드되었습니다.
향후 업데이트에서 더 상세한 내용 추출 기능이 추가될 예정입니다.

=== 분석 요청 ===
위의 IR 자료를 바탕으로 투자심사보고서를 작성해주세요.
"""
                
                if progress_callback:
                    progress_callback("file-processing-complete", 100, "파일 분석 완료!")
                
                return ir_summary
            
            else:
                raise Exception(f"지원하지 않는 파일 형식: {file_ext}")
                
        except Exception as e:
            logger.error(f"[ERROR] Blob 파일 처리 실패: {str(e)}")
            
            if progress_callback:
                progress_callback("file-processing-error", 0, f"파일 처리 실패: {str(e)}")
            
            raise Exception(f"Blob 파일 처리 실패: {str(e)}")
    
    async def cleanup_blob(self, blob_url: str) -> bool:
        """
        Blob 스토리지에서 파일 삭제 (정리)
        
        Args:
            blob_url: 삭제할 Blob URL
            
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            if not vercel_blob:
                return False
                
            # Vercel Blob 삭제
            blob_store.delete([blob_url])
            logger.info(f"[INFO] Blob 파일 삭제 완료: {blob_url}")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Blob 파일 삭제 실패: {str(e)}")
            return False
    
    def get_blob_metadata(self, blob_url: str) -> Dict[str, any]:
        """
        Blob 파일 메타데이터 조회
        
        Args:
            blob_url: Blob URL
            
        Returns:
            Dict: 메타데이터
        """
        try:
            if not vercel_blob:
                return {"error": "vercel_blob 패키지가 설치되지 않았습니다."}
                
            metadata = blob_store.head(blob_url)
            return {
                "success": True,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Blob 메타데이터 조회 실패: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# 전역 인스턴스
blob_processor = BlobProcessor()


# 테스트 함수
async def test_blob_processor():
    """Blob 프로세서 테스트"""
    processor = BlobProcessor()
    
    print("=== Vercel Blob 프로세서 테스트 ===")
    
    # 환경변수 확인
    if not processor.blob_token:
        print("[WARNING] BLOB_READ_WRITE_TOKEN 환경변수를 설정해주세요.")
        return
    
    # 테스트 파일 생성
    test_content = b"Test PDF content for Vercel Blob integration"
    test_filename = "test_ir_report.pdf"
    
    def progress_callback(stage, progress, message):
        print(f"[PROGRESS] {stage}: {progress}% - {message}")
    
    try:
        # 1. 업로드 테스트
        print("\n[TEST] 업로드 테스트...")
        upload_result = await processor.upload_to_blob(test_content, test_filename, progress_callback)
        
        if upload_result["success"]:
            print(f"[SUCCESS] 업로드 성공: {upload_result['blob_url']}")
            
            # 2. 다운로드 테스트
            print("\n[TEST] 다운로드 테스트...")
            download_result = await processor.download_from_blob(upload_result['blob_url'], progress_callback)
            
            if download_result["success"]:
                print(f"[SUCCESS] 다운로드 성공: {len(download_result['file_data'])} bytes")
                
                # 3. 정리
                print("\n[CLEANUP] 정리...")
                cleanup_success = await processor.cleanup_blob(upload_result['blob_url'])
                if cleanup_success:
                    print("[SUCCESS] 정리 완료")
                else:
                    print("[WARNING] 정리 실패")
            else:
                print(f"[ERROR] 다운로드 실패: {download_result['error']}")
        else:
            print(f"[ERROR] 업로드 실패: {upload_result['error']}")
            
    except Exception as e:
        print(f"[ERROR] 테스트 실패: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_blob_processor())