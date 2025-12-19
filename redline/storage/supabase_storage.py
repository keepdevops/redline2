"""Supabase Storage service"""
import logging
from typing import List, Dict
from uuid import UUID
from redline.auth.supabase_config import supabase_client, supabase_admin

logger = logging.getLogger(__name__)


class SupabaseStorageService:
    """Service for managing files in Supabase Storage"""

    def upload_file(self, user_id: str, filename: str, file_data: bytes, bucket: str = 'user-files') -> str:
        """
        Upload file to Supabase Storage

        Args:
            user_id: User UUID
            filename: Name of the file
            file_data: File contents as bytes
            bucket: Storage bucket name (default: 'user-files')

        Returns:
            Public URL of the uploaded file
        """
        try:
            path = f"{user_id}/files/{filename}"

            result = supabase_client.storage.from_(bucket).upload(
                path=path,
                file=file_data,
                file_options={"content-type": "application/octet-stream"}
            )

            # Get public URL
            url = supabase_client.storage.from_(bucket).get_public_url(path)

            logger.info(f"File uploaded to Supabase Storage: {path}")

            return url
        except Exception as e:
            logger.error(f"Failed to upload file {filename} for user {user_id}: {str(e)}")
            raise

    def download_file(self, user_id: str, filename: str, bucket: str = 'user-files') -> bytes:
        """
        Download file from Supabase Storage

        Args:
            user_id: User UUID
            filename: Name of the file
            bucket: Storage bucket name (default: 'user-files')

        Returns:
            File contents as bytes
        """
        try:
            path = f"{user_id}/files/{filename}"
            file_data = supabase_client.storage.from_(bucket).download(path)

            logger.debug(f"File downloaded from Supabase Storage: {path}")

            return file_data
        except Exception as e:
            logger.error(f"Failed to download file {filename} for user {user_id}: {str(e)}")
            raise

    def list_files(self, user_id: str, bucket: str = 'user-files') -> List[Dict]:
        """
        List all files for user

        Args:
            user_id: User UUID
            bucket: Storage bucket name (default: 'user-files')

        Returns:
            List of file metadata dicts
        """
        try:
            path = f"{user_id}/files"
            result = supabase_client.storage.from_(bucket).list(path)

            return result
        except Exception as e:
            logger.error(f"Failed to list files for user {user_id}: {str(e)}")
            return []

    def delete_file(self, user_id: str, filename: str, bucket: str = 'user-files') -> bool:
        """
        Delete file from storage

        Args:
            user_id: User UUID
            filename: Name of the file
            bucket: Storage bucket name (default: 'user-files')

        Returns:
            True if successful
        """
        try:
            path = f"{user_id}/files/{filename}"
            supabase_client.storage.from_(bucket).remove([path])

            logger.info(f"File deleted from Supabase Storage: {path}")

            return True
        except Exception as e:
            logger.error(f"Failed to delete file {filename} for user {user_id}: {str(e)}")
            return False

    def get_storage_stats(self, user_id: str, bucket: str = 'user-files') -> Dict:
        """
        Get storage statistics for user

        Args:
            user_id: User UUID
            bucket: Storage bucket name (default: 'user-files')

        Returns:
            Dict with total_files, total_size_bytes, total_size_mb
        """
        try:
            files = self.list_files(user_id, bucket)
            total_size = sum(f.get('metadata', {}).get('size', 0) for f in files)

            return {
                'total_files': len(files),
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }
        except Exception as e:
            logger.error(f"Failed to get storage stats for user {user_id}: {str(e)}")
            return {
                'total_files': 0,
                'total_size_bytes': 0,
                'total_size_mb': 0.0
            }


# Singleton instance
supabase_storage = SupabaseStorageService()
