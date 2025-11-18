"""
API routes for file operations.
Handles file listing, upload, and deletion.
"""

from flask import Blueprint, request, jsonify, current_app
import logging
import os
from werkzeug.utils import secure_filename
from ..utils.api_helpers import rate_limit, allowed_file

api_files_bp = Blueprint('api_files', __name__)
logger = logging.getLogger(__name__)

# System files to exclude from user-facing file lists
SYSTEM_FILES = {
    'usage_data.duckdb',
    'redline_data.duckdb',
    'api_keys.json',
    'custom_apis.json',
    'licenses.json',
    'data_config.ini',
    'config.ini'
}

# System files that should never be deleted
PROTECTED_FILES = {
    'usage_data.duckdb',
    'redline_data.duckdb',
    'api_keys.json',
    'custom_apis.json',
    'licenses.json',
    'data_config.ini',
    'config.ini'
}


@api_files_bp.route('/files')
def api_list_files():
    """List available data files via API."""
    try:
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
                        'path': file_path
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
                        'location': 'downloaded'
                    })

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
                                'location': rel_path
                            })
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({'files': files})
        
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_files_bp.route('/files/<path:filename>', methods=['DELETE'])
@rate_limit("20 per minute")
def delete_file(filename):
    """Delete a data file."""
    try:
        # Secure the filename to prevent directory traversal
        safe_filename = secure_filename(os.path.basename(filename))
        
        # Check if file is protected
        if safe_filename in PROTECTED_FILES:
            return jsonify({
                'error': 'Cannot delete system file',
                'message': f'File "{safe_filename}" is a protected system file and cannot be deleted'
            }), 403
        
        # Search for the file in data directories
        data_dir = os.path.join(os.getcwd(), 'data')
        file_path = None
        
        # Check locations in order of priority
        search_paths = [
            os.path.join(data_dir, safe_filename),
            os.path.join(data_dir, 'downloaded', safe_filename),
            os.path.join(data_dir, 'stooq', safe_filename),
            os.path.join(data_dir, 'uploads', safe_filename)
        ]
        
        # Also search in converted directory recursively
        converted_dir = os.path.join(data_dir, 'converted')
        if os.path.exists(converted_dir):
            # First try direct path
            direct_path = os.path.join(converted_dir, safe_filename)
            if os.path.exists(direct_path) and os.path.isfile(direct_path):
                search_paths.append(direct_path)
            else:
                # Search recursively
                for root, dirs, files in os.walk(converted_dir):
                    if safe_filename in files:
                        potential_path = os.path.join(root, safe_filename)
                        if os.path.exists(potential_path) and os.path.isfile(potential_path):
                            search_paths.append(potential_path)
                            break
        
        # Find the file
        for path in search_paths:
            if os.path.exists(path) and os.path.isfile(path):
                file_path = path
                break
        
        if not file_path:
            return jsonify({
                'error': 'File not found',
                'message': f'File "{safe_filename}" not found in data directories'
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


@api_files_bp.route('/upload', methods=['POST'])
@rate_limit("10 per minute")
def upload_file():
    """Upload a file for processing. Handles ZIP extraction for Stooq files."""
    try:
        import zipfile
        
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


@api_files_bp.route('/files', methods=['GET'])
def list_files():
    """List available data files."""
    try:
        data_dir = os.path.join(os.getcwd(), 'data')
        files = []
        
        for filename in os.listdir(data_dir):
            if allowed_file(filename):
                file_path = os.path.join(data_dir, filename)
                file_stat = os.stat(file_path)
                files.append({
                    'name': filename,
                    'size': file_stat.st_size,
                    'modified': file_stat.st_mtime
                })
        
        return jsonify({'files': files})
        
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return jsonify({'error': str(e)}), 500

