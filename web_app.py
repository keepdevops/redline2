#!/usr/bin/env python3
"""
VarioSync Web Application Entry Point
Flask-based web interface for VarioSync application
"""

import os
import sys

# CRITICAL: Set CURL_IMPERSONATE=0 BEFORE any imports that use yfinance
# This fixes the "Impersonating chrome136 is not supported" error
os.environ['CURL_IMPERSONATE'] = '0'

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
        logging.FileHandler('variosync_web.log'),
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
        allowed_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:8081,http://127.0.0.1:8081').split(',')
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
    
    # Access control middleware - check JWT token and hours BEFORE processing request
    @app.before_request
    def check_access():
        """Validate JWT token from Supabase Auth"""
        from flask import jsonify

        # Skip auth for public endpoints
        public_endpoints = ('static', 'health', 'main.index', 'main.register',
                           'main.login', 'payments.webhook', 'payments.payment_tab',
                           'main.dashboard', 'main.help')

        public_paths = ['/api/register', '/api/login', '/api/status', '/health',
                       '/payments/webhook', '/static', '/register', '/login', '/help', '/']

        if request.endpoint in public_endpoints or request.path.startswith('/static'):
            return

        # Check if path is public
        for path in public_paths:
            if request.path.startswith(path):
                return

        # Extract JWT token from Authorization header
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'error': 'Authentication required',
                'message': 'Please provide Authorization: Bearer <token> header'
            }), 401

        token = auth_header.replace('Bearer ', '')

        try:
            # Validate JWT and extract user info
            from redline.auth.supabase_auth import supabase_auth
            user_data = supabase_auth.validate_jwt(token)
            g.user_id = user_data['user_id']
            g.email = user_data['email']

            # Check if user has hours remaining
            if os.environ.get('ENFORCE_PAYMENT', 'true').lower() == 'true':
                hours = supabase_auth.get_user_hours(g.user_id)
                if hours <= 0:
                    return jsonify({
                        'error': 'No hours remaining',
                        'message': 'Please purchase hours to continue using the service',
                        'hours_remaining': 0.0
                    }), 403

            logger.debug(f"Access granted for {request.path} with user {g.user_id}")

        except Exception as e:
            logger.error(f"JWT validation failed for {request.path}: {str(e)}")
            return jsonify({
                'error': 'Invalid authentication token',
                'message': str(e)
            }), 401
    
    # Usage tracking middleware (Gunicorn-compatible Flask decorator)
    @app.before_request
    def track_usage():
        """Track usage and deduct hours"""
        # Skip for public endpoints
        if not hasattr(g, 'user_id'):
            return

        user_id = g.user_id

        # Get or create session
        usage_tracker = app.config.get('usage_tracker')
        if not usage_tracker:
            return

        # Session-independent tracking using last_deduction_time dict
        from datetime import datetime
        now = datetime.now()
        last_deduction = usage_tracker.last_deduction_time.get(user_id)

        if last_deduction is None:
            # First request: create session
            session_id = usage_tracker.start_session(user_id)
            g.session_id = session_id
        else:
            # Check if deduction interval elapsed
            time_since = (now - last_deduction).total_seconds()
            check_interval = int(os.environ.get('USAGE_CHECK_INTERVAL', '30'))

            if time_since >= check_interval:
                hours_used = time_since / 3600.0
                # Deduct from Supabase
                from redline.auth.supabase_auth import supabase_auth
                supabase_auth.deduct_hours(user_id, hours_used)
                usage_tracker.last_deduction_time[user_id] = now

                # Log to DuckDB
                try:
                    from redline.database.usage_storage import usage_storage
                    if usage_storage:
                        usage_storage.log_hour_deduction(
                            user_id=user_id,
                            hours=hours_used,
                            session_id=g.get('session_id')
                        )
                except Exception as e:
                    logger.debug(f"Failed to log hour deduction: {str(e)}")

        # Log API access
        try:
            from redline.database.usage_storage import usage_storage
            if usage_storage:
                usage_storage.log_access(
                    user_id=user_id,
                    endpoint=request.endpoint or request.path,
                    method=request.method,
                    ip_address=request.remote_addr
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
    from redline.web.routes.ml import ml_bp
    from redline.web.routes.download import download_bp
    from redline.web.routes.converter import converter_bp
    from redline.web.routes.settings import settings_bp
    from redline.web.routes.tasks import tasks_bp
    from redline.web.routes.api_keys import api_keys_bp
    from redline.web.routes.payments import payments_bp
    from redline.web.routes.user_data import user_data_bp
    from redline.web.routes.s3_upload import s3_upload_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(data_bp, url_prefix='/data')
    app.register_blueprint(analysis_bp, url_prefix='/analysis')
    app.register_blueprint(ml_bp, url_prefix='/ml')
    app.register_blueprint(download_bp, url_prefix='/download')
    app.register_blueprint(converter_bp, url_prefix='/converter')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    app.register_blueprint(tasks_bp, url_prefix='/tasks')
    app.register_blueprint(api_keys_bp, url_prefix='/api-keys')
    app.register_blueprint(payments_bp, url_prefix='/payments')
    app.register_blueprint(user_data_bp, url_prefix='/user-data')
    app.register_blueprint(s3_upload_bp, url_prefix='/s3-upload')
    
    # Apply rate limits to specific routes after blueprint registration
    if limiter:
        from redline.web.routes.payments_balance import get_balance
        # Apply custom rate limit to balance endpoint
        get_balance = limiter.limit("1000 per hour")(get_balance)
        # Update the route with the rate-limited function
        payments_bp.view_functions['get_balance'] = get_balance
        
        # Apply generous rate limit to /api/files endpoint (read-only, frequently accessed)
        from redline.web.routes.api_files_list import api_list_files, api_files_list_bp
        api_list_files = limiter.limit("500 per hour")(api_list_files)
        # Update the route with the rate-limited function
        api_files_list_bp.view_functions['api_list_files'] = api_list_files
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500
    
    # Health check endpoint - very high rate limit (health checks are frequent)
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'service': 'redline-web'})
    
    # Apply high rate limit to health endpoint if limiter exists
    if limiter:
        health = limiter.limit("10000 per hour")(health)
    
    logger.info("VarioSync Web application created successfully")
    
    # Store socketio for potential use
    app.config['socketio'] = socketio
    
    # For Gunicorn, return only the app
    return app

def main():
    """Main entry point for the web application (development mode only)."""
    try:
        logger.info("Starting VarioSync Web Application...")
        
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
        logger.error(f"Failed to start VarioSync Web Application: {str(e)}")
        sys.exit(1)

# Create app instance for Gunicorn
app = create_app()

if __name__ == '__main__':
    main()
