#!/usr/bin/env python3
"""
REDLINE Web Application Entry Point
Flask-based web interface for REDLINE application
"""

import os
import sys
import logging
import secrets
from flask import Flask, render_template, request, jsonify, g
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

# Load .env file if it exists (before logging config to avoid issues)
try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
except ImportError:
    # python-dotenv not installed, try manual loading
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove inline comments (everything after #)
                    if '#' in value:
                        value = value.split('#')[0].strip()
                    os.environ[key.strip()] = value.strip()
except Exception:
    pass  # Ignore errors loading .env

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
    app.config['ENV'] = os.environ.get('FLASK_ENV', 'production')  # Enable production mode for minified assets
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize SocketIO for real-time updates
    # For Gunicorn compatibility, use threading mode explicitly
    try:
        allowed_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:8080,http://127.0.0.1:8080').split(',')
        # Check if running under Gunicorn
        worker_class = os.environ.get('SERVER_SOFTWARE', '').startswith('gunicorn')
        async_mode = 'eventlet' if not worker_class else 'threading'
        socketio = SocketIO(app, cors_allowed_origins=allowed_origins, async_mode=async_mode)
        logger.info(f"SocketIO initialized with {async_mode} async_mode")
    except Exception as e:
        logger.warning(f"Failed to initialize SocketIO: {e}")
        # Fallback: create a mock SocketIO object
        class MockSocketIO:
            def __init__(self, app, **kwargs):
                self.app = app
            def run(self, app, host=None, port=None, debug=None, **kwargs):
                # Filter out unsupported parameters for Flask's app.run()
                flask_kwargs = {k: v for k, v in kwargs.items() 
                               if k not in ['allow_unsafe_werkzeug']}
                # Just run the Flask app directly
                self.app.run(host=host, port=port, debug=debug, **flask_kwargs)
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
    
    # Initialize Usage Tracker for time-based access
    try:
        from redline.auth.usage_tracker import usage_tracker
        app.config['usage_tracker'] = usage_tracker
        logger.info("Usage tracker initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize Usage Tracker: {str(e)}")
        app.config['usage_tracker'] = None
    
    # Access control middleware - check license and hours BEFORE processing request
    @app.before_request
    def check_access():
        """Check if user has valid license and sufficient hours"""
        # Skip access control for public endpoints
        public_endpoints = ('static', 'health', 'register', 'payments.payment_tab', 
                          'payments.packages', 'payments.create_checkout', 
                          'payments.success', 'payments.webhook', 'main.index',
                          'main.create_license_proxy')
        
        # Public API paths (don't require license)
        public_api_paths = ['/api/register', '/api/status', '/health']
        
        if request.endpoint in public_endpoints or request.path.startswith('/static') or request.path in public_api_paths:
            return
        
        # Get license key from request
        license_key = (
            request.headers.get('X-License-Key') or
            request.args.get('license_key') or
            (request.json.get('license_key') if request.is_json else None)
        )
        
        # For API endpoints, require license key
        if request.path.startswith('/api/') or request.path.startswith('/data/') or \
           request.path.startswith('/analysis/') or request.path.startswith('/download/'):
            if not license_key:
                from flask import jsonify
                return jsonify({
                    'error': 'License key is required',
                    'message': 'Please provide a license key in X-License-Key header, license_key query parameter, or JSON body'
                }), 401
            
            # Validate access
            try:
                from redline.auth.access_control import access_controller
                is_valid, error_msg, license_info = access_controller.validate_access(license_key)
                
                if not is_valid:
                    from flask import jsonify
                    return jsonify({
                        'error': error_msg or 'Access denied',
                        'code': 'INSUFFICIENT_HOURS' if 'hours' in (error_msg or '').lower() else 'INVALID_LICENSE'
                    }), 403
                
                # Store license info in g for use in request
                g.license_key = license_key
                g.license_info = license_info
            except ImportError:
                logger.warning("Access controller not available, skipping access check")
    
    # Usage tracking middleware (Gunicorn-compatible Flask decorator)
    @app.before_request
    def track_usage():
        """Track usage time for API requests"""
        # Skip tracking for static files and health checks
        if request.endpoint in ('static', 'health') or request.path.startswith('/static'):
            return
        
        # Get license key from request (header, session, or query param)
        license_key = (
            request.headers.get('X-License-Key') or
            request.args.get('license_key') or
            (request.json.get('license_key') if request.is_json else None) or
            getattr(g, 'license_key', None)  # Use from access control if available
        )
        
        if not license_key:
            return  # No license key, skip tracking
        
        # Get or create session
        usage_tracker = app.config.get('usage_tracker')
        if not usage_tracker:
            return
        
        # Get session ID from request or create new one
        session_id = request.headers.get('X-Session-ID')
        if not session_id:
            # Create new session (stored in response header)
            session_id = usage_tracker.start_session(license_key)
            # Store in g object for after_request
            g.session_id = session_id
        else:
            # Update existing session
            usage_tracker.update_session(session_id)
        
        # Log access to persistent storage
        try:
            from redline.database.usage_storage import usage_storage, STORAGE_AVAILABLE
            if STORAGE_AVAILABLE and usage_storage:
                usage_storage.log_access(
                    license_key=license_key,
                    endpoint=request.endpoint or request.path,
                    method=request.method,
                    session_id=session_id,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent')
                )
        except Exception as e:
            logger.debug(f"Failed to log access: {str(e)}")
    
    # Add cache headers to static files and session headers
    @app.after_request
    def add_response_headers(response):
        """Add cache control headers and session ID to responses."""
        # Add session ID header
        if hasattr(g, 'session_id'):
            response.headers['X-Session-ID'] = g.session_id
        
        # Add cache headers for static files
        if request.endpoint == 'static':
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
    from redline.web.routes.data_routes import data_bp
    from redline.web.routes.analysis import analysis_bp
    from redline.web.routes.download import download_bp
    from redline.web.routes.converter import converter_bp
    from redline.web.routes.settings import settings_bp
    from redline.web.routes.tasks import tasks_bp
    from redline.web.routes.api_keys import api_keys_bp
    from redline.web.routes.payments import payments_bp
    from redline.web.routes.user_data import user_data_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(data_bp, url_prefix='/data')
    app.register_blueprint(analysis_bp, url_prefix='/analysis')
    app.register_blueprint(download_bp, url_prefix='/download')
    app.register_blueprint(converter_bp, url_prefix='/converter')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    app.register_blueprint(tasks_bp, url_prefix='/tasks')
    app.register_blueprint(api_keys_bp, url_prefix='/api-keys')
    app.register_blueprint(payments_bp, url_prefix='/payments')
    app.register_blueprint(user_data_bp, url_prefix='/user-data')
    
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
    
    # Store socketio for potential use
    app.config['socketio'] = socketio
    
    # For Gunicorn, return only the app
    return app

def main():
    """Main entry point for the web application (development mode only)."""
    try:
        logger.info("Starting REDLINE Web Application...")
        
        # Create application
        app = create_app()
        socketio = app.config.get('socketio')
        
        # Get configuration from environment
        host = os.environ.get('HOST', '0.0.0.0')
        port = int(os.environ.get('WEB_PORT', os.environ.get('PORT', 8080)))
        debug = os.environ.get('DEBUG', 'false').lower() == 'true'
        
        logger.info(f"Starting server on {host}:{port}")
        logger.info(f"Debug mode: {debug}")
        
        # Start the application (development mode with SocketIO)
        if socketio and hasattr(socketio, 'run'):
            # Check if it's MockSocketIO (which handles allow_unsafe_werkzeug internally)
            is_mock = type(socketio).__name__ == 'MockSocketIO'
            
            if is_mock:
                # MockSocketIO filters out unsupported params
                socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=(not debug))
            else:
                # Real SocketIO - try with allow_unsafe_werkzeug for non-debug
                try:
                    if not debug:
                        socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
                    else:
                        socketio.run(app, host=host, port=port, debug=debug)
                except TypeError:
                    # If allow_unsafe_werkzeug not supported, run without it
                    socketio.run(app, host=host, port=port, debug=debug)
        else:
            # Fallback to Flask dev server
            app.run(host=host, port=port, debug=debug)
        
    except Exception as e:
        logger.error(f"Failed to start REDLINE Web Application: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
