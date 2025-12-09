"""
API file listing routes for REDLINE Web GUI
Handles file listing and metadata
"""

from flask import Blueprint, jsonify
import logging
import os
from ..utils.api_helpers import rate_limit

api_files_list_bp = Blueprint('api_files_list', __name__)
logger = logging.getLogger(__name__)

# System files to exclude from user-facing file lists
SYSTEM_FILES = {
    'usage_data.duckdb',
    'redline_data.duckdb',
    # These files are now in ~/.redline/ and should not be listed
    # 'api_keys.json',
    # 'custom_apis.json',
    # 'licenses.json',
    'data_config.ini',
    'config.ini'
}

@api_files_list_bp.route('/files')
@rate_limit("200 per hour")  # More generous limit for file listing (read-only operation)
def api_list_files():
    """List available data files via API. Includes local and S3/R2 files."""
    try:
        from flask import request
        import hashlib
        
        # Get license key for user-specific S3/R2 files
        license_key = request.headers.get('X-License-Key') or request.args.get('license_key')
        
        data_dir = os.path.join(os.getcwd(), 'data')
        files = []
        
        # Get files from main data directory
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                # Skip system files
                if filename in SYSTEM_FILES:
                    continue
                file_path = os.path.join(data_dir, filename)
                if os.path.isfile(file_path) and not filename.startswith('.'):
                    file_stat = os.stat(file_path)
                    files.append({
                        'name': filename,
                        'size': file_stat.st_size,
                        'modified': file_stat.st_mtime,
                        'path': file_path,
                        'storage': 'local',
                        'location': 'root'
                    })
        
        # Get files from downloaded directory
        downloaded_dir = os.path.join(data_dir, 'downloaded')
        if os.path.exists(downloaded_dir):
            for filename in os.listdir(downloaded_dir):
                # Skip system files
                if filename in SYSTEM_FILES:
                    continue
                file_path = os.path.join(downloaded_dir, filename)
                if os.path.isfile(file_path) and not filename.startswith('.'):
                    file_stat = os.stat(file_path)
                    files.append({
                        'name': filename,
                        'size': file_stat.st_size,
                        'modified': file_stat.st_mtime,
                        'path': file_path,
                        'storage': 'local',
                        'location': 'downloaded'
                    })
        
        # Get files from uploads directory
        uploads_dir = os.path.join(data_dir, 'uploads')
        if os.path.exists(uploads_dir):
            for filename in os.listdir(uploads_dir):
                # Skip system files
                if filename in SYSTEM_FILES:
                    continue
                file_path = os.path.join(uploads_dir, filename)
                if os.path.isfile(file_path) and not filename.startswith('.'):
                    file_stat = os.stat(file_path)
                    files.append({
                        'name': filename,
                        'size': file_stat.st_size,
                        'modified': file_stat.st_mtime,
                        'path': file_path,
                        'storage': 'local',
                        'location': 'uploads'
                    })
        
        # Get files from stooq directory (recursively including all subdirectories)
        # Stooq data often comes in nested structures like: stooq/5min/subfolder1/data.txt
        stooq_dir = os.path.join(data_dir, 'stooq')
        if os.path.exists(stooq_dir):
            try:
                # Recursively search all subdirectories in stooq/
                for root, dirs, filenames in os.walk(stooq_dir):
                    for filename in filenames:
                        # Skip system files
                        if filename in SYSTEM_FILES:
                            continue
                        if not filename.startswith('.'):
                            file_path = os.path.join(root, filename)
                            if os.path.isfile(file_path):
                                file_stat = os.stat(file_path)
                                # Get relative path from data_dir for detailed location
                                rel_path = os.path.relpath(file_path, data_dir)
                                # Also get relative path from stooq_dir for cleaner display
                                stooq_rel_path = os.path.relpath(file_path, stooq_dir)

                                files.append({
                                    'name': filename,
                                    'size': file_stat.st_size,
                                    'modified': file_stat.st_mtime,
                                    'path': file_path,
                                    'storage': 'local',
                                    'location': rel_path,  # Full path: stooq/5min/folder/file.txt
                                    'stooq_path': stooq_rel_path  # Relative to stooq: 5min/folder/file.txt
                                })
            except Exception as e:
                logger.warning(f"Error reading stooq directory: {str(e)}")

        # Get files from converted/export directory (recursively including subdirectories)
        converted_dir = os.path.join(data_dir, 'converted')
        if os.path.exists(converted_dir):
            # Recursively search subdirectories in converted/ (duckdb/, parquet/, etc.)
            for root, dirs, filenames in os.walk(converted_dir):
                for filename in filenames:
                    # Skip system files
                    if filename in SYSTEM_FILES:
                        continue
                    if not filename.startswith('.'):
                        file_path = os.path.join(root, filename)
                        if os.path.isfile(file_path):
                            file_stat = os.stat(file_path)
                            # Get relative path for location
                            rel_path = os.path.relpath(file_path, data_dir)
                            files.append({
                                'name': filename,
                                'size': file_stat.st_size,
                                'modified': file_stat.st_mtime,
                                'path': file_path,
                                'storage': 'local',
                                'location': rel_path
                            })
        
        # Get files from S3/R2 if configured
        use_s3 = os.environ.get('USE_S3_STORAGE', 'false').lower() == 'true'
        has_s3_creds = all([
            os.environ.get('S3_ACCESS_KEY'),
            os.environ.get('S3_SECRET_KEY'),
            os.environ.get('S3_BUCKET')
        ])
        
        if use_s3 and has_s3_creds and license_key:
            try:
                import boto3
                from botocore.exceptions import ClientError
                
                # Configure S3 client
                endpoint_url = os.environ.get('S3_ENDPOINT_URL')
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=os.environ.get('S3_ACCESS_KEY'),
                    aws_secret_access_key=os.environ.get('S3_SECRET_KEY'),
                    region_name=os.environ.get('S3_REGION', 'us-east-1'),
                    endpoint_url=endpoint_url if endpoint_url else None
                )
                bucket = os.environ.get('S3_BUCKET')
                
                # Get user's S3 prefix
                key_hash = hashlib.sha256(license_key.encode()).hexdigest()[:16]
                s3_prefix = f"users/{key_hash}/files/"
                
                # List objects in S3/R2
                try:
                    paginator = s3_client.get_paginator('list_objects_v2')
                    pages = paginator.paginate(Bucket=bucket, Prefix=s3_prefix)
                    
                    for page in pages:
                        if 'Contents' in page:
                            for obj in page['Contents']:
                                # Get filename from S3 key
                                s3_key = obj['Key']
                                filename = os.path.basename(s3_key)
                                
                                # Skip if already in local files (avoid duplicates)
                                if not any(f['name'] == filename and f['storage'] == 'local' for f in files):
                                    # Get file URL
                                    if endpoint_url:
                                        endpoint = endpoint_url.rstrip('/')
                                        file_url = f"{endpoint}/{bucket}/{s3_key}"
                                    else:
                                        region = os.environ.get('S3_REGION', 'us-east-1')
                                        file_url = f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"
                                    
                                    files.append({
                                        'name': filename,
                                        'size': obj['Size'],
                                        'modified': obj['LastModified'].timestamp(),
                                        'path': s3_key,
                                        'file_url': file_url,
                                        'storage': 'r2' if endpoint_url and 'r2.cloudflarestorage.com' in endpoint_url else 's3',
                                        'location': 'cloud'
                                    })
                except ClientError as e:
                    logger.warning(f"Error listing S3/R2 files: {str(e)}")
                    
            except ImportError:
                logger.debug("boto3 not available, skipping S3/R2 file listing")
            except Exception as e:
                logger.warning(f"Error accessing S3/R2: {str(e)}")
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: x.get('modified', 0), reverse=True)
        
        return jsonify({'files': files})

    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return jsonify({'error': str(e)}), 500

