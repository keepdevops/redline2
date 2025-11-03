"""
Main routes for REDLINE Web GUI
Provides the main dashboard and navigation
"""

from flask import Blueprint, render_template, request, jsonify, session
import logging

main_bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

@main_bp.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')

@main_bp.route('/dashboard')
def dashboard():
    """Dashboard with overview of all tabs."""
    return render_template('dashboard.html')

@main_bp.route('/help')
def help_page():
    """Help and documentation page."""
    return render_template('help.html')

@main_bp.route('/status')
def status():
    """Get application status."""
    try:
        status_data = {
            'status': 'running',
            'data_loader': 'available',
            'database': 'available',
            'supported_formats': ['csv', 'txt', 'parquet', 'feather', 'json', 'duckdb'],
            'version': '1.1.0'
        }
        
        return jsonify(status_data)
        
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@main_bp.route('/health')
def health():
    """Health check endpoint for Docker."""
    return jsonify({'status': 'healthy', 'service': 'redline-web'})

@main_bp.route('/tasks')
def tasks_page():
    """Background tasks page."""
    return render_template('tasks_tab.html')

@main_bp.route('/data-modular')
def data_modular():
    """Modular data tab page."""
    return render_template('data_tab_modular.html')
