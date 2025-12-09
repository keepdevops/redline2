"""
Batch file conversion routes for REDLINE Web GUI.
Handles multiple file format conversion operations.
"""

from flask import Blueprint, request, jsonify
import logging
import os
import pandas as pd
import traceback
from ..utils.converter_helpers import find_input_file_path, adjust_output_filename, validate_file_before_conversion

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
                        error_msg = f'System files cannot be converted: {input_file}'
                        logger.warning(error_msg)
                        errors.append({
                            'input_file': input_file,
                            'error': error_msg,
                            'error_type': 'system_file'
                        })
                    else:
                        error_msg = f'Input file not found: {input_file}'
                        logger.warning(f"{error_msg} (searched in: {data_dir})")
                        errors.append({
                            'input_file': input_file,
                            'error': error_msg,
                            'error_type': 'file_not_found',
                            'searched_paths': [
                                os.path.join(data_dir, input_file),
                                os.path.join(data_dir, 'downloaded', input_file),
                                os.path.join(data_dir, 'stooq', input_file)
                            ]
                        })
                    continue
                
                # Detect format from file extension
                from redline.core.schema import EXT_TO_FORMAT
                ext = os.path.splitext(input_path)[1].lower()
                format_type = EXT_TO_FORMAT.get(ext, 'csv')
                
                # Validate file before conversion attempt
                logger.info(f"Validating file {input_file} before conversion...")
                is_valid, validation_error, validation_details = validate_file_before_conversion(
                    input_path, expected_format=format_type
                )
                
                if not is_valid:
                    error_msg = validation_error or 'File validation failed'
                    logger.error(f"File validation failed for {input_file}: {error_msg}")
                    logger.debug(f"Validation details: {validation_details}")
                    errors.append({
                        'input_file': input_file,
                        'error': error_msg,
                        'error_type': 'validation_failed',
                        'validation_details': validation_details
                    })
                    continue
                
                # Log validation success with details
                if validation_details.get('file_size'):
                    logger.info(f"File validation passed: {input_file} "
                              f"(size: {validation_details['file_size']} bytes, "
                              f"format: {format_type}, "
                              f"encoding: {validation_details.get('encoding', 'N/A')})")
                
                from redline.core.format_converter import FormatConverter
                converter = FormatConverter()
                
                # Load and convert
                logger.info(f"Loading file {input_file} as {format_type} format...")
                try:
                    data_obj = converter.load_file_by_type(input_path, format_type)
                except Exception as load_error:
                    error_msg = f"Error loading file: {str(load_error)}"
                    logger.error(f"Failed to load {input_file}: {error_msg}")
                    logger.debug(f"Load error traceback:\n{traceback.format_exc()}")
                    errors.append({
                        'input_file': input_file,
                        'error': error_msg,
                        'error_type': 'load_error',
                        'format_attempted': format_type,
                        'file_path': input_path,
                        'file_size': validation_details.get('file_size', 'unknown')
                    })
                    continue
                
                if data_obj is None:
                    error_msg = f"File loaded but returned None: {input_file}"
                    logger.error(error_msg)
                    errors.append({
                        'input_file': input_file,
                        'error': error_msg,
                        'error_type': 'empty_result',
                        'format_attempted': format_type,
                        'file_path': input_path,
                        'file_size': validation_details.get('file_size', 'unknown')
                    })
                    continue
                
                if hasattr(data_obj, 'empty') and data_obj.empty:
                    error_msg = f"File loaded but contains no data: {input_file}"
                    logger.warning(error_msg)
                    logger.debug(f"Data object type: {type(data_obj)}, shape: {getattr(data_obj, 'shape', 'N/A')}")
                    errors.append({
                        'input_file': input_file,
                        'error': error_msg,
                        'error_type': 'empty_data',
                        'format_attempted': format_type,
                        'file_path': input_path,
                        'file_size': validation_details.get('file_size', 'unknown')
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
                error_msg = str(e)
                logger.error(f"Unexpected error processing {file_config.get('input_file', 'unknown')}: {error_msg}")
                logger.debug(f"Exception traceback:\n{traceback.format_exc()}")
                errors.append({
                    'input_file': file_config.get('input_file', 'unknown'),
                    'error': error_msg,
                    'error_type': 'unexpected_error',
                    'exception_type': type(e).__name__
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

