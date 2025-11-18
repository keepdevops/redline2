"""
Converter tab main page and format information routes.
"""

from flask import Blueprint, render_template, jsonify
import logging

converter_tab_bp = Blueprint('converter_tab', __name__)
logger = logging.getLogger(__name__)

@converter_tab_bp.route('/')
def converter_tab():
    """Converter tab main page."""
    return render_template('converter_tab.html')

@converter_tab_bp.route('/formats')
def get_formats():
    """Get supported input and output formats."""
    try:
        from redline.core.format_converter import FormatConverter
        converter = FormatConverter()
        
        formats = converter.get_supported_formats()
        
        format_info = {
            'csv': {
                'name': 'CSV',
                'description': 'Comma-separated values',
                'extension': '.csv',
                'readable': True,
                'writable': True
            },
            'txt': {
                'name': 'TXT',
                'description': 'Text file (tab-separated or comma-separated)',
                'extension': '.txt',
                'readable': True,
                'writable': True
            },
            'json': {
                'name': 'JSON',
                'description': 'JavaScript Object Notation',
                'extension': '.json',
                'readable': True,
                'writable': True
            },
            'parquet': {
                'name': 'Parquet',
                'description': 'Columnar storage format',
                'extension': '.parquet',
                'readable': True,
                'writable': True
            },
            'feather': {
                'name': 'Feather',
                'description': 'Fast columnar storage',
                'extension': '.feather',
                'readable': True,
                'writable': True
            },
            'duckdb': {
                'name': 'DuckDB',
                'description': 'Embedded analytical database',
                'extension': '.duckdb',
                'readable': True,
                'writable': True
            }
        }
        
        return jsonify({
            'formats': format_info,
            'supported': formats
        })
        
    except Exception as e:
        logger.error(f"Error getting formats: {str(e)}")
        return jsonify({'error': str(e)}), 500

