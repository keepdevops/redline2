#!/usr/bin/env python3
"""
REDLINE Web Application Entry Point - Safe Version
Flask-based web interface for REDLINE application with graceful error handling
"""

import os
import sys
import logging
import secrets
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
try:
    from flask_compress import Compress
    COMPRESS_AVAILABLE = True
except ImportError:
    COMPRESS_AVAILABLE = False
    print("Warning: flask-compress not available, compression disabled")

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
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'data', 'uploads')
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize SocketIO for real-time updates
    allowed_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:8080,http://127.0.0.1:8080').split(',')
    socketio = SocketIO(app, cors_allowed_origins=allowed_origins)
    
    # Initialize compression if available
    if COMPRESS_AVAILABLE:
        Compress(app)
    
    # Register blueprints (same as local web_app.py)
    from redline.web.routes.main import main_bp
    from redline.web.routes.api import api_bp
    from redline.web.routes.data import data_bp
    from redline.web.routes.analysis import analysis_bp
    from redline.web.routes.download import download_bp
    from redline.web.routes.converter import converter_bp
    from redline.web.routes.settings import settings_bp
    from redline.web.routes.tasks import tasks_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(data_bp, url_prefix='/data')
    app.register_blueprint(analysis_bp, url_prefix='/analysis')
    app.register_blueprint(download_bp, url_prefix='/download')
    app.register_blueprint(converter_bp, url_prefix='/converter')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    app.register_blueprint(tasks_bp, url_prefix='/tasks')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'service': 'redline-web'})
    
    # Simple test route
    @app.route('/test')
    def test():
        return jsonify({'message': 'Flask app is working!', 'blueprints': len(app.blueprints)})
    
    # Simple HTML test route
    @app.route('/simple')
    def simple():
        return '''
        <html>
        <head><title>REDLINE Test</title></head>
        <body>
            <h1>REDLINE Web GUI Test</h1>
            <p>Flask app is working!</p>
            <p>Blueprints registered: {}</p>
            <p><a href="/">Go to main page</a></p>
        </body>
        </html>
        '''.format(len(app.blueprints))
    
    logger.info("REDLINE Web application created successfully")
    return app, socketio

def main():
    """Main entry point for the web application."""
    try:
        logger.info("Starting REDLINE Web Application...")
        
        # Create application
        app, socketio = create_app()
        
        # Get configuration from environment - force 0.0.0.0 for Docker
        host = '0.0.0.0'  # Force bind to all interfaces for Docker
        port = int(os.environ.get('WEB_PORT', os.environ.get('PORT', 8080)))
        debug = os.environ.get('DEBUG', 'false').lower() == 'true'
        
        logger.info(f"Starting server on {host}:{port}")
        logger.info(f"Debug mode: {debug}")
        logger.info(f"Environment HOST: {os.environ.get('HOST', 'not set')}")
        logger.info(f"Environment WEB_PORT: {os.environ.get('WEB_PORT', 'not set')}")
        logger.info(f"Environment PORT: {os.environ.get('PORT', 'not set')}")
        
        # Start the application with proper production settings
        logger.info("Starting Flask-SocketIO server...")
        socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True, log_output=True)
        
    except Exception as e:
        logger.error(f"Failed to start REDLINE Web Application: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
