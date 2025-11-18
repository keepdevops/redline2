"""
API routes for metadata operations.
Handles status, formats, themes, and font colors.
"""

from flask import Blueprint, request, jsonify
import logging
import pandas as pd
from .api_themes import api_themes_bp

api_metadata_bp = Blueprint('api_metadata', __name__)
logger = logging.getLogger(__name__)

# Register themes blueprint
api_metadata_bp.register_blueprint(api_themes_bp)


@api_metadata_bp.route('/status')
def get_status():
    """Get application status."""
    try:
        status = {
            'status': 'running',
            'version': '1.0.0',
            'database': 'available',
            'supported_formats': ['csv', 'json', 'parquet', 'feather', 'duckdb'],
            'timestamp': pd.Timestamp.now().isoformat()
        }
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_metadata_bp.route('/formats', methods=['GET'])
def get_supported_formats():
    """Get supported file formats."""
    try:
        from redline.core.format_converter import FormatConverter
        converter = FormatConverter()
        formats = converter.get_supported_formats()
        
        return jsonify({'formats': formats})
        
    except Exception as e:
        logger.error(f"Error getting formats: {str(e)}")
        return jsonify({'error': str(e)}), 500
