"""
Single file loading routes for REDLINE Web GUI
Handles loading individual files
"""

from flask import Blueprint, request, jsonify
import logging
import os
from ..utils.file_loading import (
    rate_limit,
    detect_format_from_path as _detect_format_from_path,
    load_file_by_format as _load_file_by_format
)
from ..utils.data_helpers import clean_dataframe_columns

data_loading_single_bp = Blueprint('data_loading_single', __name__)
logger = logging.getLogger(__name__)

@data_loading_single_bp.route('/load', methods=['POST'])
@rate_limit("30 per minute")
def load_data():
    """Load data from file."""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        logger.info(f"load_data() called with filename: {filename}")
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        # Determine file path - check multiple locations in order
        data_dir = os.path.join(os.getcwd(), 'data')
        data_path = None
        
        # Check locations in order of priority:
        # 1. Root data directory
        # 2. data/stooq directory (for Stooq downloads)
        # 3. data/downloaded directory (for other downloads)
        # 4. data/uploads directory (for uploaded files)
        # 5. data/converted directory (recursively - for converted files)
        search_paths = [
            os.path.join(data_dir, filename),
            os.path.join(data_dir, 'stooq', filename),  # Already included
            os.path.join(data_dir, 'downloaded', filename),
            os.path.join(data_dir, 'uploads', filename)
        ]
        
        # Also search in converted directory recursively
        converted_dir = os.path.join(data_dir, 'converted')
        converted_path = None
        if os.path.exists(converted_dir):
            # First try direct path (most common case)
            direct_converted_path = os.path.join(converted_dir, filename)
            logger.debug(f"Checking converted direct path: {direct_converted_path}")
            if os.path.exists(direct_converted_path) and os.path.isfile(direct_converted_path):
                converted_path = direct_converted_path
                logger.info(f"Found file in converted directory: {converted_path}")
            else:
                # If not found, search recursively
                logger.debug(f"File not in converted root, searching recursively...")
                for root, dirs, files in os.walk(converted_dir):
                    if filename in files:
                        potential_path = os.path.join(root, filename)
                        if os.path.exists(potential_path) and os.path.isfile(potential_path):
                            converted_path = potential_path
                            logger.info(f"Found file in converted subdirectory: {converted_path}")
                            break
        
        # Add converted path to search paths if found
        if converted_path:
            search_paths.append(converted_path)
            logger.debug(f"Added converted path to search: {converted_path}")
        
        # Try all search paths
        logger.debug(f"Searching {len(search_paths)} paths for {filename}")
        for path in search_paths:
            if os.path.exists(path) and os.path.isfile(path):
                data_path = path
                logger.info(f"Found file at: {data_path}")
                break
        
        # If file not found locally, check S3/R2
        if not data_path:
            use_s3 = os.environ.get('USE_S3_STORAGE', 'false').lower() == 'true'
            has_s3_creds = all([
                os.environ.get('S3_ACCESS_KEY'),
                os.environ.get('S3_SECRET_KEY'),
                os.environ.get('S3_BUCKET')
            ])
            
            if use_s3 and has_s3_creds:
                # Get license key for user-specific S3/R2 files
                license_key = request.headers.get('X-License-Key') or (data.get('license_key') if isinstance(data, dict) else None)
                
                if license_key:
                    try:
                        import boto3
                        from botocore.exceptions import ClientError
                        import hashlib
                        import tempfile
                        
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
                        s3_key = f"users/{key_hash}/files/{filename}"
                        
                        # Try to download from S3/R2
                        try:
                            # Create temporary file
                            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1])
                            temp_path = temp_file.name
                            temp_file.close()
                            
                            # Download from S3/R2
                            s3_client.download_file(bucket, s3_key, temp_path)
                            data_path = temp_path
                            logger.info(f"Downloaded file from S3/R2: {s3_key} to {temp_path}")
                            
                        except ClientError as e:
                            if e.response['Error']['Code'] == 'NoSuchKey':
                                logger.warning(f"File not found in S3/R2: {s3_key}")
                            else:
                                logger.error(f"Error downloading from S3/R2: {str(e)}")
                    except ImportError:
                        logger.debug("boto3 not available, skipping S3/R2 check")
                    except Exception as e:
                        logger.warning(f"Error checking S3/R2: {str(e)}")
        
        if not data_path:
            logger.warning(f"File not found: {filename}. Searched in: {', '.join(search_paths[:4])}")
            return jsonify({
                'error': 'File not found',
                'message': f'File "{filename}" not found in data directories or S3/R2',
                'searched_paths': search_paths[:4]  # Don't include all converted paths
            }), 404
        
        # Load data
        format_type = _detect_format_from_path(data_path)
        logger.info(f"Loading file with format: {format_type}")
        try:
            df = _load_file_by_format(data_path, format_type)
        except Exception as e:
            logger.error(f"Error loading file {data_path}: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return jsonify({
                'error': 'Failed to load file',
                'message': str(e),
                'format': format_type
            }), 500
        
        if df.empty:
            logger.warning(f"Loaded DataFrame is empty for {filename}")
            return jsonify({
                'error': 'No data found',
                'message': f'The file "{filename}" contains no data or could not be parsed',
                'format': format_type
            }), 404
        
        # Clean up malformed CSV headers - remove unnamed/empty columns
        df = clean_dataframe_columns(df)
        
        # Mask API keys if this is an API key file or contains API key columns
        from ..utils.security_helpers import should_mask_file, mask_dataframe_columns
        if should_mask_file(filename):
            df = mask_dataframe_columns(df)
            logger.info(f"Masked API keys in file: {filename}")
        else:
            # Still check for API key columns even if not an API key file
            df = mask_dataframe_columns(df)
        
        # Check if file is in converted directory (suggests it may have been cleaned during conversion)
        is_converted_file = 'converted' in data_path.replace(os.sep, '/')
        logger.info(f"File {filename} is_converted_file: {is_converted_file} (path: {data_path})")
        
        # Get pagination parameters
        page = data.get('page', 1)
        per_page = data.get('per_page', 500)
        
        # Validate pagination parameters
        try:
            page = max(1, int(page))
            per_page = min(max(1, int(per_page)), 1000)  # Max 1000 rows per page
        except (ValueError, TypeError):
            page = 1
            per_page = 500
        
        # Calculate pagination
        total_rows = len(df)
        total_pages = (total_rows + per_page - 1) // per_page
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total_rows)
        
        # Get paginated data
        paginated_df = df.iloc[start_idx:end_idx]
        
        return jsonify({
            'columns': list(df.columns),
            'data': paginated_df.to_dict('records'),
            'total_rows': total_rows,
            'filename': filename,
            'is_converted_file': is_converted_file,  # Indicates file is in converted/ directory
            'file_path': data_path,  # Include path for debugging
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_rows,
                'pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        })
        
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@data_loading_single_bp.route('/load-from-path', methods=['POST'])
def load_data_from_path():
    """Load data from any file path on the system."""
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        if not os.path.isfile(file_path):
            return jsonify({'error': 'Path is not a file'}), 400
        
        # Security check - prevent loading sensitive files
        abs_path = os.path.abspath(file_path)
        if any(abs_path.startswith(restricted) for restricted in ['/etc/', '/var/', '/usr/bin/', '/usr/sbin/']):
            return jsonify({'error': 'Access denied to system files'}), 403
        
        # Load data
        format_type = _detect_format_from_path(file_path)
        df = _load_file_by_format(file_path, format_type)
        
        if df.empty:
            return jsonify({'error': 'No data found'}), 404
        
        # Clean up malformed CSV headers
        df = clean_dataframe_columns(df)
        
        return jsonify({
            'columns': list(df.columns),
            'data': df.head(1000).to_dict('records'),
            'total_rows': len(df),
            'filename': os.path.basename(file_path),
            'file_path': file_path
        })
        
    except Exception as e:
        logger.error(f"Error loading data from path: {str(e)}")
        return jsonify({'error': str(e)}), 500

