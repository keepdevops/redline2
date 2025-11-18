"""
API routes for file conversion operations.
Handles format conversion between different file types.
"""

from flask import Blueprint, request, jsonify
import logging
import os
import pandas as pd
from ..utils.api_helpers import rate_limit

api_convert_bp = Blueprint('api_convert', __name__)
logger = logging.getLogger(__name__)


@api_convert_bp.route('/convert', methods=['POST'])
@rate_limit("20 per hour")
def convert_file():
    """Convert file between formats."""
    try:
        data = request.get_json()
        input_file = data.get('input_file')
        output_format = data.get('output_format')
        output_file = data.get('output_file')
        
        if not all([input_file, output_format, output_file]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        from redline.core.format_converter import FormatConverter
        from redline.core.schema import EXT_TO_FORMAT
        converter = FormatConverter()
        
        # Determine input file path - check both root data directory and downloaded subdirectory
        data_dir = os.path.join(os.getcwd(), 'data')
        input_path = None
        
        # Check in root data directory first
        root_path = os.path.join(data_dir, input_file)
        if os.path.exists(root_path):
            input_path = root_path
        else:
            # Check in downloaded directory
            downloaded_path = os.path.join(data_dir, 'downloaded', input_file)
            if os.path.exists(downloaded_path):
                input_path = downloaded_path
        
        if not input_path or not os.path.exists(input_path):
            return jsonify({'error': 'Input file not found'}), 404
        
        # Detect format from file extension
        ext = os.path.splitext(input_path)[1].lower()
        format_type = EXT_TO_FORMAT.get(ext, 'csv')
        
        # Load data
        data_obj = converter.load_file_by_type(input_path, format_type)
        
        # Aggressive cleaning during conversion: clean column names, remove unnamed columns, etc.
        if isinstance(data_obj, pd.DataFrame):
            from redline.web.utils.data_helpers import clean_dataframe_columns
            try:
                data_obj = clean_dataframe_columns(data_obj)
                logger.info(f"Cleaned columns during API conversion")
            except Exception as clean_error:
                logger.warning(f"Error during column cleaning (non-fatal): {str(clean_error)}")
                # Continue with conversion anyway
        
        # Convert and save
        converter.save_file_by_type(data_obj, output_file, output_format)
        
        return jsonify({
            'message': 'File converted successfully',
            'output_file': output_file
        })
        
    except Exception as e:
        logger.error(f"Error converting file: {str(e)}")
        return jsonify({'error': str(e)}), 500

