"""
Main index routes for REDLINE Web GUI
Provides the main dashboard and navigation pages
"""

from flask import Blueprint, render_template, jsonify, send_from_directory
import logging
import os

main_index_bp = Blueprint('main_index', __name__)
logger = logging.getLogger(__name__)

# Note: index, dashboard, and help_page routes are defined in main.py as aliases
# to maintain backward compatibility with templates using url_for('main.*')

@main_index_bp.route('/test-button-clicks')
def test_button_clicks():
    """Test page for verifying license key inclusion in API calls."""
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'redline', 'web', 'static')
    return send_from_directory(static_dir, 'test_button_clicks.html')

@main_index_bp.route('/status')
def status():
    """Get application status."""
    try:
        # Get actual supported formats from FormatConverter
        from redline.core.format_converter import FormatConverter
        converter = FormatConverter()
        supported_formats = converter.get_supported_formats()
        
        status_data = {
            'status': 'running',
            'data_loader': 'available',
            'database': 'available',
            'supported_formats': supported_formats,
            'version': '1.1.0'
        }
        
        return jsonify(status_data)
        
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@main_index_bp.route('/health')
def health():
    """Health check endpoint for Docker."""
    return jsonify({'status': 'healthy', 'service': 'redline-web'})

@main_index_bp.route('/tasks')
def tasks_page():
    """Background tasks page."""
    return render_template('tasks_tab.html')

@main_index_bp.route('/data-modular')
def data_modular():
    """Modular data tab page."""
    return render_template('data_tab_modular.html')

