"""
Storage Service Abstraction Layer

Provides unified interface for file storage operations supporting both
S3 (production) and local filesystem (development) backends.
"""
import os
import hashlib
import uuid
from typing import Tuple, Optional
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

import boto3
from botocore.exceptions import ClientError, BotoCoreError
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("services.storage")


class StorageServiceInterface(ABC):
    """Abstract base class for storage services"""
    
    @abstractmethod
    def upload_file(
        self,
        file_bytes: bytes,
        storage_path: str,
        content_type: str
    ) -> Tuple[str, str]:
        """
        Upload file to storage.
        
        Args:
            file_bytes: File content as bytes
            storage_path: S3/local path where file should be stored
            content_type: MIME type of the file
            
        Returns:
            Tuple of (storage_path, checksum)
        """
        pass
    
    @abstractmethod
    def download_file(self, storage_path: str) -> bytes:
        """
        Download file from storage.
        
        Args:
            storage_path: S3/local path of the file
            
        Returns:
            File content as bytes
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        pass
    
    @abstractmethod
    def delete_file(self, storage_path: str) -> bool:
        """
        Delete file from storage.
        
        Args:
            storage_path: S3/local path of the file
            
        Returns:
            True if deleted successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def file_exists(self, storage_path: str) -> bool:
        """
        Check if file exists in storage.
        
        Args:
            storage_path: S3/local path of the file
            
        Returns:
            True if file exists, False otherwise
        """
        pass
    
    @abstractmethod
    def generate_presigned_url(
        self,
        storage_path: str,
        expiration: int = 3600
    ) -> Optional[str]:
        """
        Generate presigned URL for direct access (S3 only).
        
        Args:
            storage_path: S3/local path of the file
            expiration: URL expiration time in seconds
            
        Returns:
            Presigned URL string or None if not supported
        """
        pass
    
    @staticmethod
    def calculate_checksum(file_bytes: bytes) -> str:
        """Calculate SHA-256 checksum of file bytes"""
        return hashlib.sha256(file_bytes).hexdigest()


class S3StorageService(StorageServiceInterface):
    """S3 storage service implementation"""
    
    def __init__(self):
        """Initialize S3 client"""
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
                endpoint_url=settings.AWS_S3_ENDPOINT_URL if settings.AWS_S3_ENDPOINT_URL else None
            )
            self.bucket_name = settings.AWS_S3_BUCKET_NAME
            
            if not self.bucket_name:
                raise ValueError("AWS_S3_BUCKET_NAME is not configured")
                
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"S3 storage initialization failed: {str(e)}"
            )
    
    def upload_file(
        self,
        file_bytes: bytes,
        storage_path: str,
        content_type: str
    ) -> Tuple[str, str]:
        """Upload file to S3"""
        try:
            # Ensure path doesn't start with /
            storage_path = storage_path.lstrip('/')
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=storage_path,
                Body=file_bytes,
                ContentType=content_type
            )
            
            checksum = self.calculate_checksum(file_bytes)
            logger.info(f"File uploaded to S3: {storage_path}")
            
            return storage_path, checksum
            
        except ClientError as e:
            logger.error(f"S3 upload error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file to S3: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error during S3 upload: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"File upload failed: {str(e)}"
            )
    
    def download_file(self, storage_path: str) -> bytes:
        """Download file from S3"""
        try:
            storage_path = storage_path.lstrip('/')
            
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=storage_path
            )
            
            file_bytes = response['Body'].read()
            logger.info(f"File downloaded from S3: {storage_path}")
            
            return file_bytes
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'NoSuchKey':
                logger.warning(f"File not found in S3: {storage_path}")
                raise FileNotFoundError(f"File not found: {storage_path}")
            else:
                logger.error(f"S3 download error: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to download file from S3: {str(e)}"
                )
        except Exception as e:
            logger.error(f"Unexpected error during S3 download: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"File download failed: {str(e)}"
            )
    
    def delete_file(self, storage_path: str) -> bool:
        """Delete file from S3"""
        try:
            storage_path = storage_path.lstrip('/')
            
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=storage_path
            )
            
            logger.info(f"File deleted from S3: {storage_path}")
            return True
            
        except ClientError as e:
            logger.error(f"S3 delete error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during S3 delete: {str(e)}")
            return False
    
    def file_exists(self, storage_path: str) -> bool:
        """Check if file exists in S3"""
        try:
            storage_path = storage_path.lstrip('/')
            
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=storage_path
            )
            return True
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == '404':
                return False
            logger.error(f"Error checking file existence: {str(e)}")
            return False
    
    def generate_presigned_url(
        self,
        storage_path: str,
        expiration: int = 3600
    ) -> Optional[str]:
        """Generate presigned URL for direct S3 access"""
        try:
            storage_path = storage_path.lstrip('/')
            
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': storage_path
                },
                ExpiresIn=expiration
            )
            
            return url
            
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            return None


class LocalStorageService(StorageServiceInterface):
    """Local filesystem storage service (for development)"""
    
    def __init__(self, base_dir: str = "storage"):
        """Initialize local storage service"""
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
    
    def upload_file(
        self,
        file_bytes: bytes,
        storage_path: str,
        content_type: str
    ) -> Tuple[str, str]:
        """Upload file to local filesystem"""
        try:
            # Create full path
            full_path = os.path.join(self.base_dir, storage_path)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Write file
            with open(full_path, "wb") as f:
                f.write(file_bytes)
            
            checksum = self.calculate_checksum(file_bytes)
            logger.info(f"File uploaded to local storage: {full_path}")
            
            return storage_path, checksum
            
        except Exception as e:
            logger.error(f"Local storage upload error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file: {str(e)}"
            )
    
    def download_file(self, storage_path: str) -> bytes:
        """Download file from local filesystem"""
        try:
            full_path = os.path.join(self.base_dir, storage_path)
            
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"File not found: {storage_path}")
            
            with open(full_path, "rb") as f:
                file_bytes = f.read()
            
            logger.info(f"File downloaded from local storage: {full_path}")
            return file_bytes
            
        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Local storage download error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to download file: {str(e)}"
            )
    
    def delete_file(self, storage_path: str) -> bool:
        """Delete file from local filesystem"""
        try:
            full_path = os.path.join(self.base_dir, storage_path)
            
            if os.path.exists(full_path):
                os.remove(full_path)
                logger.info(f"File deleted from local storage: {full_path}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Local storage delete error: {str(e)}")
            return False
    
    def file_exists(self, storage_path: str) -> bool:
        """Check if file exists in local filesystem"""
        full_path = os.path.join(self.base_dir, storage_path)
        return os.path.exists(full_path)
    
    def generate_presigned_url(
        self,
        storage_path: str,
        expiration: int = 3600
    ) -> Optional[str]:
        """Presigned URLs not supported for local storage"""
        return None


def get_storage_service() -> StorageServiceInterface:
    """
    Factory function to get appropriate storage service based on configuration.
    
    Returns:
        StorageServiceInterface instance (S3StorageService or LocalStorageService)
    """
    storage_type = settings.STORAGE_TYPE.lower()
    
    if storage_type == "s3":
        return S3StorageService()
    elif storage_type == "local":
        return LocalStorageService()
    else:
        logger.warning(f"Unknown storage type: {storage_type}, defaulting to local")
        return LocalStorageService()
