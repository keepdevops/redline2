"""
Single file conversion routes for REDLINE Web GUI.
Handles individual file format conversion operations.
"""

from flask import Blueprint, request, jsonify
import logging
import os
import pandas as pd
from ..utils.converter_helpers import find_input_file_path, adjust_output_filename

converter_single_bp = Blueprint('converter_single', __name__)
logger = logging.getLogger(__name__)

@converter_single_bp.route('/convert', methods=['POST'])
def convert_file():
    """Convert file between formats."""
    try:
        data = request.get_json()
        input_file = data.get('input_file')
        output_format = data.get('output_format')
        output_filename = data.get('output_filename')
        overwrite = data.get('overwrite', False)
        
        logger.info(f"Convert request: input_file={input_file}, output_format={output_format}, output_filename={output_filename}, overwrite={overwrite}")
        
        if not all([input_file, output_format, output_filename]):
            logger.error(f"Missing required parameters: input_file={input_file}, output_format={output_format}, output_filename={output_filename}")
            return jsonify({
                'error': 'Missing required parameters',
                'details': {
                    'input_file': input_file,
                    'output_format': output_format,
                    'output_filename': output_filename
                }
            }), 400
        
        # Ensure output filename has the correct extension
        output_filename = adjust_output_filename(output_filename, output_format)
        
        # Check if output file exists and overwrite is not allowed
        output_path = os.path.join(os.getcwd(), 'data', 'converted', output_filename)
        
        if os.path.exists(output_path) and not overwrite:
            return jsonify({
                'error': 'Output file already exists',
                'output_file': output_filename,
                'suggestion': 'Set overwrite to true or choose a different filename'
            }), 400
        
        # Find input file path
        data_dir = os.path.join(os.getcwd(), 'data')
        input_path = find_input_file_path(input_file, data_dir)
        
        if not input_path or not os.path.exists(input_path):
            return jsonify({'error': 'Input file not found'}), 404
        
        from redline.core.format_converter import FormatConverter
        converter = FormatConverter()
        
        # Load data
        logger.info(f"Loading data from {input_file}")
        from redline.core.schema import EXT_TO_FORMAT
        
        # Validate output format
        supported_formats = converter.get_supported_formats()
        logger.info(f"Supported formats: {supported_formats}")
        logger.info(f"Requested output format: {output_format}")
        
        if output_format not in supported_formats:
            logger.error(f"Unsupported output format: {output_format}")
            return jsonify({
                'error': 'Unsupported output format',
                'details': f'Format "{output_format}" is not supported. Supported formats: {", ".join(supported_formats)}',
                'supported_formats': supported_formats
            }), 400
        
        # Detect format from file extension
        ext = os.path.splitext(input_path)[1].lower()
        format_type = EXT_TO_FORMAT.get(ext, 'csv')
        
        data_obj = converter.load_file_by_type(input_path, format_type)
        
        if data_obj is None or (hasattr(data_obj, 'empty') and data_obj.empty):
            logger.error(f"Failed to load data from {input_path}")
            return jsonify({
                'error': 'Failed to load input file',
                'details': f'Could not load data from {input_file} as {format_type} format'
            }), 400
        
        # Apply data cleaning options if provided
        remove_duplicates = data.get('remove_duplicates', False)
        handle_missing = data.get('handle_missing', 'none')
        clean_column_names = data.get('clean_column_names', False)
        
        original_rows = len(data_obj) if isinstance(data_obj, pd.DataFrame) else 0
        cleaning_stats = {}
        
        if isinstance(data_obj, pd.DataFrame):
            # Remove duplicates
            if remove_duplicates:
                from redline.core.data_cleaner import DataCleaner
                cleaner = DataCleaner()
                df_before = len(data_obj)
                # Determine subset for duplicate detection
                subset = None
                if 'ticker' in data_obj.columns and 'timestamp' in data_obj.columns:
                    subset = ['ticker', 'timestamp']
                elif 'timestamp' in data_obj.columns:
                    subset = ['timestamp']
                data_obj = cleaner.remove_duplicates(data_obj, subset=subset)
                duplicates_removed = df_before - len(data_obj)
                cleaning_stats['duplicates_removed'] = duplicates_removed
                logger.info(f"Removed {duplicates_removed} duplicate rows")
            
            # Handle missing values
            if handle_missing and handle_missing != 'none':
                from redline.core.data_cleaner import DataCleaner
                cleaner = DataCleaner()
                df_before = len(data_obj)
                data_obj = cleaner.handle_missing_values(data_obj, strategy=handle_missing)
                missing_handled = df_before - len(data_obj)
                cleaning_stats['missing_handled'] = missing_handled
                logger.info(f"Handled missing values using {handle_missing} strategy, {missing_handled} rows affected")
            
            # Clean column names
            if clean_column_names:
                from redline.web.utils.data_helpers import clean_dataframe_columns
                data_obj = clean_dataframe_columns(data_obj)
                logger.info("Cleaned column names")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save in new format
        logger.info(f"Converting to {output_format} format")
        try:
            converter.save_file_by_type(data_obj, output_path, output_format)
        except Exception as save_error:
            logger.error(f"Failed to save converted file: {str(save_error)}")
            return jsonify({
                'error': 'Failed to save converted file',
                'details': str(save_error)
            }), 400
        
        # Get file info
        file_stat = os.stat(output_path)
        
        # Save to user storage if license key provided
        license_key = (
            request.headers.get('X-License-Key') or
            request.args.get('license_key') or
            data.get('license_key')
        )
        
        user_file_id = None
        if license_key:
            try:
                from redline.storage.user_storage import user_storage, STORAGE_AVAILABLE
                if STORAGE_AVAILABLE and user_storage:
                    # Read converted file
                    with open(output_path, 'rb') as f:
                        file_data = f.read()
                    
                    # Save to user storage
                    file_info = user_storage.save_file(
                        license_key=license_key,
                        file_data=file_data,
                        filename=output_filename,
                        file_type=output_format,
                        metadata={
                            'converted_from': input_file,
                            'original_format': format_type,
                            'converted_via': 'web_converter',
                            'records': len(data_obj) if isinstance(data_obj, pd.DataFrame) else 0
                        }
                    )
                    user_file_id = file_info.get('file_id')
                    logger.info(f"Saved converted file to user storage for license {license_key[:8]}...")
            except Exception as e:
                logger.warning(f"Failed to save to user storage: {str(e)}")
                # Don't fail the conversion if storage fails
        
        result = {
            'message': 'File converted successfully',
            'input_file': input_file,
            'output_file': output_filename,
            'output_format': output_format,
            'output_path': output_path,
            'file_size': file_stat.st_size,
            'records': len(data_obj) if isinstance(data_obj, pd.DataFrame) else 0,
            'original_records': original_rows,
            'user_file_id': user_file_id,  # ID in user storage if saved
            'cleaning_applied': remove_duplicates or (handle_missing and handle_missing != 'none') or clean_column_names,
            'cleaning_stats': cleaning_stats
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error converting file: {str(e)}")
        return jsonify({'error': str(e)}), 500

