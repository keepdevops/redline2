"""
API file listing routes for VarioSync Web GUI
Handles file listing and metadata
"""

from flask import Blueprint, jsonify, g
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
    # Get user_id for user-specific S3/R2 files
    user_id = getattr(g, 'user_id', None)

    # Pre-validation with if-else
    data_dir = os.path.join(os.getcwd(), 'data')

    if not data_dir:
        logger.error("Data directory path is empty")
        return jsonify({'error': 'Data directory not configured', 'code': 'DATA_DIR_EMPTY'}), 500

    if not os.path.exists(data_dir):
        logger.warning(f"Data directory does not exist: {data_dir}")
        # Create the directory if it doesn't exist
        try:
            os.makedirs(data_dir, exist_ok=True)
            logger.info(f"Created data directory: {data_dir}")
        except PermissionError as e:
            logger.error(f"Permission denied creating data directory {data_dir}: {str(e)}")
            return jsonify({'error': 'Cannot create data directory', 'code': 'PERMISSION_DENIED'}), 500
        except OSError as e:
            logger.error(f"OS error creating data directory {data_dir}: {str(e)}")
            return jsonify({'error': 'Failed to create data directory', 'code': 'OS_ERROR'}), 500

    logger.debug(f"Listing files from data directory: {data_dir} (user_id: {user_id})")
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
        if not os.access(stooq_dir, os.R_OK):
            logger.warning(f"Stooq directory not readable: {stooq_dir}")
        else:
            # Note: Directory traversal requires try-except for file system errors
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
                                try:
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
                                except (PermissionError, OSError) as e:
                                    logger.debug(f"Cannot access file {file_path}: {str(e)}")
                                    continue
            except PermissionError as e:
                logger.warning(f"Permission denied reading stooq directory {stooq_dir}: {str(e)}")
            except OSError as e:
                logger.warning(f"OS error reading stooq directory {stooq_dir}: {str(e)}")
            except Exception as e:
                logger.warning(f"Unexpected error reading stooq directory {stooq_dir}: {type(e).__name__}: {str(e)}")

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

    if use_s3 and has_s3_creds and user_id:
        logger.debug(f"Fetching S3/R2 files for user: {user_id}")

        # Import boto3 - Note: ImportError is expected if boto3 not installed
        try:
            import boto3
            from botocore.exceptions import ClientError
        except ImportError as e:
            logger.debug(f"boto3 not available, skipping S3/R2 file listing: {str(e)}")
            boto3 = None

        if boto3:
            # Validate S3 configuration
            s3_access_key = os.environ.get('S3_ACCESS_KEY')
            s3_secret_key = os.environ.get('S3_SECRET_KEY')
            bucket = os.environ.get('S3_BUCKET')

            if not s3_access_key or not isinstance(s3_access_key, str):
                logger.warning("S3_ACCESS_KEY is invalid or empty")
            elif not s3_secret_key or not isinstance(s3_secret_key, str):
                logger.warning("S3_SECRET_KEY is invalid or empty")
            elif not bucket or not isinstance(bucket, str):
                logger.warning("S3_BUCKET is invalid or empty")
            else:
                # Configure S3 client - Note: S3 API calls require try-except
                try:
                    endpoint_url = os.environ.get('S3_ENDPOINT_URL')
                    s3_client = boto3.client(
                        's3',
                        aws_access_key_id=s3_access_key,
                        aws_secret_access_key=s3_secret_key,
                        region_name=os.environ.get('S3_REGION', 'us-east-1'),
                        endpoint_url=endpoint_url if endpoint_url else None
                    )

                    # Get user's S3 prefix (using user_id directly)
                    s3_prefix = f"users/{user_id}/files/"
                    logger.debug(f"Listing S3/R2 objects with prefix: {s3_prefix}")

                    # List objects in S3/R2
                    try:
                        paginator = s3_client.get_paginator('list_objects_v2')
                        pages = paginator.paginate(Bucket=bucket, Prefix=s3_prefix)

                        for page in pages:
                            if 'Contents' in page:
                                for obj in page['Contents']:
                                    # Validate object structure
                                    if not isinstance(obj, dict):
                                        logger.debug(f"Invalid S3 object type: {type(obj)}")
                                        continue

                                    s3_key = obj.get('Key')
                                    if not s3_key:
                                        logger.debug("S3 object missing 'Key' field")
                                        continue

                                    filename = os.path.basename(s3_key)
                                    if not filename:
                                        logger.debug(f"S3 key has no filename: {s3_key}")
                                        continue

                                    # Skip if already in local files (avoid duplicates)
                                    if any(f['name'] == filename and f['storage'] == 'local' for f in files):
                                        logger.debug(f"Skipping duplicate S3 file: {filename}")
                                        continue

                                    # Get file URL
                                    if endpoint_url:
                                        endpoint = endpoint_url.rstrip('/')
                                        file_url = f"{endpoint}/{bucket}/{s3_key}"
                                    else:
                                        region = os.environ.get('S3_REGION', 'us-east-1')
                                        file_url = f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"

                                    files.append({
                                        'name': filename,
                                        'size': obj.get('Size', 0),
                                        'modified': obj.get('LastModified').timestamp() if obj.get('LastModified') else 0,
                                        'path': s3_key,
                                        'file_url': file_url,
                                        'storage': 'r2' if endpoint_url and 'r2.cloudflarestorage.com' in endpoint_url else 's3',
                                        'location': 'cloud'
                                    })

                        logger.debug(f"Found {sum(1 for f in files if f.get('storage') in ('s3', 'r2'))} S3/R2 files for user {user_id}")

                    except ClientError as e:
                        error_code = e.response.get('Error', {}).get('Code', 'Unknown') if hasattr(e, 'response') else 'Unknown'
                        logger.warning(f"S3/R2 ClientError listing files for user {user_id}: {error_code}: {str(e)}")
                    except Exception as e:
                        logger.warning(f"Unexpected error listing S3/R2 files for user {user_id}: {type(e).__name__}: {str(e)}")

                except Exception as e:
                    logger.warning(f"Error configuring S3/R2 client for user {user_id}: {type(e).__name__}: {str(e)}")
    else:
        if use_s3:
            if not has_s3_creds:
                logger.debug("S3 storage enabled but credentials missing")
            elif not user_id:
                logger.debug("S3 storage enabled but no user_id for file listing")

    # Sort by modification time (newest first)
    files.sort(key=lambda x: x.get('modified', 0), reverse=True)

    logger.info(f"File listing completed: {len(files)} files found (user_id: {user_id})")
    return jsonify({'files': files})

