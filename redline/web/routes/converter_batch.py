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
        
        logger.info(f"Batch conversion started: {len(files)} file(s)")
        
        if not files:
            return jsonify({'error': 'No files provided for conversion'}), 400
        
        results = []
        errors = []
        data_dir = os.path.join(os.getcwd(), 'data')
        
        for idx, file_config in enumerate(files, 1):
            try:
                input_file = file_config.get('input_file')
                output_format = file_config.get('output_format')
                output_filename = file_config.get('output_filename')
                
                logger.info(f"Processing file {idx}/{len(files)}: {input_file}")
                
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
                    # Check if it's a system file
                    from ..utils.converter_helpers import is_system_file
                    if is_system_file(os.path.basename(input_file)):
                        errors.append({
                            'input_file': input_file,
                            'error': 'System files cannot be converted'
                        })
                    else:
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
                
                logger.info(f"Loading file {input_file} as {format_type} format...")
                data_obj = converter.load_file_by_type(input_path, format_type)
                
                if data_obj is None or (hasattr(data_obj, 'empty') and data_obj.empty):
                    logger.warning(f"Failed to load or empty file: {input_file}")
                    errors.append({
                        'input_file': input_file,
                        'error': 'Failed to load input file or file is empty'
                    })
                    continue
                
                logger.info(f"Successfully loaded {input_file}: {len(data_obj)} rows")
                
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                logger.info(f"Saving converted file to {output_path}...")
                converter.save_file_by_type(data_obj, output_path, output_format)
                
                file_stat = os.stat(output_path)
                logger.info(f"Successfully converted {input_file} to {output_filename} ({file_stat.st_size} bytes)")
                
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
        
        logger.info(f"Batch conversion completed: {len(results)} successful, {len(errors)} failed")
        
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

