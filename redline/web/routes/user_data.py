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
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401

        if not STORAGE_AVAILABLE:
            return jsonify({'error': 'User storage not available'}), 503

        file_type = request.args.get('type')
        files = user_storage.list_files(user_id, file_type=file_type)
        
        return jsonify({
            'success': True,
            'files': files,
            'count': len(files)
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing user files: {str(e)}")
        return jsonify({'error': str(e)}), 500

@user_data_bp.route('/files/upload', methods=['POST'])
def upload_file():
    """Upload a file for the user"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        if not STORAGE_AVAILABLE:
            return jsonify({'error': 'User storage not available'}), 503
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
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
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@user_data_bp.route('/files/<int:file_id>', methods=['GET'])
def get_file_info(file_id: int):
    """Get file information"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        if not STORAGE_AVAILABLE:
            return jsonify({'error': 'User storage not available'}), 503
        
        file_info = user_storage.get_file(user_id, file_id)
        
        if not file_info:
            return jsonify({'error': 'File not found'}), 404
        
        return jsonify({
            'success': True,
            'file': file_info
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting file info: {str(e)}")
        return jsonify({'error': str(e)}), 500

@user_data_bp.route('/files/<int:file_id>/download', methods=['GET'])
def download_file(file_id: int):
    """Download a file"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        if not STORAGE_AVAILABLE:
            return jsonify({'error': 'User storage not available'}), 503
        
        file_info = user_storage.get_file(user_id, file_id)
        
        if not file_info or not file_info.get('exists'):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            file_info['local_path'],
            as_attachment=True,
            download_name=file_info['original_filename'] or file_info['filename']
        )
        
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@user_data_bp.route('/tables', methods=['GET'])
def list_data_tables():
    """List all data tables for the user"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        if not STORAGE_AVAILABLE:
            return jsonify({'error': 'User storage not available'}), 503
        
        tables = user_storage.list_data_tables(user_id)
        
        return jsonify({
            'success': True,
            'tables': tables,
            'count': len(tables)
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing data tables: {str(e)}")
        return jsonify({'error': str(e)}), 500

@user_data_bp.route('/stats', methods=['GET'])
def get_storage_stats():
    """Get storage statistics for the user"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        if not STORAGE_AVAILABLE:
            return jsonify({'error': 'User storage not available'}), 503
        
        stats = user_storage.get_storage_stats(user_id)
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting storage stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

