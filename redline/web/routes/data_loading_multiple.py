"""
Multiple file loading routes for VarioSync Web GUI
Handles loading multiple files and file uploads
"""

from flask import Blueprint, request, jsonify, g
import logging
import os
import zipfile
from ..utils.file_loading import (
    detect_format_from_path as _detect_format_from_path,
    load_file_by_format as _load_file_by_format
)
from ..utils.data_helpers import clean_dataframe_columns

data_loading_multiple_bp = Blueprint('data_loading_multiple', __name__)
logger = logging.getLogger(__name__)

@data_loading_multiple_bp.route('/load-multiple', methods=['POST'])
def load_multiple_files():
    """Load multiple files at once."""
    # Pre-validation with if-else
    data = request.get_json()

    if not data:
        logger.warning("Load multiple files request with empty body")
        return jsonify({'error': 'Request body is required', 'code': 'NO_BODY'}), 400

    if not isinstance(data, dict):
        logger.error(f"Load multiple files request with invalid data type: {type(data)}")
        return jsonify({'error': 'Request body must be JSON object', 'code': 'INVALID_BODY_TYPE'}), 400

    filenames = data.get('filenames', [])

    if not filenames:
        logger.warning("Load multiple files request without filenames")
        return jsonify({'error': 'No filenames provided', 'code': 'NO_FILENAMES'}), 400

    if not isinstance(filenames, list):
        logger.error(f"Filenames must be a list, got {type(filenames)}")
        return jsonify({'error': 'Filenames must be an array', 'code': 'INVALID_FILENAMES_TYPE'}), 400

    try:
        
        results = {}
        errors = {}
        success_count = 0
        error_count = 0
        
        for filename in filenames:
            try:
                # Determine file path - check multiple locations in order
                data_dir = os.path.join(os.getcwd(), 'data')
                
                # Check locations in order of priority:
                # 1. Root data directory
                # 2. data/stooq directory (for Stooq downloads)
                # 3. data/downloaded directory (for other downloads)
                # 4. data/uploads directory (for uploaded files)
                # 5. data/converted directory (recursively - for converted files)
                search_paths = [
                    os.path.join(data_dir, filename),
                    os.path.join(data_dir, 'stooq', filename),
                    os.path.join(data_dir, 'downloaded', filename),
                    os.path.join(data_dir, 'uploads', filename)
                ]
                
                # Also search in converted directory recursively
                converted_dir = os.path.join(data_dir, 'converted')
                converted_path = None
                if os.path.exists(converted_dir):
                    # First try direct path (most common case)
                    direct_converted_path = os.path.join(converted_dir, filename)
                    if os.path.exists(direct_converted_path) and os.path.isfile(direct_converted_path):
                        converted_path = direct_converted_path
                    else:
                        # If not found, search recursively
                        for root, dirs, files in os.walk(converted_dir):
                            if filename in files:
                                potential_path = os.path.join(root, filename)
                                if os.path.exists(potential_path) and os.path.isfile(potential_path):
                                    converted_path = potential_path
                                    break
                
                # Add converted path to search paths if found
                if converted_path:
                    search_paths.append(converted_path)
                
                # Try all search paths
                file_path = None
                for path in search_paths:
                    if os.path.exists(path) and os.path.isfile(path):
                        file_path = path
                        break
                
                if not file_path:
                    errors[filename] = f'File not found: {filename}'
                    error_count += 1
                    continue
                
                # Load the file
                format_type = _detect_format_from_path(file_path)
                df = _load_file_by_format(file_path, format_type)
                
                if df.empty:
                    errors[filename] = f'No data found in file: {filename}'
                    error_count += 1
                    continue
                
                # Clean up malformed CSV headers - remove unnamed/empty columns
                df = clean_dataframe_columns(df)
                
                # Store results
                results[filename] = {
                    'columns': list(df.columns),
                    'data': df.head(1000).to_dict('records'),
                    'total_rows': len(df),
                    'filename': filename
                }
                success_count += 1

            except PermissionError as e:
                logger.error(f"Permission denied loading file {filename}: {str(e)}")
                errors[filename] = f"Permission denied: {str(e)}"
                error_count += 1
            except OSError as e:
                logger.error(f"OS error loading file {filename}: {str(e)}")
                errors[filename] = f"File system error: {str(e)}"
                error_count += 1
            except KeyError as e:
                logger.error(f"Missing column in data for {filename}: {str(e)}")
                errors[filename] = f"Data error: {str(e)}"
                error_count += 1
            except ValueError as e:
                logger.error(f"Value error loading file {filename}: {str(e)}")
                errors[filename] = f"Data format error: {str(e)}"
                error_count += 1
            except Exception as e:
                logger.error(f"Unexpected error loading file {filename}: {str(e)}")
                errors[filename] = f"Internal error: {str(e)}"
                error_count += 1
        
        return jsonify({
            'success_count': success_count,
            'error_count': error_count,
            'results': results,
            'errors': errors
        })

    except PermissionError as e:
        logger.error(f"Permission denied in load_multiple_files: {str(e)}")
        return jsonify({'error': 'Permission denied', 'code': 'PERMISSION_DENIED'}), 403
    except OSError as e:
        logger.error(f"OS error in load_multiple_files: {str(e)}")
        return jsonify({'error': 'File system error', 'code': 'OS_ERROR'}), 500
    except KeyError as e:
        logger.error(f"Missing key in load_multiple_files: {str(e)}")
        return jsonify({'error': f'Missing data: {str(e)}', 'code': 'KEY_ERROR'}), 500
    except ValueError as e:
        logger.error(f"Value error in load_multiple_files: {str(e)}")
        return jsonify({'error': f'Data format error: {str(e)}', 'code': 'VALUE_ERROR'}), 400
    except Exception as e:
        logger.error(f"Unexpected error in load_multiple_files: {str(e)}")
        return jsonify({'error': 'Internal server error', 'code': 'INTERNAL_ERROR'}), 500

@data_loading_multiple_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    Upload a file to the data directory or S3/R2.
    Handles ZIP extraction for Stooq files.
    If S3/R2 is configured, uploads directly to cloud storage.
    """
    # Pre-validation with if-else
    if 'file' not in request.files:
        logger.warning("Upload file request without file")
        return jsonify({'error': 'No file provided', 'code': 'NO_FILE'}), 400

    file = request.files['file']

    if not file or file.filename == '':
        logger.warning("Upload file request with empty filename")
        return jsonify({'error': 'No file selected', 'code': 'EMPTY_FILENAME'}), 400

    if not isinstance(file.filename, str):
        logger.error(f"Invalid filename type: {type(file.filename)}")
        return jsonify({'error': 'Invalid filename type', 'code': 'INVALID_FILENAME_TYPE'}), 400

    try:
        
        # Check if S3/R2 is configured and should be used
        use_s3 = os.environ.get('USE_S3_STORAGE', 'false').lower() == 'true'
        has_s3_creds = all([
            os.environ.get('S3_ACCESS_KEY'),
            os.environ.get('S3_SECRET_KEY'),
            os.environ.get('S3_BUCKET')
        ])
        
        # If S3/R2 is configured, upload directly to cloud storage
        if use_s3 and has_s3_creds:
            try:
                import boto3
                from botocore.exceptions import ClientError
                
                # Get user_id for user isolation
                user_id = getattr(g, 'user_id', 'anonymous')

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

                # Read file data
                file_data = file.read()
                filename = file.filename
                s3_key = f"users/{user_id}/files/{filename}"
                
                # Upload to S3/R2
                s3_client.put_object(
                    Bucket=bucket,
                    Key=s3_key,
                    Body=file_data,
                    ContentType=file.content_type or 'application/octet-stream'
                )
                
                # Handle ZIP extraction if needed
                extracted_files = []
                if zipfile.is_zipfile(file):
                    # For ZIP files, we'd need to download, extract, and re-upload
                    # For now, just upload the ZIP and note it needs extraction
                    logger.info(f"ZIP file uploaded to S3/R2: {filename}")
                    message = f'ZIP file uploaded to S3/R2. Extraction can be done on-demand.'
                else:
                    message = f'File uploaded to S3/R2 successfully.'
                
                # Get file URL
                if endpoint_url:
                    # R2 or custom endpoint
                    endpoint = endpoint_url.rstrip('/')
                    file_url = f"{endpoint}/{bucket}/{s3_key}"
                else:
                    # Standard S3
                    region = os.environ.get('S3_REGION', 'us-east-1')
                    file_url = f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"
                
                return jsonify({
                    'message': message,
                    'filename': filename,
                    's3_key': s3_key,
                    'file_url': file_url,
                    'storage': 'r2' if endpoint_url and 'r2.cloudflarestorage.com' in endpoint_url else 's3',
                    'size': len(file_data)
                })

            except ImportError as e:
                logger.warning(f"boto3 not available, falling back to local storage: {str(e)}")
            except PermissionError as e:
                logger.error(f"Permission denied uploading to S3/R2: {str(e)}, falling back to local storage")
            except OSError as e:
                logger.error(f"OS error uploading to S3/R2: {str(e)}, falling back to local storage")
            except Exception as e:
                logger.error(f"Unexpected error uploading to S3/R2: {str(e)}, falling back to local storage")
        
        # Fallback to local storage
        # Save uploaded file temporarily
        upload_dir = os.path.join(os.getcwd(), 'data', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        temp_path = os.path.join(upload_dir, file.filename)
        file.save(temp_path)
        
        # Check if it's a ZIP file (common for Stooq downloads)
        extracted_files = []
        final_path = temp_path
        
        if zipfile.is_zipfile(temp_path):
            logger.info(f"Detected ZIP file: {file.filename}, extracting...")
            try:
                from redline.utils.stooq_file_handler import extract_zip_file
                
                # Extract to data/stooq directory
                extracted = extract_zip_file(temp_path)
                extracted_files = extracted if isinstance(extracted, list) else [extracted]
                
                # Remove the ZIP file after extraction
                os.remove(temp_path)
                
                if extracted_files:
                    final_path = extracted_files[0] if len(extracted_files) == 1 else extracted_files
                    message = f'ZIP file extracted successfully. {len(extracted_files)} file(s) extracted to data/stooq directory.'
                else:
                    logger.warning(f"ZIP file extraction produced no files: {file.filename}")
                    return jsonify({'error': 'ZIP file extraction failed or contained no files', 'code': 'EMPTY_ZIP'}), 400

            except ImportError as e:
                logger.error(f"Import error extracting ZIP file {file.filename}: {str(e)}")
                return jsonify({'error': f'Failed to import extraction module: {str(e)}', 'code': 'IMPORT_ERROR'}), 500
            except PermissionError as e:
                logger.error(f"Permission denied extracting ZIP file {file.filename}: {str(e)}")
                return jsonify({'error': 'Permission denied during extraction', 'code': 'PERMISSION_DENIED'}), 403
            except OSError as e:
                logger.error(f"OS error extracting ZIP file {file.filename}: {str(e)}")
                return jsonify({'error': f'File system error during extraction: {str(e)}', 'code': 'OS_ERROR'}), 500
            except Exception as e:
                logger.error(f"Unexpected error extracting ZIP file {file.filename}: {str(e)}")
                return jsonify({'error': f'Failed to extract ZIP file: {str(e)}', 'code': 'EXTRACTION_ERROR'}), 500
        else:
            # For non-ZIP files, check if it's a Stooq file and move to data/stooq
            try:
                from redline.utils.stooq_file_handler import is_stooq_file, move_file_to_stooq_dir
                
                if is_stooq_file(file.filename):
                    final_path = move_file_to_stooq_dir(temp_path, file.filename)
                    message = f'File uploaded and moved to data/stooq directory.'
                else:
                    message = f'File uploaded successfully.'
            except ImportError as e:
                logger.warning(f"Could not import Stooq handler for file {file.filename}: {str(e)}")
                message = f'File uploaded successfully.'
            except PermissionError as e:
                logger.warning(f"Permission denied moving file {file.filename}: {str(e)}")
                message = f'File uploaded successfully.'
            except OSError as e:
                logger.warning(f"OS error moving file {file.filename}: {str(e)}")
                message = f'File uploaded successfully.'
            except Exception as e:
                logger.warning(f"Unexpected error checking/moving file {file.filename}: {str(e)}")
                message = f'File uploaded successfully.'
        
        response_data = {
            'message': message,
            'filename': os.path.basename(final_path) if isinstance(final_path, str) else file.filename,
            'path': final_path,
            'is_zip': zipfile.is_zipfile(temp_path) if os.path.exists(temp_path) else False
        }
        
        if extracted_files:
            response_data['extracted_files'] = [os.path.basename(f) for f in extracted_files]
            response_data['extracted_count'] = len(extracted_files)
        
        return jsonify(response_data)

    except PermissionError as e:
        logger.error(f"Permission denied uploading file: {str(e)}")
        return jsonify({'error': 'Permission denied', 'code': 'PERMISSION_DENIED'}), 403
    except OSError as e:
        logger.error(f"OS error uploading file: {str(e)}")
        return jsonify({'error': 'File system error', 'code': 'OS_ERROR'}), 500
    except KeyError as e:
        logger.error(f"Missing key in upload file: {str(e)}")
        return jsonify({'error': f'Missing data: {str(e)}', 'code': 'KEY_ERROR'}), 500
    except ValueError as e:
        logger.error(f"Value error uploading file: {str(e)}")
        return jsonify({'error': f'Invalid data: {str(e)}', 'code': 'VALUE_ERROR'}), 400
    except Exception as e:
        logger.error(f"Unexpected error uploading file: {str(e)}")
        return jsonify({'error': 'Internal server error', 'code': 'INTERNAL_ERROR'}), 500

