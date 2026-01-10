"""
Single file loading routes for VarioSync Web GUI
Handles loading individual files
"""

from flask import Blueprint, request, jsonify, g
import logging
import os
from ..utils.file_loading import (
    rate_limit,
    detect_format_from_path as _detect_format_from_path,
    load_file_by_format as _load_file_by_format
)
from ..utils.data_helpers import clean_dataframe_columns
from redline.auth.supabase_auth import auth_manager

data_loading_single_bp = Blueprint('data_loading_single', __name__)
logger = logging.getLogger(__name__)

@data_loading_single_bp.route('/load', methods=['POST'])
@rate_limit("200 per minute")  # Increased for pagination - users need to browse through pages
@auth_manager.require_auth
def load_data():
    """Load data from file. Requires JWT authentication."""
    # Get authenticated user from g (set by @require_auth decorator)
    user_id = getattr(g, 'user_id', None)
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get request data
    data = request.get_json()

    if not data:
        logger.warning("Load data request with empty body")
        return jsonify({'error': 'Request body is required'}), 400

    if not isinstance(data, dict):
        logger.error(f"Load data request with invalid data type: {type(data)}")
        return jsonify({'error': 'Request body must be JSON object'}), 400

    # Validate filename
    filename = data.get('filename')

    if not filename:
        logger.warning("Load data request missing filename field")
        return jsonify({'error': 'No filename provided'}), 400

    if not isinstance(filename, str):
        logger.error(f"Load data request filename has invalid type: {type(filename)}")
        return jsonify({'error': 'Filename must be a string'}), 400

    if len(filename) == 0:
        logger.warning("Load data request with empty filename")
        return jsonify({'error': 'Filename cannot be empty'}), 400

    # Security check: prevent path traversal
    if '..' in filename or filename.startswith('/') or filename.startswith('\\'):
        logger.warning(f"Load data request with suspicious filename: {filename}")
        return jsonify({'error': 'Invalid filename format'}), 400

    logger.info(f"Processing load data request for filename: {filename}")

    try:
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
                # Get user_id for user-specific S3/R2 files
                user_id = getattr(g, 'user_id', None)

                if user_id:
                    try:
                        import boto3
                        from botocore.exceptions import ClientError
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

                        # Get user's S3 prefix (using user_id instead of license key hash)
                        s3_key = f"users/{user_id}/files/{filename}"

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

        # Validate file path exists
        if not data_path:
            logger.error(f"data_path is None after search for {filename}")
            return jsonify({
                'error': 'File not found',
                'message': f'File "{filename}" not found in data directories or S3/R2'
            }), 404

        if not os.path.exists(data_path):
            logger.error(f"data_path does not exist: {data_path}")
            return jsonify({
                'error': 'File not found',
                'message': f'File path exists but file not accessible: {data_path}'
            }), 404

        # Get file size for logging
        try:
            file_size = os.path.getsize(data_path)
            logger.debug(f"File size: {file_size} bytes")
        except OSError as e:
            logger.warning(f"Could not get file size for {data_path}: {str(e)}")
            file_size = None

        # Detect file format
        format_type = _detect_format_from_path(data_path)

        if not format_type:
            logger.error(f"Could not detect format for file: {data_path}")
            return jsonify({
                'error': 'Unknown file format',
                'message': f'Could not determine format for file: {filename}'
            }), 400

        logger.info(f"Loading file with format: {format_type} (size: {file_size} bytes)")

        # Load file data
        df = _load_file_by_format(data_path, format_type)

        # Validate loaded data
        if df is None:
            logger.error(f"File loading returned None for {filename}")
            return jsonify({
                'error': 'Failed to load file',
                'message': f'File loading function returned None for format: {format_type}'
            }), 500

        if not hasattr(df, 'empty'):
            logger.error(f"Loaded data is not a DataFrame for {filename}: {type(df)}")
            return jsonify({
                'error': 'Failed to load file',
                'message': f'File loading returned unexpected type: {type(df)}'
            }), 500

        if df.empty:
            logger.warning(f"Loaded DataFrame is empty for {filename}")
            return jsonify({
                'error': 'No data found',
                'message': f'The file "{filename}" contains no data or could not be parsed',
                'format': format_type
            }), 404

        logger.debug(f"Successfully loaded DataFrame with shape: {df.shape}")

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

        # Validate pagination parameters - handle various input types
        try:
            # Convert to string first to handle edge cases, then to int
            if page is None:
                page = 1
            else:
                # Handle string inputs like "1", "2", etc.
                page_str = str(page).strip()
                # Remove any non-numeric characters (except negative sign, but we'll clamp to 1+)
                page_str = ''.join(c for c in page_str if c.isdigit() or c == '-')
                if page_str and page_str != '-':
                    page = max(1, int(page_str))
                else:
                    page = 1
        except (ValueError, TypeError, AttributeError) as e:
            logger.warning(f"Invalid page parameter '{data.get('page')}', defaulting to 1: {str(e)}")
            page = 1

        try:
            if per_page is None:
                per_page = 500
            else:
                # Handle string inputs like "500", "1000", etc.
                per_page_str = str(per_page).strip()
                # Remove any non-numeric characters
                per_page_str = ''.join(c for c in per_page_str if c.isdigit() or c == '-')
                if per_page_str and per_page_str != '-':
                    per_page = min(max(1, int(per_page_str)), 1000)  # Max 1000 rows per page
                else:
                    per_page = 500
        except (ValueError, TypeError, AttributeError) as e:
            logger.warning(f"Invalid per_page parameter '{data.get('per_page')}', defaulting to 500: {str(e)}")
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

    except PermissionError as e:
        logger.error(f"Permission denied loading file {filename}: {str(e)}")
        return jsonify({'error': 'Permission denied', 'code': 'PERMISSION_DENIED'}), 403
    except OSError as e:
        logger.error(f"OS error loading file {filename}: {str(e)}")
        return jsonify({'error': 'File system error', 'code': 'OS_ERROR'}), 500
    except KeyError as e:
        logger.error(f"Missing column in data for {filename}: {str(e)}")
        return jsonify({'error': f'Data error: {str(e)}', 'code': 'KEY_ERROR'}), 500
    except ValueError as e:
        logger.error(f"Value error loading file {filename}: {str(e)}")
        return jsonify({'error': f'Data format error: {str(e)}', 'code': 'VALUE_ERROR'}), 400
    except Exception as e:
        logger.error(f"Unexpected error loading data for {filename}: {str(e)}")
        return jsonify({'error': 'Internal server error', 'code': 'INTERNAL_ERROR'}), 500

@data_loading_single_bp.route('/load-from-path', methods=['POST'])
def load_data_from_path():
    """Load data from any file path on the system."""
    # Pre-validation with if-else
    data = request.get_json()

    if not data:
        logger.warning("Load from path request with empty body")
        return jsonify({'error': 'Request body is required', 'code': 'NO_BODY'}), 400

    file_path = data.get('file_path')

    if not file_path:
        logger.warning("Load from path request missing file_path")
        return jsonify({'error': 'File path is required', 'code': 'NO_FILE_PATH'}), 400

    if not isinstance(file_path, str):
        logger.error(f"Load from path request with invalid file_path type: {type(file_path)}")
        return jsonify({'error': 'File path must be a string', 'code': 'INVALID_PATH_TYPE'}), 400

    if not os.path.exists(file_path):
        logger.warning(f"File not found: {file_path}")
        return jsonify({'error': 'File not found', 'code': 'FILE_NOT_FOUND'}), 404

    if not os.path.isfile(file_path):
        logger.warning(f"Path is not a file: {file_path}")
        return jsonify({'error': 'Path is not a file', 'code': 'NOT_FILE'}), 400

    # Security check - prevent loading sensitive files
    abs_path = os.path.abspath(file_path)
    if any(abs_path.startswith(restricted) for restricted in ['/etc/', '/var/', '/usr/bin/', '/usr/sbin/']):
        logger.warning(f"Attempted access to restricted system file: {abs_path}")
        return jsonify({'error': 'Access denied to system files', 'code': 'ACCESS_DENIED'}), 403

    try:
        # Load data
        format_type = _detect_format_from_path(file_path)
        df = _load_file_by_format(file_path, format_type)

        if df.empty:
            logger.warning(f"Loaded DataFrame is empty for {file_path}")
            return jsonify({'error': 'No data found', 'code': 'NO_DATA'}), 404

        # Clean up malformed CSV headers
        df = clean_dataframe_columns(df)

        return jsonify({
            'columns': list(df.columns),
            'data': df.head(1000).to_dict('records'),
            'total_rows': len(df),
            'filename': os.path.basename(file_path),
            'file_path': file_path
        })

    except PermissionError as e:
        logger.error(f"Permission denied loading file {file_path}: {str(e)}")
        return jsonify({'error': 'Permission denied', 'code': 'PERMISSION_DENIED'}), 403
    except OSError as e:
        logger.error(f"OS error loading file {file_path}: {str(e)}")
        return jsonify({'error': 'File system error', 'code': 'OS_ERROR'}), 500
    except KeyError as e:
        logger.error(f"Missing column in data for {file_path}: {str(e)}")
        return jsonify({'error': f'Data error: {str(e)}', 'code': 'KEY_ERROR'}), 500
    except ValueError as e:
        logger.error(f"Value error loading file {file_path}: {str(e)}")
        return jsonify({'error': f'Data format error: {str(e)}', 'code': 'VALUE_ERROR'}), 400
    except Exception as e:
        logger.error(f"Unexpected error loading data from path {file_path}: {str(e)}")
        return jsonify({'error': 'Internal server error', 'code': 'INTERNAL_ERROR'}), 500

