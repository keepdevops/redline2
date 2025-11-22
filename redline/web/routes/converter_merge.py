"""
File merge routes for REDLINE Web GUI.
Handles merging multiple files into one during batch conversion.
"""

from flask import Blueprint, request, jsonify
import logging
import os
import pandas as pd
from ..utils.converter_helpers import (
    find_input_file_path, 
    adjust_output_filename,
    merge_dataframes
)

converter_merge_bp = Blueprint('converter_merge', __name__)
logger = logging.getLogger(__name__)

@converter_merge_bp.route('/batch-merge', methods=['POST'])
def batch_merge():
    """Merge multiple files into one during batch conversion."""
    try:
        data = request.get_json()
        files = data.get('files', [])
        output_format = data.get('output_format')
        output_filename = data.get('output_filename', 'merged_data')
        column_mappings = data.get('column_mappings', {})
        column_order = data.get('column_order')
        overwrite = data.get('overwrite', False)
        
        if not files:
            return jsonify({'error': 'No files provided for merge'}), 400
        
        if not output_format:
            return jsonify({'error': 'Output format is required'}), 400
        
        # Normalize format names (npz -> tensorflow for consistency)
        format_mapping = {
            'npz': 'tensorflow',
            'h5': 'keras',
            'arrow': 'pyarrow'
        }
        normalized_format = format_mapping.get(output_format.lower(), output_format.lower())
        
        data_dir = os.path.join(os.getcwd(), 'data')
        output_filename = adjust_output_filename(output_filename, normalized_format)
        output_path = os.path.join(data_dir, 'converted', output_filename)
        
        if os.path.exists(output_path) and not overwrite:
            return jsonify({
                'error': 'Output file already exists',
                'output_file': output_filename
            }), 400
        
        # Load all files
        from redline.core.format_converter import FormatConverter
        from redline.core.schema import EXT_TO_FORMAT
        
        converter = FormatConverter()
        dataframes = []
        loaded_files = []
        errors = []
        
        for file_info in files:
            try:
                input_file = file_info.get('input_file') if isinstance(file_info, dict) else file_info
                
                # Check if it's a system file
                from ..utils.converter_helpers import is_system_file
                if is_system_file(os.path.basename(input_file)):
                    errors.append({
                        'input_file': input_file,
                        'error': 'System files cannot be merged'
                    })
                    continue
                
                # Check in converted directory first (for merging converted files)
                converted_path = os.path.join(data_dir, 'converted', input_file)
                if os.path.exists(converted_path):
                    input_path = converted_path
                else:
                    input_path = find_input_file_path(input_file, data_dir)
                if not input_path or not os.path.exists(input_path):
                    errors.append({
                        'input_file': input_file,
                        'error': 'File not found'
                    })
                    continue
                
                ext = os.path.splitext(input_path)[1].lower()
                format_type = EXT_TO_FORMAT.get(ext, 'csv')
                
                # Skip system/config files that shouldn't be merged
                filename = os.path.basename(input_path)
                if filename in ['custom_apis.json', 'api_keys.json', 'data_config.ini', 'config.ini']:
                    errors.append({
                        'input_file': input_file,
                        'error': f'Skipping system/config file: {filename}'
                    })
                    continue
                
                data_obj = converter.load_file_by_type(input_path, format_type)
                if data_obj is None or (hasattr(data_obj, 'empty') and data_obj.empty):
                    errors.append({
                        'input_file': input_file,
                        'error': 'Failed to load file or file is empty'
                    })
                    continue
                
                if isinstance(data_obj, pd.DataFrame):
                    dataframes.append(data_obj)
                    loaded_files.append(input_file)
                else:
                    errors.append({
                        'input_file': input_file,
                        'error': 'Unsupported data type for merge'
                    })
                    
            except Exception as e:
                errors.append({
                    'input_file': file_info if isinstance(file_info, str) else file_info.get('input_file', 'unknown'),
                    'error': str(e)
                })
        
        if not dataframes:
            return jsonify({
                'error': 'No valid files could be loaded for merge',
                'errors': errors
            }), 400
        
        # Merge DataFrames
        try:
            # Parse column_order if it's a string (comma-separated)
            if column_order and isinstance(column_order, str):
                column_order = [col.strip() for col in column_order.split(',') if col.strip()]
            
            merged_df = merge_dataframes(dataframes, column_mappings, column_order=column_order)
            
            if merged_df.empty:
                return jsonify({
                    'error': 'Merged DataFrame is empty'
                }), 400
            
            # Save merged file
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Check if numpy is available for npz/tensorflow format
            if normalized_format in ('tensorflow', 'npz'):
                try:
                    import numpy as np
                except ImportError:
                    return jsonify({
                        'error': 'NumPy is required for .npz format but is not available',
                        'suggestion': 'Please install numpy: pip install numpy'
                    }), 500
            
            try:
                converter.save_file_by_type(merged_df, output_path, normalized_format)
            except Exception as save_error:
                logger.error(f"Error saving file to {output_path}: {str(save_error)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                return jsonify({
                    'error': f'Failed to save merged file: {str(save_error)}',
                    'output_format': normalized_format,
                    'errors': errors
                }), 500
            
            if not os.path.exists(output_path):
                return jsonify({
                    'error': 'File was not created after save operation',
                    'output_path': output_path,
                    'errors': errors
                }), 500
            
            file_stat = os.stat(output_path)
            
            return jsonify({
                'success': True,
                'message': f'Successfully merged {len(loaded_files)} files',
                'output_file': output_filename,
                'output_format': normalized_format,
                'file_size': file_stat.st_size,
                'total_records': len(merged_df),
                'columns': list(merged_df.columns),
                'loaded_files': loaded_files,
                'errors': errors
            })
            
        except Exception as e:
            logger.error(f"Error merging files: {str(e)}")
            return jsonify({
                'error': f'Failed to merge files: {str(e)}',
                'errors': errors
            }), 500
        
    except Exception as e:
        logger.error(f"Error in batch merge: {str(e)}")
        return jsonify({'error': str(e)}), 500

