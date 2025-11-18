"""
Data filtering routes for REDLINE Web GUI
Handles data filtering and export operations
"""

from flask import Blueprint, request, jsonify
import logging
import os
from ..utils.file_loading import (
    rate_limit,
    detect_format_from_path as _detect_format_from_path,
    load_file_by_format as _load_file_by_format,
    save_file_by_format as _save_file_by_format,
    apply_filters as _apply_filters
)

data_filtering_filter_bp = Blueprint('data_filtering_filter', __name__)
logger = logging.getLogger(__name__)

@data_filtering_filter_bp.route('/filter', methods=['POST'])
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

@data_filtering_filter_bp.route('/export', methods=['POST'])
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

