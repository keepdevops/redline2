#!/usr/bin/env python3
"""
User Data Routes
Handles user-specific data access, file management, and storage
"""

from flask import Blueprint, request, jsonify, send_file, g
import logging
import os
from typing import Optional

try:
    from redline.storage.user_storage import user_storage
    STORAGE_AVAILABLE = True
except ImportError:
    STORAGE_AVAILABLE = False
    user_storage = None

user_data_bp = Blueprint('user_data', __name__)
logger = logging.getLogger(__name__)

def get_user_id() -> Optional[str]:
    """Extract user_id from Flask g (set by auth middleware)"""
    return getattr(g, 'user_id', None)

@user_data_bp.route('/files', methods=['GET'])
def list_user_files():
    """List all files for the authenticated user"""
    # Pre-validation with if-else
    user_id = get_user_id()
    if not user_id:
        logger.warning("List user files request without authentication")
        return jsonify({'error': 'Authentication required', 'code': 'AUTH_REQUIRED'}), 401

    if not STORAGE_AVAILABLE:
        logger.error("User storage not available")
        return jsonify({'error': 'User storage not available', 'code': 'STORAGE_UNAVAILABLE'}), 503

    try:
        file_type = request.args.get('type')
        files = user_storage.list_files(user_id, file_type=file_type)

        return jsonify({
            'success': True,
            'files': files,
            'count': len(files)
        }), 200

    except AttributeError as e:
        logger.error(f"Storage method not found for user {user_id}: {str(e)}")
        return jsonify({'error': 'Storage operation failed', 'code': 'ATTRIBUTE_ERROR'}), 500
    except KeyError as e:
        logger.error(f"Missing key in storage data for user {user_id}: {str(e)}")
        return jsonify({'error': f'Missing data: {str(e)}', 'code': 'KEY_ERROR'}), 500
    except Exception as e:
        logger.error(f"Unexpected error listing user files for user {user_id}: {str(e)}")
        return jsonify({'error': 'Internal server error', 'code': 'INTERNAL_ERROR'}), 500

@user_data_bp.route('/files/upload', methods=['POST'])
def upload_file():
    """Upload a file for the user"""
    # Pre-validation with if-else
    user_id = get_user_id()
    if not user_id:
        logger.warning("Upload file request without authentication")
        return jsonify({'error': 'Authentication required', 'code': 'AUTH_REQUIRED'}), 401

    if not STORAGE_AVAILABLE:
        logger.error("User storage not available")
        return jsonify({'error': 'User storage not available', 'code': 'STORAGE_UNAVAILABLE'}), 503

    if 'file' not in request.files:
        logger.warning(f"Upload request without file from user {user_id}")
        return jsonify({'error': 'No file provided', 'code': 'NO_FILE'}), 400

    file = request.files['file']
    if not file.filename or file.filename == '':
        logger.warning(f"Upload request with empty filename from user {user_id}")
        return jsonify({'error': 'No file selected', 'code': 'EMPTY_FILENAME'}), 400

    try:
        # Read file data
        file_data = file.read()
        filename = file.filename
        file_type = request.form.get('file_type') or os.path.splitext(filename)[1][1:].lower()

        # Save file
        result = user_storage.save_file(
            user_id=user_id,
            file_data=file_data,
            filename=filename,
            file_type=file_type,
            metadata={
                'original_filename': filename,
                'uploaded_via': 'web_api'
            }
        )

        return jsonify({
            'success': True,
            'file': result
        }), 200

    except AttributeError as e:
        logger.error(f"Storage method not found for user {user_id}: {str(e)}")
        return jsonify({'error': 'Storage operation failed', 'code': 'ATTRIBUTE_ERROR'}), 500
    except PermissionError as e:
        logger.error(f"Permission denied uploading file for user {user_id}: {str(e)}")
        return jsonify({'error': 'Permission denied', 'code': 'PERMISSION_DENIED'}), 403
    except OSError as e:
        logger.error(f"File system error uploading file for user {user_id}: {str(e)}")
        return jsonify({'error': 'File system error', 'code': 'OS_ERROR'}), 500
    except Exception as e:
        logger.error(f"Unexpected error uploading file for user {user_id}: {str(e)}")
        return jsonify({'error': 'Internal server error', 'code': 'INTERNAL_ERROR'}), 500

@user_data_bp.route('/files/<int:file_id>', methods=['GET'])
def get_file_info(file_id: int):
    """Get file information"""
    # Pre-validation with if-else
    user_id = get_user_id()
    if not user_id:
        logger.warning(f"Get file info request without authentication for file_id {file_id}")
        return jsonify({'error': 'Authentication required', 'code': 'AUTH_REQUIRED'}), 401

    if not STORAGE_AVAILABLE:
        logger.error("User storage not available")
        return jsonify({'error': 'User storage not available', 'code': 'STORAGE_UNAVAILABLE'}), 503

    try:
        file_info = user_storage.get_file(user_id, file_id)

        if not file_info:
            logger.warning(f"File {file_id} not found for user {user_id}")
            return jsonify({'error': 'File not found', 'code': 'FILE_NOT_FOUND'}), 404

        return jsonify({
            'success': True,
            'file': file_info
        }), 200

    except AttributeError as e:
        logger.error(f"Storage method not found for user {user_id}, file {file_id}: {str(e)}")
        return jsonify({'error': 'Storage operation failed', 'code': 'ATTRIBUTE_ERROR'}), 500
    except KeyError as e:
        logger.error(f"Missing key in file info for user {user_id}, file {file_id}: {str(e)}")
        return jsonify({'error': f'Missing data: {str(e)}', 'code': 'KEY_ERROR'}), 500
    except Exception as e:
        logger.error(f"Unexpected error getting file info for user {user_id}, file {file_id}: {str(e)}")
        return jsonify({'error': 'Internal server error', 'code': 'INTERNAL_ERROR'}), 500

@user_data_bp.route('/files/<int:file_id>/download', methods=['GET'])
def download_file(file_id: int):
    """Download a file"""
    # Pre-validation with if-else
    user_id = get_user_id()
    if not user_id:
        logger.warning(f"Download file request without authentication for file_id {file_id}")
        return jsonify({'error': 'Authentication required', 'code': 'AUTH_REQUIRED'}), 401

    if not STORAGE_AVAILABLE:
        logger.error("User storage not available")
        return jsonify({'error': 'User storage not available', 'code': 'STORAGE_UNAVAILABLE'}), 503

    try:
        file_info = user_storage.get_file(user_id, file_id)

        if not file_info or not file_info.get('exists'):
            logger.warning(f"File {file_id} not found for download by user {user_id}")
            return jsonify({'error': 'File not found', 'code': 'FILE_NOT_FOUND'}), 404

        return send_file(
            file_info['local_path'],
            as_attachment=True,
            download_name=file_info['original_filename'] or file_info['filename']
        )

    except FileNotFoundError as e:
        logger.error(f"File not found on disk for user {user_id}, file {file_id}: {str(e)}")
        return jsonify({'error': 'File not found', 'code': 'FILE_NOT_FOUND'}), 404
    except PermissionError as e:
        logger.error(f"Permission denied downloading file for user {user_id}, file {file_id}: {str(e)}")
        return jsonify({'error': 'Permission denied', 'code': 'PERMISSION_DENIED'}), 403
    except KeyError as e:
        logger.error(f"Missing file path for user {user_id}, file {file_id}: {str(e)}")
        return jsonify({'error': 'File configuration error', 'code': 'KEY_ERROR'}), 500
    except Exception as e:
        logger.error(f"Unexpected error downloading file for user {user_id}, file {file_id}: {str(e)}")
        return jsonify({'error': 'Internal server error', 'code': 'INTERNAL_ERROR'}), 500

@user_data_bp.route('/tables', methods=['GET'])
def list_data_tables():
    """List all data tables for the user"""
    # Pre-validation with if-else
    user_id = get_user_id()
    if not user_id:
        logger.warning("List data tables request without authentication")
        return jsonify({'error': 'Authentication required', 'code': 'AUTH_REQUIRED'}), 401

    if not STORAGE_AVAILABLE:
        logger.error("User storage not available")
        return jsonify({'error': 'User storage not available', 'code': 'STORAGE_UNAVAILABLE'}), 503

    try:
        tables = user_storage.list_data_tables(user_id)

        return jsonify({
            'success': True,
            'tables': tables,
            'count': len(tables)
        }), 200

    except AttributeError as e:
        logger.error(f"Storage method not found for user {user_id}: {str(e)}")
        return jsonify({'error': 'Storage operation failed', 'code': 'ATTRIBUTE_ERROR'}), 500
    except KeyError as e:
        logger.error(f"Missing key in table data for user {user_id}: {str(e)}")
        return jsonify({'error': f'Missing data: {str(e)}', 'code': 'KEY_ERROR'}), 500
    except Exception as e:
        logger.error(f"Unexpected error listing data tables for user {user_id}: {str(e)}")
        return jsonify({'error': 'Internal server error', 'code': 'INTERNAL_ERROR'}), 500

@user_data_bp.route('/stats', methods=['GET'])
def get_storage_stats():
    """Get storage statistics for the user"""
    # Pre-validation with if-else
    user_id = get_user_id()
    if not user_id:
        logger.warning("Get storage stats request without authentication")
        return jsonify({'error': 'Authentication required', 'code': 'AUTH_REQUIRED'}), 401

    if not STORAGE_AVAILABLE:
        logger.error("User storage not available")
        return jsonify({'error': 'User storage not available', 'code': 'STORAGE_UNAVAILABLE'}), 503

    try:
        stats = user_storage.get_storage_stats(user_id)

        return jsonify({
            'success': True,
            'stats': stats
        }), 200

    except AttributeError as e:
        logger.error(f"Storage method not found for user {user_id}: {str(e)}")
        return jsonify({'error': 'Storage operation failed', 'code': 'ATTRIBUTE_ERROR'}), 500
    except KeyError as e:
        logger.error(f"Missing key in stats data for user {user_id}: {str(e)}")
        return jsonify({'error': f'Missing data: {str(e)}', 'code': 'KEY_ERROR'}), 500
    except Exception as e:
        logger.error(f"Unexpected error getting storage stats for user {user_id}: {str(e)}")
        return jsonify({'error': 'Internal server error', 'code': 'INTERNAL_ERROR'}), 500

