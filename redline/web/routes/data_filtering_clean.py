"""
Data cleaning routes for REDLINE Web GUI
Handles data cleaning operations
"""

from flask import Blueprint, request, jsonify
import logging
import os
import pandas as pd
from ..utils.file_loading import (
    rate_limit,
    detect_format_from_path as _detect_format_from_path,
    load_file_by_format as _load_file_by_format,
    save_file_by_format as _save_file_by_format
)
from ..utils.data_helpers import clean_dataframe_columns

data_filtering_clean_bp = Blueprint('data_filtering_clean', __name__)
logger = logging.getLogger(__name__)

@data_filtering_clean_bp.route('/clean', methods=['POST'])
@rate_limit("10 per minute")
def clean_data():
    """Clean data: remove duplicates and handle missing values."""
    try:
        from redline.core.data_cleaner import DataCleaner
        
        data = request.get_json()
        filename = data.get('filename')
        remove_duplicates = data.get('remove_duplicates', True)
        handle_missing = data.get('handle_missing', 'drop')  # 'drop', 'forward_fill', 'backward_fill'
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        # Load the file
        data_dir = os.path.join(os.getcwd(), 'data')
        file_path = None
        
        # Search for file in data directories
        search_paths = [
            os.path.join(data_dir, filename),
            os.path.join(data_dir, 'downloaded', filename),
            os.path.join(data_dir, 'stooq', filename),
            os.path.join(data_dir, 'uploads', filename)
        ]
        
        # Search in converted directory recursively
        converted_dir = os.path.join(data_dir, 'converted')
        if os.path.exists(converted_dir):
            direct_path = os.path.join(converted_dir, filename)
            if os.path.exists(direct_path) and os.path.isfile(direct_path):
                search_paths.append(direct_path)
            else:
                for root, dirs, files in os.walk(converted_dir):
                    if filename in files:
                        search_paths.append(os.path.join(root, filename))
                        break
        
        # Find the file
        for path in search_paths:
            if os.path.exists(path) and os.path.isfile(path):
                file_path = path
                break
        
        if not file_path:
            return jsonify({
                'error': 'File not found',
                'message': f'File "{filename}" not found in data directories'
            }), 404
        
        # Load data
        format_type = _detect_format_from_path(file_path)
        df = _load_file_by_format(file_path, format_type)
        
        if df.empty:
            return jsonify({
                'error': 'No data found',
                'message': f'The file "{filename}" contains no data'
            }), 404
        
        original_rows = len(df)
        stats = {}
        
        # Initialize cleaner
        cleaner = DataCleaner()
        
        # Remove duplicates
        if remove_duplicates:
            df_before = len(df)
            # Determine subset for duplicate detection (flexible column detection)
            from ..utils.analysis_helpers import detect_ticker_column, detect_timestamp_column
            ticker_col = detect_ticker_column(df)
            timestamp_col = detect_timestamp_column(df)
            
            subset = None
            if ticker_col and timestamp_col:
                subset = [ticker_col, timestamp_col]
            elif timestamp_col:
                subset = [timestamp_col]
            df = cleaner.remove_duplicates(df, subset=subset)
            duplicates_removed = df_before - len(df)
            stats['duplicates_removed'] = duplicates_removed
        
        # Handle missing values
        if handle_missing and handle_missing != 'none':
            df_before = len(df)
            df = cleaner.handle_missing_values(df, strategy=handle_missing)
            missing_handled = df_before - len(df)
            stats['missing_handled'] = missing_handled
        
        # Clean column names
        df = clean_dataframe_columns(df)
        
        # Convert to JSON-serializable format
        cleaned_data = df.head(1000).to_dict('records')
        
        return jsonify({
            'success': True,
            'filename': filename,
            'columns': list(df.columns),
            'data': cleaned_data,
            'total_rows': len(df),
            'original_rows': original_rows,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error cleaning data: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@data_filtering_clean_bp.route('/save-cleaned', methods=['POST'])
@rate_limit("10 per minute")
def save_cleaned_data():
    """Save cleaned data to a new file."""
    try:
        data = request.get_json()
        filename = data.get('filename')
        cleaned_data = data.get('data')
        columns = data.get('columns', [])
        
        if not filename or not cleaned_data:
            return jsonify({'error': 'Filename and data are required'}), 400
        
        # Create DataFrame from cleaned data
        df = pd.DataFrame(cleaned_data)
        
        # Ensure columns are in correct order if provided
        if columns and len(columns) == len(df.columns):
            df = df[columns]
        
        # Determine save location and format
        data_dir = os.path.join(os.getcwd(), 'data')
        save_dir = os.path.join(data_dir, 'converted')
        os.makedirs(save_dir, exist_ok=True)
        
        save_path = os.path.join(save_dir, filename)
        
        # Detect format from extension
        format_type = _detect_format_from_path(save_path)
        
        # Save file
        _save_file_by_format(df, save_path, format_type)
        
        logger.info(f"Saved cleaned data to: {save_path}")
        
        return jsonify({
            'success': True,
            'message': f'Cleaned data saved as "{filename}"',
            'filename': filename,
            'path': save_path,
            'rows': len(df)
        })
        
    except Exception as e:
        logger.error(f"Error saving cleaned data: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

