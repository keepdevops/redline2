"""
File browsing and listing routes for converter operations.
Handles file system browsing, file listing, and file preview.
"""

from flask import Blueprint, request, jsonify
import logging
import os
import pandas as pd

converter_browsing_bp = Blueprint('converter_browsing', __name__)
logger = logging.getLogger(__name__)

@converter_browsing_bp.route('/files')
def list_available_files():
    """List files available for conversion."""
    try:
        data_dir = os.path.join(os.getcwd(), 'data')
        files = []
        
        # List files in main data directory
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.endswith(('.csv', '.txt', '.json', '.parquet', '.feather', '.duckdb')):
                    file_path = os.path.join(data_dir, filename)
                    file_stat = os.stat(file_path)
                    files.append({
                        'name': filename,
                        'path': file_path,
                        'size': file_stat.st_size,
                        'modified': file_stat.st_mtime,
                        'location': 'data'
                    })
        
        # List files in downloaded directory
        downloaded_dir = os.path.join(data_dir, 'downloaded')
        if os.path.exists(downloaded_dir):
            for filename in os.listdir(downloaded_dir):
                if filename.endswith(('.csv', '.txt', '.json', '.parquet', '.feather', '.duckdb')):
                    file_path = os.path.join(downloaded_dir, filename)
                    file_stat = os.stat(file_path)
                    files.append({
                        'name': filename,
                        'path': file_path,
                        'size': file_stat.st_size,
                        'modified': file_stat.st_mtime,
                        'location': 'data/downloaded'
                    })
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({'files': files})
        
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return jsonify({'error': str(e)}), 500

@converter_browsing_bp.route('/converted-files')
def list_converted_files():
    """List previously converted files."""
    try:
        converted_dir = os.path.join(os.getcwd(), 'data', 'converted')
        files = []
        
        if os.path.exists(converted_dir):
            for filename in os.listdir(converted_dir):
                if filename.endswith(('.csv', '.txt', '.json', '.parquet', '.feather', '.duckdb')):
                    file_path = os.path.join(converted_dir, filename)
                    file_stat = os.stat(file_path)
                    files.append({
                        'name': filename,
                        'path': file_path,
                        'size': file_stat.st_size,
                        'modified': file_stat.st_mtime,
                        'location': 'data/converted'
                    })
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({'files': files})
        
    except Exception as e:
        logger.error(f"Error listing converted files: {str(e)}")
        return jsonify({'error': str(e)}), 500

@converter_browsing_bp.route('/home')
def get_home_directory():
    """Get user home directory path."""
    try:
        home_dir = os.path.expanduser('~')
        return jsonify({
            'home': home_dir,
            'downloads': os.path.join(home_dir, 'Downloads')
        })
    except Exception as e:
        logger.error(f"Error getting home directory: {str(e)}")
        return jsonify({'error': str(e)}), 500

@converter_browsing_bp.route('/browse')
def browse_filesystem():
    """Browse file system - list directories and files for file selection."""
    try:
        path = request.args.get('path', os.path.expanduser('~'))
        
        # Log for debugging
        logger.debug(f"Browsing path: {path}")
        
        # Security check - prevent directory traversal
        if not os.path.exists(path):
            logger.warning(f"Path does not exist: {path}")
            return jsonify({'error': f'Path does not exist: {path}'}), 400
            
        if not os.path.isdir(path):
            logger.warning(f"Path is not a directory: {path}")
            return jsonify({'error': f'Path is not a directory: {path}'}), 400
        
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
            dir_contents = os.listdir(abs_path)
            
            # If directory is empty, return empty list
            if not dir_contents:
                return jsonify({
                    'path': abs_path,
                    'items': []
                })
                
            for item_name in sorted(dir_contents):
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
                except (OSError, PermissionError) as e:
                    # Log but continue with other items
                    logger.debug(f"Cannot access {item_path}: {str(e)}")
                    continue
                    
        except PermissionError as e:
            logger.warning(f"Permission denied for directory {abs_path}: {str(e)}")
            return jsonify({
                'error': f'Permission denied: {str(e)}',
                'path': abs_path,
                'suggestion': 'Try a different directory or grant read permissions'
            }), 403
        
        return jsonify({
            'path': abs_path,
            'items': items
        })
        
    except Exception as e:
        logger.error(f"Error browsing filesystem: {str(e)}")
        return jsonify({'error': str(e)}), 500

@converter_browsing_bp.route('/preview/<filename>')
def preview_file(filename):
    """Preview file contents for conversion."""
    try:
        file_path = os.path.join(os.getcwd(), 'data', filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        from redline.core.format_converter import FormatConverter
        converter = FormatConverter()
        
        from redline.core.schema import EXT_TO_FORMAT
        
        # Detect format from file extension
        ext = os.path.splitext(file_path)[1].lower()
        format_type = EXT_TO_FORMAT.get(ext, 'csv')
        
        data = converter.load_file_by_type(file_path, format_type)
        
        if isinstance(data, pd.DataFrame):
            preview = {
                'type': 'dataframe',
                'columns': list(data.columns),
                'dtypes': data.dtypes.astype(str).to_dict(),
                'shape': {
                    'rows': int(data.shape[0]),
                    'columns': int(data.shape[1])
                },
                'sample_data': data.head(10).to_dict('records'),
                'null_counts': {k: int(v) for k, v in data.isnull().sum().to_dict().items()},
                'memory_usage': int(data.memory_usage(deep=True).sum())
            }
        else:
            preview = {
                'type': 'other',
                'content': str(data)[:1000],  # Truncate for large content
                'size': len(str(data))
            }
        
        return jsonify({
            'filename': filename,
            'preview': preview
        })
        
    except Exception as e:
        logger.error(f"Error previewing file {filename}: {str(e)}")
        return jsonify({'error': str(e)}), 500

