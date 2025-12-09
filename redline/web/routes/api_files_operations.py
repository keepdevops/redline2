"""
API file operations routes for REDLINE Web GUI
Handles file upload and deletion
"""

from flask import Blueprint, request, jsonify, current_app
import logging
import os
import zipfile
from werkzeug.utils import secure_filename
from ..utils.api_helpers import rate_limit, allowed_file

api_files_operations_bp = Blueprint('api_files_operations', __name__)
logger = logging.getLogger(__name__)

# System files that should never be deleted
PROTECTED_FILES = {
    'usage_data.duckdb',
    'redline_data.duckdb',
    # These files are now in ~/.redline/ and should not be listed
    # 'api_keys.json',
    # 'custom_apis.json',
    # 'licenses.json',
    'data_config.ini',
    'config.ini'
}

@api_files_operations_bp.route('/files/<path:filename>', methods=['DELETE'])
@rate_limit("20 per minute")
def delete_file(filename):
    """Delete a data file."""
    try:
        # Get the original filename from the path parameter
        # The filename may contain special characters like '=' that secure_filename removes
        # Also handle paths with subdirectories (e.g., "stooq/5min/file.txt")
        original_filename = os.path.basename(filename)
        safe_filename = secure_filename(original_filename)
        
        # Check if file is protected
        if safe_filename in PROTECTED_FILES or original_filename in PROTECTED_FILES:
            return jsonify({
                'error': 'Cannot delete system file',
                'message': f'File "{original_filename}" is a protected system file and cannot be deleted'
            }), 403
        
        # Search for the file in data directories
        data_dir = os.path.join(os.getcwd(), 'data')
        file_path = None
        
        logger.info(f"Delete request for: {repr(filename)} (original: {repr(original_filename)}, safe: {repr(safe_filename)})")
        
        # First, try the path as-is if it contains subdirectories (e.g., "stooq/5 min/hk/file.txt")
        if '/' in filename or '\\' in filename:
            # Path contains subdirectories - try direct path first
            # Flask's <path:filename> should preserve the path structure
            potential_path = os.path.join(data_dir, filename)
            logger.info(f"Trying direct path: {potential_path}")
            if os.path.exists(potential_path) and os.path.isfile(potential_path):
                file_path = potential_path
                logger.info(f"Found file using direct path: {potential_path}")
            else:
                logger.warning(f"Direct path not found: {potential_path} (exists: {os.path.exists(potential_path)})")
        
        # If not found, try both original and safe filename in case secure_filename modified it
        if not file_path:
            logger.info(f"File not found via direct path, starting recursive search for: {original_filename}")
            filenames_to_search = [original_filename]
            if safe_filename != original_filename:
                filenames_to_search.append(safe_filename)
            
            logger.info(f"Will search for filenames: {filenames_to_search}")
            
            # Check locations in order of priority for both filename variants
            search_paths = []
            for search_filename in filenames_to_search:
                search_paths.extend([
                    os.path.join(data_dir, search_filename),
                    os.path.join(data_dir, 'downloaded', search_filename),
                    os.path.join(data_dir, 'stooq', search_filename),
                    os.path.join(data_dir, 'uploads', search_filename)
                ])
            
            # Also search in stooq directory recursively (handle nested subdirectories)
            stooq_dir = os.path.join(data_dir, 'stooq')
            if os.path.exists(stooq_dir):
                for search_filename in filenames_to_search:
                    # Search recursively in all subdirectories
                    logger.info(f"Recursively searching for '{search_filename}' in {stooq_dir}")
                    found_count = 0
                    for root, dirs, files in os.walk(stooq_dir):
                        if search_filename in files:
                            potential_path = os.path.join(root, search_filename)
                            if os.path.exists(potential_path) and os.path.isfile(potential_path):
                                found_count += 1
                                logger.info(f"Found file #{found_count} in recursive search: {potential_path}")
                                search_paths.append(potential_path)
                                # Use the first match found (most common case)
                                if not file_path:
                                    file_path = potential_path
                                    logger.info(f"Using first match: {file_path}")
                                # Don't break - there might be multiple files with same name in different locations
                    if found_count == 0:
                        logger.warning(f"No files named '{search_filename}' found in recursive search of {stooq_dir}")
                    else:
                        logger.info(f"Recursive search found {found_count} file(s) named '{search_filename}'")
            
            # Also search in downloads directory recursively (handle nested subdirectories)
            downloads_dir = os.path.join(data_dir, 'downloads')
            if os.path.exists(downloads_dir):
                for search_filename in filenames_to_search:
                    # Search recursively in all subdirectories
                    for root, dirs, files in os.walk(downloads_dir):
                        if search_filename in files:
                            potential_path = os.path.join(root, search_filename)
                            if os.path.exists(potential_path) and os.path.isfile(potential_path):
                                search_paths.append(potential_path)
                                # Don't break - there might be multiple files with same name in different locations
            
            # Also search in converted directory recursively
            converted_dir = os.path.join(data_dir, 'converted')
            if os.path.exists(converted_dir):
                for search_filename in filenames_to_search:
                    # First try direct path
                    direct_path = os.path.join(converted_dir, search_filename)
                    if os.path.exists(direct_path) and os.path.isfile(direct_path):
                        search_paths.append(direct_path)
                    else:
                        # Search recursively in all subdirectories
                        for root, dirs, files in os.walk(converted_dir):
                            if search_filename in files:
                                potential_path = os.path.join(root, search_filename)
                                if os.path.exists(potential_path) and os.path.isfile(potential_path):
                                    search_paths.append(potential_path)
                                    break  # Found it, no need to continue
            
            # Find the file (check search_paths, prioritizing recursive finds)
            # First check recursive search results (these are more likely to be correct for nested files)
            recursive_paths = [p for p in search_paths if 'stooq' in p or 'downloads' in p or 'converted' in p]
            direct_paths = [p for p in search_paths if p not in recursive_paths]
            
            # Try recursive paths first (for nested subdirectories)
            for path in recursive_paths:
                if os.path.exists(path) and os.path.isfile(path):
                    file_path = path
                    logger.info(f"Found file via recursive search: {file_path}")
                    break
            
            # If not found in recursive search, try direct paths
            if not file_path:
                for path in direct_paths:
                    if os.path.exists(path) and os.path.isfile(path):
                        file_path = path
                        logger.info(f"Found file via direct path: {file_path}")
                        break
        
        if not file_path:
            logger.warning(f"File not found: {filename} (searched as: {original_filename})")
            logger.debug(f"Data dir: {data_dir}, Received filename: {repr(filename)}")
            if 'search_paths' in locals():
                logger.debug(f"Total search paths checked: {len(search_paths)}")
                logger.debug(f"First 5 search paths: {search_paths[:5]}")
            return jsonify({
                'error': 'File not found',
                'message': f'File "{original_filename}" not found in data directories',
                'searched_path': filename,
                'data_dir': data_dir,
                'hint': 'If the file is in a subdirectory with spaces, ensure the full relative path is provided (e.g., "stooq/5 min/hk/file.txt")'
            }), 404
        
        # Delete the file
        try:
            os.remove(file_path)
            logger.info(f"Deleted file: {file_path}")
            return jsonify({
                'success': True,
                'message': f'File "{safe_filename}" deleted successfully',
                'filename': safe_filename
            })
        except PermissionError:
            return jsonify({
                'error': 'Permission denied',
                'message': f'Cannot delete file "{safe_filename}": Permission denied'
            }), 403
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")
            return jsonify({
                'error': 'Failed to delete file',
                'message': str(e)
            }), 500
        
    except Exception as e:
        logger.error(f"Error in delete_file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_files_operations_bp.route('/upload', methods=['POST'])
@rate_limit("10 per minute")
def upload_file():
    """Upload a file for processing. Handles ZIP extraction for Stooq files."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_path)
            
            # Check if it's a ZIP file and extract to data/stooq
            extracted_files = []
            final_path = upload_path
            
            if zipfile.is_zipfile(upload_path):
                logger.info(f"Detected ZIP file: {filename}, extracting to data/stooq...")
                try:
                    from redline.utils.stooq_file_handler import extract_zip_file
                    extracted = extract_zip_file(upload_path)
                    extracted_files = extracted if isinstance(extracted, list) else [extracted]
                    os.remove(upload_path)  # Remove ZIP after extraction
                    
                    if extracted_files:
                        final_path = extracted_files[0] if len(extracted_files) == 1 else extracted_files
                except Exception as e:
                    logger.error(f"Error extracting ZIP: {str(e)}")
            else:
                # Check if it's a Stooq file and move to data/stooq
                try:
                    from redline.utils.stooq_file_handler import is_stooq_file, move_file_to_stooq_dir
                    if is_stooq_file(filename):
                        final_path = move_file_to_stooq_dir(upload_path, filename)
                        logger.info(f"Moved Stooq file {filename} to data/stooq directory")
                except Exception as e:
                    logger.warning(f"Could not check/move to stooq directory: {str(e)}")
            
            response = {
                'message': 'File uploaded successfully',
                'filename': os.path.basename(final_path) if isinstance(final_path, str) else filename,
                'path': final_path
            }
            
            if extracted_files:
                response['extracted_files'] = [os.path.basename(f) for f in extracted_files]
                response['extracted_count'] = len(extracted_files)
                response['message'] = f'ZIP file extracted. {len(extracted_files)} file(s) in data/stooq.'
            
            return jsonify(response)
        else:
            return jsonify({'error': 'Invalid file type'}), 400
            
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return jsonify({'error': str(e)}), 500

