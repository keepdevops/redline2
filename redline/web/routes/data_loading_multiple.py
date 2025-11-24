"""
Multiple file loading routes for REDLINE Web GUI
Handles loading multiple files and file uploads
"""

from flask import Blueprint, request, jsonify
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
    try:
        data = request.get_json()
        filenames = data.get('filenames', [])
        
        if not filenames:
            return jsonify({'error': 'No filenames provided'}), 400
        
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
                
            except Exception as e:
                logger.error(f"Error loading file {filename}: {str(e)}")
                errors[filename] = str(e)
                error_count += 1
        
        return jsonify({
            'success_count': success_count,
            'error_count': error_count,
            'results': results,
            'errors': errors
        })
        
    except Exception as e:
        logger.error(f"Error in load_multiple_files: {str(e)}")
        return jsonify({'error': str(e)}), 500

@data_loading_multiple_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    Upload a file to the data directory or S3/R2.
    Handles ZIP extraction for Stooq files.
    If S3/R2 is configured, uploads directly to cloud storage.
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
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
                
                # Get license key for user isolation
                license_key = request.headers.get('X-License-Key') or request.form.get('license_key', 'default')
                import hashlib
                key_hash = hashlib.sha256(license_key.encode()).hexdigest()[:16]
                
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
                s3_key = f"users/{key_hash}/files/{filename}"
                
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
                
            except ImportError:
                logger.warning("boto3 not available, falling back to local storage")
            except Exception as e:
                logger.error(f"Error uploading to S3/R2: {str(e)}, falling back to local storage")
        
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
                    return jsonify({'error': 'ZIP file extraction failed or contained no files'}), 400
                    
            except Exception as e:
                logger.error(f"Error extracting ZIP file: {str(e)}")
                return jsonify({'error': f'Failed to extract ZIP file: {str(e)}'}), 500
        else:
            # For non-ZIP files, check if it's a Stooq file and move to data/stooq
            try:
                from redline.utils.stooq_file_handler import is_stooq_file, move_file_to_stooq_dir
                
                if is_stooq_file(file.filename):
                    final_path = move_file_to_stooq_dir(temp_path, file.filename)
                    message = f'File uploaded and moved to data/stooq directory.'
                else:
                    message = f'File uploaded successfully.'
            except Exception as e:
                logger.warning(f"Could not check/move file: {str(e)}")
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
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return jsonify({'error': str(e)}), 500

