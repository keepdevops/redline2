#!/usr/bin/env python3
"""
REDLINE S3/R2 Operations
Handles cloud storage operations for AWS S3 and Cloudflare R2.
"""

import os
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Cloud storage providers
try:
    import boto3
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False
    boto3 = None


class S3Operations:
    """Handles S3/R2 cloud storage operations."""
    
    def __init__(self, s3_config: Dict):
        """
        Initialize S3 operations.
        
        Args:
            s3_config: S3 configuration dict with bucket, access_key, secret_key, region, endpoint_url
        """
        if not S3_AVAILABLE:
            raise ImportError("boto3 is required for S3 operations. Install with: pip install boto3")
        
        self.s3_config = s3_config
        self.s3_client = None
        self.s3_bucket = None
        self._init_s3()
    
    def _init_s3(self):
        """Initialize S3 client (supports AWS S3 and Cloudflare R2)"""
        try:
            # Get endpoint URL for R2 (Cloudflare R2 uses custom endpoint)
            endpoint_url = os.environ.get('S3_ENDPOINT_URL') or self.s3_config.get('endpoint_url')
            
            # Build client config
            client_config = {
                'aws_access_key_id': self.s3_config.get('access_key'),
                'aws_secret_access_key': self.s3_config.get('secret_key'),
                'region_name': self.s3_config.get('region', 'us-east-1')
            }
            
            # Add endpoint URL if provided (for R2 or other S3-compatible services)
            if endpoint_url:
                client_config['endpoint_url'] = endpoint_url
                logger.info(f"Using custom S3 endpoint: {endpoint_url}")
            
            self.s3_client = boto3.client('s3', **client_config)
            self.s3_bucket = self.s3_config.get('bucket')
            
            # Determine storage type for logging
            storage_type = "R2" if endpoint_url and 'r2.cloudflarestorage.com' in endpoint_url else "S3"
            logger.info(f"{storage_type} storage initialized: bucket={self.s3_bucket}")
        except Exception as e:
            logger.error(f"Failed to initialize S3/R2: {str(e)}")
            raise
    
    def get_s3_prefix(self, license_key: str) -> str:
        """Get S3 prefix for a user"""
        import hashlib
        key_hash = hashlib.sha256(license_key.encode()).hexdigest()[:16]
        return f"users/{key_hash}/"
    
    def upload_file(self, license_key: str, filename: str, file_data: bytes) -> Optional[str]:
        """
        Upload a file to S3/R2.
        
        Args:
            license_key: User license key
            filename: Name of the file
            file_data: File data as bytes
            
        Returns:
            S3 key if successful, None otherwise
        """
        try:
            s3_key = f"{self.get_s3_prefix(license_key)}files/{filename}"
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=s3_key,
                Body=file_data
            )
            logger.debug(f"Uploaded file to S3: {s3_key}")
            return s3_key
        except Exception as e:
            logger.error(f"Error uploading file to S3: {str(e)}")
            return None
    
    def download_file(self, license_key: str, filename: str) -> Optional[bytes]:
        """
        Download a file from S3/R2.
        
        Args:
            license_key: User license key
            filename: Name of the file
            
        Returns:
            File data as bytes if successful, None otherwise
        """
        try:
            s3_key = f"{self.get_s3_prefix(license_key)}files/{filename}"
            response = self.s3_client.get_object(
                Bucket=self.s3_bucket,
                Key=s3_key
            )
            return response['Body'].read()
        except Exception as e:
            logger.error(f"Error downloading file from S3: {str(e)}")
            return None
    
    def delete_file(self, license_key: str, filename: str) -> bool:
        """
        Delete a file from S3/R2.
        
        Args:
            license_key: User license key
            filename: Name of the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            s3_key = f"{self.get_s3_prefix(license_key)}files/{filename}"
            self.s3_client.delete_object(
                Bucket=self.s3_bucket,
                Key=s3_key
            )
            logger.debug(f"Deleted file from S3: {s3_key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file from S3: {str(e)}")
            return False
    
    def list_files(self, license_key: str, prefix: str = None) -> list:
        """
        List files in S3/R2 for a user.
        
        Args:
            license_key: User license key
            prefix: Optional prefix to filter files
            
        Returns:
            List of file keys
        """
        try:
            s3_prefix = self.get_s3_prefix(license_key)
            if prefix:
                s3_prefix = f"{s3_prefix}{prefix}"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.s3_bucket,
                Prefix=s3_prefix
            )
            
            if 'Contents' not in response:
                return []
            
            return [obj['Key'] for obj in response['Contents']]
        except Exception as e:
            logger.error(f"Error listing files from S3: {str(e)}")
            return []

