"""
API file operations routes for VarioSync Web GUI
Handles file upload and deletion
"""

from flask import Blueprint, request, jsonify, current_app, g
import logging
import os
import zipfile
from werkzeug.utils import secure_filename
from ..utils.api_helpers import rate_limit, allowed_file
from redline.auth.supabase_auth import auth_manager

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
@auth_manager.require_auth
def delete_file(filename):
    """Delete a data file. Requires JWT authentication."""
    # Get authenticated user from g (set by @require_auth decorator)
    user_id = getattr(g, 'user_id', None)
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    # Validate filename parameter
    if not filename:
        logger.warning("Delete file request with empty filename")
        return jsonify({'error': 'Filename is required'}), 400

    if not isinstance(filename, str):
        logger.error(f"Delete file request with invalid filename type: {type(filename)}")
        return jsonify({'error': 'Filename must be a string'}), 400

    if len(filename) == 0:
        logger.warning("Delete file request with zero-length filename")
        return jsonify({'error': 'Filename cannot be empty'}), 400

    # Security check: prevent path traversal attempts
    if '..' in filename:
        logger.warning(f"Delete file request with path traversal attempt: {filename}")
        return jsonify({'error': 'Invalid filename format (path traversal not allowed)'}), 400

    # Get the original filename from the path parameter
    # The filename may contain special characters like '=' that secure_filename removes
    # Also handle paths with subdirectories (e.g., "stooq/5min/file.txt")
    original_filename = os.path.basename(filename)
    safe_filename = secure_filename(original_filename)

    logger.info(f"Delete request for: {repr(filename)} (original: {repr(original_filename)}, safe: {repr(safe_filename)})")

    # Validate safe_filename is not empty after sanitization
    if not safe_filename:
        logger.warning(f"Filename became empty after sanitization: {original_filename}")
        return jsonify({'error': 'Filename contains only invalid characters'}), 400

    # Check if file is protected
    if safe_filename in PROTECTED_FILES or original_filename in PROTECTED_FILES:
        logger.warning(f"Attempted to delete protected file: {original_filename}")
        return jsonify({
            'error': 'Cannot delete system file',
            'message': f'File "{original_filename}" is a protected system file and cannot be deleted'
        }), 403

    # Validate data directory
    data_dir = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(data_dir):
        logger.error(f"Data directory not found: {data_dir}")
        return jsonify({'error': 'Data directory not configured'}), 500

    # Search for the file in data directories
    file_path = None

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

    # Delete the file (legitimate exception handling for file operations)
    try:
        os.remove(file_path)
        logger.info(f"Deleted file: {file_path}")
        return jsonify({
            'success': True,
            'message': f'File "{safe_filename}" deleted successfully',
            'filename': safe_filename
        })
    except FileNotFoundError:
        logger.error(f"File not found for deletion: {file_path}")
        return jsonify({
            'error': 'File not found',
            'message': f'File "{safe_filename}" not found',
            'code': 'FILE_NOT_FOUND'
        }), 404
    except PermissionError:
        logger.error(f"Permission denied deleting file: {file_path}")
        return jsonify({
            'error': 'Permission denied',
            'message': f'Cannot delete file "{safe_filename}": Permission denied',
            'code': 'PERMISSION_DENIED'
        }), 403
    except OSError as e:
        logger.error(f"OS error deleting file {file_path}: {str(e)}")
        return jsonify({
            'error': 'File system error',
            'message': f'Failed to delete file: {str(e)}',
            'code': 'OS_ERROR'
        }), 500
    except Exception as e:
        logger.error(f"Unexpected error deleting file {file_path}: {str(e)}")
        return jsonify({
            'error': 'Failed to delete file',
            'message': str(e),
            'code': 'DELETE_ERROR'
        }), 500

@api_files_operations_bp.route('/upload', methods=['POST'])
@rate_limit("10 per minute")
@auth_manager.require_auth
def upload_file():
    """Upload a file for processing. Handles ZIP extraction for Stooq files. Requires JWT authentication."""
    # Get authenticated user from g (set by @require_auth decorator)
    user_id = getattr(g, 'user_id', None)
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Validate file presence
    if 'file' not in request.files:
        logger.warning("Upload request missing file field")
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    # Validate filename
    if not file.filename or file.filename == '':
        logger.warning("Upload request with empty filename")
        return jsonify({'error': 'No file selected'}), 400

    if not isinstance(file.filename, str):
        logger.error(f"Upload request with invalid filename type: {type(file.filename)}")
        return jsonify({'error': 'Invalid filename type'}), 400

    logger.info(f"Processing upload request: {file.filename}")

    # Validate file type
    if not allowed_file(file.filename):
        logger.warning(f"Upload request with disallowed file type: {file.filename}")
        return jsonify({'error': 'Invalid file type'}), 400

    # Sanitize filename
    filename = secure_filename(file.filename)

    if not filename:
        logger.warning(f"Filename became empty after sanitization: {file.filename}")
        return jsonify({'error': 'Filename contains only invalid characters'}), 400

    # Validate upload folder configuration
    if 'UPLOAD_FOLDER' not in current_app.config:
        logger.error("UPLOAD_FOLDER not configured in app config")
        return jsonify({'error': 'Upload configuration missing'}), 500

    upload_folder = current_app.config['UPLOAD_FOLDER']

    if not os.path.exists(upload_folder):
        logger.error(f"Upload folder does not exist: {upload_folder}")
        return jsonify({'error': 'Upload folder not found'}), 500

    upload_path = os.path.join(upload_folder, filename)
    logger.debug(f"Upload path: {upload_path}")

    # Save file (Note: File I/O requires try-except for external operations)
    try:
        file.save(upload_path)
        logger.info(f"File saved to: {upload_path}")
    except PermissionError as e:
        logger.error(f"Permission denied saving file {upload_path}: {str(e)}")
        return jsonify({'error': 'Permission denied saving file', 'code': 'PERMISSION_DENIED'}), 403
    except OSError as e:
        logger.error(f"OS error saving file {upload_path}: {str(e)}")
        return jsonify({'error': f'Failed to save file: {str(e)}', 'code': 'OS_ERROR'}), 500
    except IOError as e:
        logger.error(f"I/O error saving file {upload_path}: {str(e)}")
        return jsonify({'error': 'I/O error writing file', 'code': 'IO_ERROR'}), 500
    except Exception as e:
        logger.error(f"Unexpected error saving file {upload_path}: {type(e).__name__}: {str(e)}")
        return jsonify({'error': f'Failed to save file: {str(e)}', 'code': 'SAVE_ERROR'}), 500

    # Verify file was saved
    if not os.path.exists(upload_path):
        logger.error(f"File was not created after save: {upload_path}")
        return jsonify({'error': 'Failed to save file', 'code': 'FILE_NOT_CREATED'}), 500

    # Check if it's a ZIP file and extract to data/stooq
    extracted_files = []
    final_path = upload_path

    # Check if file is a ZIP file
    is_zip = zipfile.is_zipfile(upload_path)
    logger.debug(f"File is ZIP: {is_zip}")

    if is_zip:
        logger.info(f"Detected ZIP file: {filename}, extracting to data/stooq...")

        # Import extraction utility
        try:
            from redline.utils.stooq_file_handler import extract_zip_file
        except ImportError as e:
            logger.error(f"Failed to import stooq_file_handler for ZIP extraction: {str(e)}")
            # ZIP uploaded but cannot extract - return success with warning
            return jsonify({
                'message': 'ZIP file uploaded but extraction not available',
                'filename': filename,
                'path': upload_path,
                'warning': 'ZIP extraction module not available'
            })

        # Extract ZIP file - Note: ZIP operations require try-except for file format errors
        try:
            extracted = extract_zip_file(upload_path)

            # Validate extraction result
            if not extracted:
                logger.warning(f"ZIP extraction returned no files for {filename}")
                extracted_files = []
            elif isinstance(extracted, list):
                extracted_files = extracted
            else:
                extracted_files = [extracted]

            # Remove ZIP after successful extraction
            if extracted_files:
                try:
                    os.remove(upload_path)
                    logger.debug(f"Removed ZIP file after extraction: {upload_path}")
                except PermissionError as e:
                    logger.warning(f"Permission denied removing ZIP file {upload_path}: {str(e)}")
                except OSError as e:
                    logger.warning(f"OS error removing ZIP file {upload_path}: {str(e)}")
                except Exception as e:
                    logger.warning(f"Unexpected error removing ZIP file {upload_path}: {str(e)}")

                final_path = extracted_files[0] if len(extracted_files) == 1 else extracted_files
                logger.info(f"Extracted {len(extracted_files)} file(s) from ZIP: {filename}")
            else:
                logger.warning(f"ZIP extraction returned no files for {filename}")

        except zipfile.BadZipFile as e:
            logger.error(f"Invalid ZIP file {filename}: {str(e)}")
            return jsonify({'error': 'Invalid ZIP file format', 'code': 'BAD_ZIP'}), 400
        except ValueError as e:
            logger.error(f"Value error extracting ZIP {filename}: {str(e)}")
            return jsonify({'error': f'ZIP extraction error: {str(e)}', 'code': 'EXTRACTION_ERROR'}), 400
        except Exception as e:
            logger.error(f"Unexpected error extracting ZIP {filename}: {type(e).__name__}: {str(e)}")
            # ZIP extraction failed, but original file is still saved
            extracted_files = []
    else:
        # Check if it's a Stooq file and move to data/stooq
        logger.debug(f"Non-ZIP file, checking if Stooq file: {filename}")

        # Import Stooq utilities
        try:
            from redline.utils.stooq_file_handler import is_stooq_file, move_file_to_stooq_dir
        except ImportError as e:
            logger.debug(f"stooq_file_handler not available: {str(e)}")
            # File uploaded successfully, just won't be moved to stooq directory
        else:
            # Check and move if Stooq file
            try:
                if is_stooq_file(filename):
                    logger.info(f"Detected Stooq file: {filename}")
                    final_path = move_file_to_stooq_dir(upload_path, filename)

                    # Validate move was successful
                    if final_path and os.path.exists(final_path):
                        logger.info(f"Moved Stooq file to data/stooq directory: {final_path}")
                    else:
                        logger.warning(f"Stooq file move returned invalid path: {final_path}")
                        final_path = upload_path
                else:
                    logger.debug(f"Not a Stooq file: {filename}")
            except PermissionError as e:
                logger.warning(f"Permission denied moving Stooq file {filename}: {str(e)}")
                # File is still saved in upload folder if move fails
            except OSError as e:
                logger.warning(f"OS error moving Stooq file {filename}: {str(e)}")
                # File is still saved in upload folder if move fails
            except Exception as e:
                logger.warning(f"Unexpected error checking/moving Stooq file {filename}: {type(e).__name__}: {str(e)}")
                # File is still saved in upload folder if move fails

    # Prepare response
    response = {
        'message': 'File uploaded successfully',
        'filename': os.path.basename(final_path) if isinstance(final_path, str) else filename,
        'path': final_path
    }

    if extracted_files:
        response['extracted_files'] = [os.path.basename(f) for f in extracted_files]
        response['extracted_count'] = len(extracted_files)
        response['message'] = f'ZIP file extracted. {len(extracted_files)} file(s) in data/stooq.'

    logger.info(f"Upload completed successfully: {response['filename']}")
    return jsonify(response)

