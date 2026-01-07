#!/usr/bin/env python3
"""
S3/Wasabi Storage Manager for REDLINE
Handles file uploads, downloads, and presigned URLs
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import mimetypes

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    boto3 = None
    ClientError = Exception

logger = logging.getLogger(__name__)


class S3Manager:
    """Manage S3/Wasabi file operations for REDLINE"""

    def __init__(self):
        """Initialize S3 client with credentials from environment"""
        if not BOTO3_AVAILABLE:
            logger.warning("boto3 not available. Install with: pip install boto3")
            self.s3_client = None
            self.bucket = None
            return

        # Get configuration from environment (supports both S3 and R2 naming)
        self.bucket = os.environ.get('R2_BUCKET_NAME') or os.environ.get('S3_BUCKET')
        self.endpoint_url = os.environ.get('R2_ENDPOINT_URL') or os.environ.get('S3_ENDPOINT_URL')
        access_key = os.environ.get('R2_ACCESS_KEY_ID') or os.environ.get('S3_ACCESS_KEY')
        secret_key = os.environ.get('R2_SECRET_ACCESS_KEY') or os.environ.get('S3_SECRET_KEY')
        region = os.environ.get('S3_REGION', 'us-east-1')

        if not all([self.bucket, access_key, secret_key]):
            logger.warning("S3 credentials not configured. Set S3_BUCKET, S3_ACCESS_KEY, S3_SECRET_KEY")
            self.s3_client = None
            return

        try:
            # Initialize S3 client
            self.s3_client = boto3.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            logger.info(f"S3 Manager initialized successfully (bucket: {self.bucket})")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {str(e)}")
            self.s3_client = None

    def is_available(self) -> bool:
        """Check if S3 client is available and configured"""
        return self.s3_client is not None

    # ========================================================================
    # PATH GENERATION
    # ========================================================================

    def get_user_path(self, user_id: str, folder: str = 'raw') -> str:
        """
        Get S3 path for user folder

        Args:
            user_id: Supabase user ID (UUID)
            folder: Folder name (raw, processed, cleaned, etc.)

        Returns:
            S3 path (e.g., "users/uuid/raw/")
        """
        return f"users/{user_id}/{folder}/"

    def get_file_path(self, user_id: str, filename: str, folder: str = 'raw') -> str:
        """
        Generate full S3 path for a file

        Args:
            user_id: Supabase user ID
            filename: Name of the file
            folder: Folder name (raw, processed, cleaned, etc.)

        Returns:
            Full S3 path (e.g., "users/uuid/raw/stocks.csv")
        """
        folder_path = self.get_user_path(user_id, folder)
        return f"{folder_path}{filename}"

    def get_s3_uri(self, s3_key: str) -> str:
        """
        Convert S3 key to S3 URI (for DuckDB)

        Args:
            s3_key: S3 object key

        Returns:
            S3 URI (e.g., "s3://bucket/path/to/file")
        """
        return f"s3://{self.bucket}/{s3_key}"

    # ========================================================================
    # FILE UPLOAD
    # ========================================================================

    def upload_file(self, local_path: str, s3_key: str,
                   metadata: Optional[Dict[str, str]] = None) -> Optional[str]:
        """
        Upload file to S3

        Args:
            local_path: Path to local file
            s3_key: S3 object key (destination path)
            metadata: Optional metadata dict

        Returns:
            S3 URI if successful, None otherwise
        """
        if not self.s3_client:
            logger.error("S3 client not available")
            return None

        try:
            # Determine content type
            content_type, _ = mimetypes.guess_type(local_path)
            if not content_type:
                content_type = 'application/octet-stream'

            # Prepare extra args
            extra_args = {'ContentType': content_type}
            if metadata:
                extra_args['Metadata'] = metadata

            # Upload file
            self.s3_client.upload_file(
                local_path,
                self.bucket,
                s3_key,
                ExtraArgs=extra_args
            )

            logger.info(f"Uploaded file to S3: {s3_key}")
            return self.get_s3_uri(s3_key)

        except ClientError as e:
            logger.error(f"Error uploading file to S3: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading file: {str(e)}")
            return None

    def upload_fileobj(self, file_obj, s3_key: str,
                      content_type: str = 'application/octet-stream',
                      metadata: Optional[Dict[str, str]] = None) -> Optional[str]:
        """
        Upload file object to S3 (useful for Flask uploaded files)

        Args:
            file_obj: File-like object
            s3_key: S3 object key (destination path)
            content_type: MIME type
            metadata: Optional metadata dict

        Returns:
            S3 URI if successful, None otherwise
        """
        if not self.s3_client:
            logger.error("S3 client not available")
            return None

        try:
            # Prepare extra args
            extra_args = {'ContentType': content_type}
            if metadata:
                extra_args['Metadata'] = metadata

            # Upload file object
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket,
                s3_key,
                ExtraArgs=extra_args
            )

            logger.info(f"Uploaded file object to S3: {s3_key}")
            return self.get_s3_uri(s3_key)

        except ClientError as e:
            logger.error(f"Error uploading file object to S3: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading file object: {str(e)}")
            return None

    # ========================================================================
    # FILE DOWNLOAD
    # ========================================================================

    def download_file(self, s3_key: str, local_path: str) -> bool:
        """
        Download file from S3

        Args:
            s3_key: S3 object key
            local_path: Local destination path

        Returns:
            True if successful, False otherwise
        """
        if not self.s3_client:
            logger.error("S3 client not available")
            return False

        try:
            # Ensure local directory exists
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            # Download file
            self.s3_client.download_file(self.bucket, s3_key, local_path)

            logger.info(f"Downloaded file from S3: {s3_key} -> {local_path}")
            return True

        except ClientError as e:
            logger.error(f"Error downloading file from S3: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error downloading file: {str(e)}")
            return False

    def generate_presigned_url(self, s3_key: str, expiration: int = 3600,
                              method: str = 'get_object') -> Optional[str]:
        """
        Generate presigned URL for file access

        Args:
            s3_key: S3 object key
            expiration: URL expiration time in seconds (default: 1 hour)
            method: S3 method (get_object for download, put_object for upload)

        Returns:
            Presigned URL or None on failure
        """
        if not self.s3_client:
            logger.error("S3 client not available")
            return None

        try:
            url = self.s3_client.generate_presigned_url(
                method,
                Params={'Bucket': self.bucket, 'Key': s3_key},
                ExpiresIn=expiration
            )

            logger.info(f"Generated presigned URL for {s3_key} (expires in {expiration}s)")
            return url

        except ClientError as e:
            logger.error(f"Error generating presigned URL: {str(e)}")
            return None

    # ========================================================================
    # FILE OPERATIONS
    # ========================================================================

    def file_exists(self, s3_key: str) -> bool:
        """
        Check if file exists in S3

        Args:
            s3_key: S3 object key

        Returns:
            True if file exists, False otherwise
        """
        if not self.s3_client:
            return False

        try:
            self.s3_client.head_object(Bucket=self.bucket, Key=s3_key)
            return True
        except ClientError:
            return False

    def get_file_metadata(self, s3_key: str) -> Optional[Dict[str, Any]]:
        """
        Get file metadata from S3

        Args:
            s3_key: S3 object key

        Returns:
            Metadata dict with size, last_modified, content_type, etc.
        """
        if not self.s3_client:
            return None

        try:
            response = self.s3_client.head_object(Bucket=self.bucket, Key=s3_key)

            return {
                'size': response.get('ContentLength', 0),
                'last_modified': response.get('LastModified'),
                'content_type': response.get('ContentType'),
                'etag': response.get('ETag', '').strip('"'),
                'metadata': response.get('Metadata', {})
            }

        except ClientError as e:
            logger.error(f"Error getting file metadata: {str(e)}")
            return None

    def delete_file(self, s3_key: str) -> bool:
        """
        Delete file from S3

        Args:
            s3_key: S3 object key

        Returns:
            True if successful, False otherwise
        """
        if not self.s3_client:
            return False

        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=s3_key)
            logger.info(f"Deleted file from S3: {s3_key}")
            return True

        except ClientError as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False

    def copy_file(self, source_key: str, dest_key: str) -> bool:
        """
        Copy file within S3 bucket

        Args:
            source_key: Source S3 object key
            dest_key: Destination S3 object key

        Returns:
            True if successful, False otherwise
        """
        if not self.s3_client:
            return False

        try:
            copy_source = {'Bucket': self.bucket, 'Key': source_key}
            self.s3_client.copy_object(
                CopySource=copy_source,
                Bucket=self.bucket,
                Key=dest_key
            )

            logger.info(f"Copied file in S3: {source_key} -> {dest_key}")
            return True

        except ClientError as e:
            logger.error(f"Error copying file: {str(e)}")
            return False

    # ========================================================================
    # FOLDER OPERATIONS
    # ========================================================================

    def list_files(self, prefix: str, max_keys: int = 1000) -> List[Dict[str, Any]]:
        """
        List files in S3 with given prefix

        Args:
            prefix: S3 key prefix (folder path)
            max_keys: Maximum number of files to return

        Returns:
            List of file metadata dicts
        """
        if not self.s3_client:
            return []

        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix,
                MaxKeys=max_keys
            )

            files = []
            for obj in response.get('Contents', []):
                # Skip folder markers (keys ending with /)
                if obj['Key'].endswith('/'):
                    continue

                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'etag': obj.get('ETag', '').strip('"')
                })

            return files

        except ClientError as e:
            logger.error(f"Error listing files: {str(e)}")
            return []

    def delete_folder(self, prefix: str) -> bool:
        """
        Delete all files in folder (with given prefix)

        Args:
            prefix: S3 key prefix (folder path)

        Returns:
            True if successful, False otherwise
        """
        if not self.s3_client:
            return False

        try:
            # List all objects with prefix
            files = self.list_files(prefix, max_keys=10000)

            if not files:
                logger.info(f"No files to delete in {prefix}")
                return True

            # Delete objects in batches of 1000
            objects_to_delete = [{'Key': f['key']} for f in files]

            for i in range(0, len(objects_to_delete), 1000):
                batch = objects_to_delete[i:i+1000]
                self.s3_client.delete_objects(
                    Bucket=self.bucket,
                    Delete={'Objects': batch}
                )

            logger.info(f"Deleted {len(files)} files from {prefix}")
            return True

        except ClientError as e:
            logger.error(f"Error deleting folder: {str(e)}")
            return False

    def create_folder(self, prefix: str) -> bool:
        """
        Create folder marker in S3 (empty object with trailing /)

        Args:
            prefix: Folder path (will add trailing / if missing)

        Returns:
            True if successful, False otherwise
        """
        if not self.s3_client:
            return False

        # Ensure prefix ends with /
        if not prefix.endswith('/'):
            prefix += '/'

        try:
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=prefix,
                Body=b'',
                ContentType='application/x-directory'
            )

            logger.info(f"Created folder: {prefix}")
            return True

        except ClientError as e:
            logger.error(f"Error creating folder: {str(e)}")
            return False

    # ========================================================================
    # USER FOLDER INITIALIZATION
    # ========================================================================

    def initialize_user_folders(self, user_id: str) -> bool:
        """
        Create standard folder structure for new user

        Args:
            user_id: Supabase user ID

        Returns:
            True if successful, False otherwise
        """
        folders = ['raw', 'processed', 'cleaned', 'merged',
                  'analytics', 'aggregated', 'cache', 'exports']

        success = True
        for folder in folders:
            folder_path = self.get_user_path(user_id, folder)
            if not self.create_folder(folder_path):
                success = False

        if success:
            logger.info(f"Initialized folder structure for user {user_id}")

        return success


# Global instance
s3_manager = S3Manager()
