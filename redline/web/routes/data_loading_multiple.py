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
    """Upload a file to the data directory. Handles ZIP extraction for Stooq files."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
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

