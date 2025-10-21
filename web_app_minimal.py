#!/usr/bin/env python3
"""
REDLINE Web Application Entry Point - Minimal Test Version
Flask-based web interface for REDLINE application
"""

import os
import sys
import logging
from flask import Flask, render_template, request, jsonify

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('redline_web.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, 
                template_folder='redline/web/templates',
                static_folder='redline/web/static')
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'redline-secret-key-2024')
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'data', 'uploads')
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Simple test route
    @app.route('/')
    def index():
        return jsonify({
            'status': 'success',
            'message': 'REDLINE Web GUI is running!',
            'version': '1.0.0'
        })
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'})
    
    logger.info("Flask app created successfully")
    return app

if __name__ == '__main__':
    app = create_app()
    logger.info("Starting REDLINE Web GUI...")
    app.run(host='0.0.0.0', port=8080, debug=True)
