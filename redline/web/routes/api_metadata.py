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
    except AttributeError as e:
        logger.error(f"Pandas timestamp error getting status: {str(e)}")
        return jsonify({'error': 'Timestamp generation failed', 'code': 'TIMESTAMP_ERROR'}), 500
    except Exception as e:
        logger.error(f"Unexpected error getting status: {str(e)}")
        return jsonify({'error': 'Internal server error', 'code': 'INTERNAL_ERROR'}), 500


@api_metadata_bp.route('/formats', methods=['GET'])
def get_supported_formats():
    """Get supported file formats."""
    try:
        from redline.core.format_converter import FormatConverter
        converter = FormatConverter()
        formats = converter.get_supported_formats()

        return jsonify({'formats': formats})

    except ImportError as e:
        logger.error(f"Failed to import FormatConverter: {str(e)}")
        return jsonify({'error': 'Format converter not available', 'code': 'IMPORT_ERROR'}), 500
    except AttributeError as e:
        logger.error(f"Format converter method not found: {str(e)}")
        return jsonify({'error': 'Format operation failed', 'code': 'ATTRIBUTE_ERROR'}), 500
    except Exception as e:
        logger.error(f"Unexpected error getting formats: {str(e)}")
        return jsonify({'error': 'Internal server error', 'code': 'INTERNAL_ERROR'}), 500
