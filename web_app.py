#!/usr/bin/env python3
"""
REDLINE Web Application Entry Point
Flask-based web interface for REDLINE application
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

try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    LIMITER_AVAILABLE = True
except ImportError:
    LIMITER_AVAILABLE = False
    print("Warning: flask-limiter not available, rate limiting disabled")

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
    # For PyInstaller compatibility, use threading mode explicitly
    try:
        allowed_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:8080,http://127.0.0.1:8080').split(',')
        socketio = SocketIO(app, cors_allowed_origins=allowed_origins, async_mode='threading')
        logger.info("SocketIO initialized with threading async_mode")
    except Exception as e:
        logger.warning(f"Failed to initialize SocketIO: {e}")
        # Fallback: create a mock SocketIO object
        class MockSocketIO:
            def __init__(self, app, **kwargs):
                self.app = app
            def run(self, app, host=None, port=None, debug=None, **kwargs):
                # Just run the Flask app directly
                self.app.run(host=host, port=port, debug=debug, **kwargs)
        socketio = MockSocketIO(app)
        logger.info("Using mock SocketIO for compatibility")
    
    # Initialize compression if available
    if COMPRESS_AVAILABLE:
        Compress(app)
    
    # Configure Jinja2 template caching for production
    app.jinja_env.auto_reload = False
    app.jinja_options = {
        'cache_size': 400,
        'auto_reload': False
    }
    
    # Initialize rate limiting if available
    limiter = None
    if LIMITER_AVAILABLE:
        # Use Redis if available, otherwise memory
        redis_url = os.environ.get('REDIS_URL')
        if redis_url:
            storage_uri = redis_url
            logger.info("Rate limiting using Redis storage")
        else:
            storage_uri = "memory://"
            logger.info("Rate limiting using in-memory storage")
        
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"],
            storage_uri=storage_uri,
            headers_enabled=True
        )
        logger.info("Rate limiting enabled")
    
    # Store limiter for blueprint access
    app.config['limiter'] = limiter
    
    # Initialize TaskManager for background tasks
    try:
        from redline.background.task_manager import TaskManager
        task_manager = TaskManager(app=app)
        app.config['task_manager'] = task_manager
        logger.info("TaskManager initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize TaskManager: {str(e)}")
        app.config['task_manager'] = None
    
    # Add cache headers to static files
    @app.after_request
    def add_cache_headers(response):
        """Add cache control headers to improve performance."""
        if request.endpoint != 'static':
            return response
        
        # Add cache headers for static files
        if '.min.' in request.path:
            # Minified files can be cached for 1 year
            response.cache_control.max_age = 31536000  # 1 year
            response.cache_control.public = True
            response.cache_control.immutable = True
        elif request.path.endswith(('.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico')):
            # Regular static files cached for 1 hour
            response.cache_control.max_age = 3600  # 1 hour
            response.cache_control.public = True
        
        return response
    
    # Register blueprints
    from redline.web.routes.main import main_bp
    from redline.web.routes.api import api_bp
    from redline.web.routes.data import data_bp
    from redline.web.routes.analysis import analysis_bp
    from redline.web.routes.download import download_bp
    from redline.web.routes.converter import converter_bp
    from redline.web.routes.settings import settings_bp
    from redline.web.routes.tasks import tasks_bp
    from redline.web.routes.api_keys import api_keys_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(data_bp, url_prefix='/data')
    app.register_blueprint(analysis_bp, url_prefix='/analysis')
    app.register_blueprint(download_bp, url_prefix='/download')
    app.register_blueprint(converter_bp, url_prefix='/converter')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    app.register_blueprint(tasks_bp, url_prefix='/tasks')
    app.register_blueprint(api_keys_bp, url_prefix='/api-keys')
    
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
    
    logger.info("REDLINE Web application created successfully")
    return app, socketio

def main():
    """Main entry point for the web application."""
    try:
        logger.info("Starting REDLINE Web Application...")
        
        # Create application
        app, socketio = create_app()
        
        # Get configuration from environment
        host = os.environ.get('HOST', '0.0.0.0')
        port = int(os.environ.get('WEB_PORT', os.environ.get('PORT', 8080)))
        debug = os.environ.get('DEBUG', 'false').lower() == 'true'
        
        logger.info(f"Starting server on {host}:{port}")
        logger.info(f"Debug mode: {debug}")
        
        # Start the application
        if not debug:
            # Allow Werkzeug to run in non-debug mode
            socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
        else:
            socketio.run(app, host=host, port=port, debug=debug)
        
    except Exception as e:
        logger.error(f"Failed to start REDLINE Web Application: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
