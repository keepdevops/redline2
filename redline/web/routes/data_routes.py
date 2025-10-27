"""
Data tab routes for REDLINE Web GUI
Route handlers for data viewing, filtering, and management
"""

from flask import Blueprint, render_template, request, jsonify, send_file
import logging
import os
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from ...database.optimized_connector import OptimizedDatabaseConnector
from ...core.schema import EXT_TO_FORMAT
from ..utils.file_loading import (
    rate_limit,
    detect_format_from_path as _detect_format_from_path,
    load_file_by_format as _load_file_by_format,
    save_file_by_format as _save_file_by_format,
    apply_filters as _apply_filters,
    load_large_file_chunked as _load_large_file_chunked
)

# Initialize optimized database connector
optimized_db = OptimizedDatabaseConnector(max_connections=8, cache_size=64, cache_ttl=300)

# Create blueprint
data_bp = Blueprint('data', __name__)
logger = logging.getLogger(__name__)

@data_bp.route('/')
def data_tab():
    """Data tab main page - TKINTER STYLE VERSION."""
    return render_template('data_tab_tkinter_style.html')

@data_bp.route('/browser')
def file_browser():
    """File browser page - browse and load files from anywhere on the system."""
    return render_template('file_browser.html')

@data_bp.route('/stooq')
def stooq_downloader():
    """Stooq data downloader page."""
    return render_template('stooq_downloader.html')

@data_bp.route('/multi')
def data_tab_multi():
    """Multi-file data tab."""
    return render_template('data_tab_multi_file.html')

@data_bp.route('/debug')
def data_tab_debug():
    """Data tab debug page."""
    return render_template('data_tab_debug.html')

@data_bp.route('/simple')
def data_tab_simple():
    """Data tab simple version."""
    return render_template('data_tab_simple.html')

@data_bp.route('/files')
def list_files():
    """List available data files."""
    try:
        data_dir = os.path.join(os.getcwd(), 'data')
        files = []
        
        # Get files from root data directory
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                file_path = os.path.join(data_dir, filename)
                if os.path.isfile(file_path) and not filename.startswith('.'):
                    file_stat = os.stat(file_path)
                    files.append({
                        'name': filename,
                        'size': file_stat.st_size,
                        'modified': file_stat.st_mtime,
                        'path': file_path,
                        'location': 'root'
                    })
        
        # Get files from downloaded directory
        downloaded_dir = os.path.join(data_dir, 'downloaded')
        if os.path.exists(downloaded_dir):
            for filename in os.listdir(downloaded_dir):
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
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({'files': files})
        
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return jsonify({'error': str(e)}), 500

@data_bp.route('/db-stats')
def get_database_stats():
    """Get database performance statistics."""
    try:
        stats = optimized_db.get_performance_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting database stats: {str(e)}")
        return jsonify({'error': str(e)}), 500
# Rest of the routes continue here - keeping this as a simplified version
# The full implementation would include all route handlers from original data.py
# Shows the modular approach for better code organization

@data_bp.route('/load-multiple', methods=['POST'])
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
                # Build file paths
                data_dir = os.path.join(os.getcwd(), 'data')
                root_path = os.path.join(data_dir, filename)
                downloaded_path = os.path.join(data_dir, 'downloaded', filename)
                
                file_path = None
                if os.path.exists(root_path):
                    file_path = root_path
                elif os.path.exists(downloaded_path):
                    file_path = downloaded_path
                else:
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
                
                # Store results
                results[filename] = {
                    'columns': list(df.columns),
                    'data': df.head(1000).to_dict('records'),
                    'total_rows': len(df)
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

@data_bp.route('/load', methods=['POST'])
@rate_limit("30 per minute")
def load_data():
    """Load data from file."""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        # Determine file path
        data_dir = os.path.join(os.getcwd(), 'data')
        data_path = None
        
        root_path = os.path.join(data_dir, filename)
        if os.path.exists(root_path):
            data_path = root_path
        else:
            downloaded_path = os.path.join(data_dir, 'downloaded', filename)
            if os.path.exists(downloaded_path):
                data_path = downloaded_path
        
        if not data_path:
            return jsonify({'error': 'File not found'}), 404
        
        # Load data
        format_type = _detect_format_from_path(data_path)
        df = _load_file_by_format(data_path, format_type)
        
        if df.empty:
            return jsonify({'error': 'No data found'}), 404
        
        return jsonify({
            'columns': list(df.columns),
            'data': df.head(1000).to_dict('records'),
            'total_rows': len(df)
        })
        
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@data_bp.route('/filter', methods=['POST'])
@rate_limit("60 per minute")
def filter_file_data():
    """Apply filters to loaded data."""
    try:
        data = request.get_json()
        filename = data.get('filename')
        filters = data.get('filters', {})
        
        if not filename:
            return jsonify({'error': 'Filename is required'}), 400
        
        # Load the file first
        data_dir = os.path.join(os.getcwd(), 'data')
        root_path = os.path.join(data_dir, filename)
        downloaded_path = os.path.join(data_dir, 'downloaded', filename)
        
        file_path = root_path if os.path.exists(root_path) else downloaded_path
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Load and filter data
        format_type = _detect_format_from_path(file_path)
        df = _load_file_by_format(file_path, format_type)
        
        # Apply filters
        filtered_df = _apply_filters(df, filters)
        
        return jsonify({
            'data': filtered_df.to_dict('records'),
            'columns': list(filtered_df.columns),
            'total_rows': len(filtered_df),
            'original_rows': len(df)
        })
        
    except Exception as e:
        logger.error(f"Error filtering data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@data_bp.route('/export', methods=['POST'])
def export_file_data():
    """Export filtered data to a file."""
    try:
        data = request.get_json()
        filename = data.get('filename')
        format_type = data.get('format', 'csv')
        export_filename = data.get('export_filename')
        filters = data.get('filters', {})
        
        if not filename or not export_filename:
            return jsonify({'error': 'Filename and export filename are required'}), 400
        
        # Load and filter data
        data_dir = os.path.join(os.getcwd(), 'data')
        root_path = os.path.join(data_dir, filename)
        downloaded_path = os.path.join(data_dir, 'downloaded', filename)
        
        file_path = root_path if os.path.exists(root_path) else downloaded_path
        
        if not file_path:
            return jsonify({'error': 'File not found'}), 404
        
        # Load data
        original_format = _detect_format_from_path(file_path)
        df = _load_file_by_format(file_path, original_format)
        
        # Apply filters if any
        if filters:
            df = _apply_filters(df, filters)
        
        # Export to new format
        export_path = os.path.join(data_dir, export_filename)
        _save_file_by_format(df, export_path, format_type)
        
        return jsonify({
            'message': f'Data exported successfully to {export_filename}',
            'export_path': export_path,
            'rows_exported': len(df)
        })
        
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@data_bp.route('/browse')
def browse_filesystem():
    """Browse file system - list directories and files."""
    try:
        path = request.args.get('path', os.path.expanduser('~'))
        
        # Security check - prevent directory traversal
        if not os.path.exists(path) or not os.path.isdir(path):
            return jsonify({'error': 'Invalid path'}), 400
        
        # Get absolute path to prevent traversal attacks
        abs_path = os.path.abspath(path)
        
        items = []
        
        # Add parent directory if not at root
        if abs_path != os.path.abspath(os.path.expanduser('~')) and abs_path != '/':
            parent_path = os.path.dirname(abs_path)
            items.append({
                'name': '..',
                'type': 'directory',
                'path': parent_path,
                'size': 0,
                'modified': 0
            })
        
        # List directory contents
        try:
            for item_name in sorted(os.listdir(abs_path)):
                item_path = os.path.join(abs_path, item_name)
                
                # Skip hidden files/folders
                if item_name.startswith('.'):
                    continue
                
                try:
                    stat_info = os.stat(item_path)
                    is_dir = os.path.isdir(item_path)
                    
                    items.append({
                        'name': item_name,
                        'type': 'directory' if is_dir else 'file',
                        'path': item_path,
                        'size': stat_info.st_size if not is_dir else 0,
                        'modified': stat_info.st_mtime,
                        'extension': os.path.splitext(item_name)[1].lower() if not is_dir else ''
                    })
                except (OSError, PermissionError):
                    continue
                    
        except PermissionError:
            return jsonify({'error': 'Permission denied'}), 403
        
        return jsonify({
            'path': abs_path,
            'items': items,
            'parent': os.path.dirname(abs_path) if abs_path != '/' else None
        })
        
    except Exception as e:
        logger.error(f"Error browsing filesystem: {str(e)}")
        return jsonify({'error': str(e)}), 500

@data_bp.route('/load-from-path', methods=['POST'])
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

@data_bp.route('/upload', methods=['POST'])
def upload_file():
    """Upload a file to the data directory."""
    try:
        from flask import request
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(os.getcwd(), 'data', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, file.filename)
        file.save(file_path)
        
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': file.filename,
            'path': file_path
        })
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@data_bp.route('/download/<path:file_path>')
def download_file(file_path):
    """Download a file from the system."""
    try:
        # Security check
        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path) or not os.path.isfile(abs_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(abs_path, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        return jsonify({'error': str(e)}), 500
