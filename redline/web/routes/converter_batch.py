"""
Batch file conversion routes for REDLINE Web GUI.
Handles multiple file format conversion operations.
"""

from flask import Blueprint, request, jsonify
import logging
import os
import pandas as pd
from ..utils.converter_helpers import find_input_file_path, adjust_output_filename

converter_batch_bp = Blueprint('converter_batch', __name__)
logger = logging.getLogger(__name__)

@converter_batch_bp.route('/batch-convert', methods=['POST'])
def batch_convert():
    """Convert multiple files in batch."""
    try:
        data = request.get_json()
        files = data.get('files', [])  # List of {input_file, output_format, output_filename}
        overwrite = data.get('overwrite', False)
        
        if not files:
            return jsonify({'error': 'No files provided for conversion'}), 400
        
        results = []
        errors = []
        data_dir = os.path.join(os.getcwd(), 'data')
        
        for file_config in files:
            try:
                input_file = file_config.get('input_file')
                output_format = file_config.get('output_format')
                output_filename = file_config.get('output_filename')
                
                if not all([input_file, output_format, output_filename]):
                    errors.append({
                        'input_file': input_file,
                        'error': 'Missing required parameters'
                    })
                    continue
                
                # Adjust output filename extension
                output_filename = adjust_output_filename(output_filename, output_format)
                
                # Check if output file exists
                output_path = os.path.join(data_dir, 'converted', output_filename)
                
                if os.path.exists(output_path) and not overwrite:
                    errors.append({
                        'input_file': input_file,
                        'output_file': output_filename,
                        'error': 'Output file already exists'
                    })
                    continue
                
                # Find input file path
                input_path = find_input_file_path(input_file, data_dir)
                
                # Log debugging info
                logger.debug(f"Input file search: {input_file}")
                
                if not input_path or not os.path.exists(input_path):
                    error_msg = f'Input file not found: {input_file}'
                    logger.warning(error_msg)
                    errors.append({
                        'input_file': input_file,
                        'error': error_msg
                    })
                    continue
                
                from redline.core.format_converter import FormatConverter
                converter = FormatConverter()
                
                # Load and convert
                from redline.core.schema import EXT_TO_FORMAT
                
                # Detect format from file extension
                ext = os.path.splitext(input_path)[1].lower()
                format_type = EXT_TO_FORMAT.get(ext, 'csv')
                
                data_obj = converter.load_file_by_type(input_path, format_type)
                
                if data_obj is None or (hasattr(data_obj, 'empty') and data_obj.empty):
                    errors.append({
                        'input_file': input_file,
                        'error': 'Failed to load input file'
                    })
                    continue
                
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                converter.save_file_by_type(data_obj, output_path, output_format)
                
                file_stat = os.stat(output_path)
                
                results.append({
                    'input_file': input_file,
                    'output_file': output_filename,
                    'output_format': output_format,
                    'file_size': file_stat.st_size,
                    'records': len(data_obj) if isinstance(data_obj, pd.DataFrame) else 0,
                    'success': True
                })
                
            except Exception as e:
                errors.append({
                    'input_file': file_config.get('input_file', 'unknown'),
                    'error': str(e)
                })
        
        return jsonify({
            'message': f'Batch conversion completed. {len(results)} successful, {len(errors)} failed.',
            'results': results,
            'errors': errors,
            'total_files': len(files),
            'successful': len(results),
            'failed': len(errors)
        })
        
    except Exception as e:
        logger.error(f"Error in batch conversion: {str(e)}")
        return jsonify({'error': str(e)}), 500

