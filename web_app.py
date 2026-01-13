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
# Check flask_compress availability using importlib
import importlib.util
flask_compress_spec = importlib.util.find_spec('flask_compress')
if flask_compress_spec is not None:
    from flask_compress import Compress
    COMPRESS_AVAILABLE = True
    logging.info("flask-compress is available and loaded")
else:
    COMPRESS_AVAILABLE = False
    logging.warning("flask-compress not available, compression disabled")

# Check flask_limiter availability using importlib
flask_limiter_spec = importlib.util.find_spec('flask_limiter')
if flask_limiter_spec is not None:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    LIMITER_AVAILABLE = True
    logging.info("flask-limiter is available and loaded")
else:
    LIMITER_AVAILABLE = False
    logging.warning("flask-limiter not available, rate limiting disabled")

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load .env file if it exists (before logging config to avoid issues)
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
dotenv_spec = importlib.util.find_spec('dotenv')

if dotenv_spec is not None:
    from dotenv import load_dotenv
    if os.path.exists(env_path):
        load_dotenv(env_path)
        logging.info(f"Loaded environment variables from {env_path} using python-dotenv")
    else:
        logging.debug(f".env file not found at {env_path}")
else:
    # python-dotenv not installed, try manual loading
    logging.info("python-dotenv not installed, attempting manual .env loading")
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
        logging.info(f"Manually loaded environment variables from {env_path}")
    else:
        logging.debug(f".env file not found at {env_path}")

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
    
    # Define MockSocketIO class for fallback
    class MockSocketIO:
        def __init__(self, app, **kwargs):
            self.app = app
        def run(self, app, host=None, port=None, debug=None, **kwargs):
            # Filter out unsupported parameters for Flask's app.run()
            flask_kwargs = {k: v for k, v in kwargs.items() 
                           if k not in ['allow_unsafe_werkzeug']}
            # Just run the Flask app directly
            self.app.run(host=host, port=port, debug=debug, **flask_kwargs)
    
    # Check if flask_socketio is available
    flask_socketio_spec = importlib.util.find_spec('flask_socketio')
    if flask_socketio_spec is None:
        logger.warning("flask_socketio module not available, using MockSocketIO")
        socketio = MockSocketIO(app)
    else:
        allowed_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:8080,http://127.0.0.1:8080').split(',')
        if not allowed_origins or allowed_origins == ['']:
            logger.warning("CORS_ORIGINS is empty, using default origins")
            allowed_origins = ['http://localhost:8080', 'http://127.0.0.1:8080']
        
        # Check if running under Gunicorn
        worker_class = os.environ.get('SERVER_SOFTWARE', '').startswith('gunicorn')
        async_mode = 'eventlet' if not worker_class else 'threading'
        
        # Validate async_mode choice
        if async_mode == 'eventlet':
            eventlet_spec = importlib.util.find_spec('eventlet')
            if eventlet_spec is None:
                logger.warning("eventlet not available, falling back to threading async_mode")
                async_mode = 'threading'
        
        socketio = SocketIO(app, cors_allowed_origins=allowed_origins, async_mode=async_mode)
        logger.info(f"SocketIO initialized with {async_mode} async_mode")
    
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
    task_manager_spec = importlib.util.find_spec('redline.background.task_manager')
    if task_manager_spec is not None:
        from redline.background.task_manager import TaskManager
        task_manager = TaskManager(app=app)
        if task_manager is not None:
            app.config['task_manager'] = task_manager
            logger.info("TaskManager initialized successfully")
        else:
            logger.warning("TaskManager initialization returned None")
            app.config['task_manager'] = None
    else:
        logger.warning("TaskManager module not available at redline.background.task_manager")
        app.config['task_manager'] = None
    
    # Initialize Supabase Auth Manager for JWT authentication
    auth_manager_spec = importlib.util.find_spec('redline.auth.supabase_auth')
    if auth_manager_spec is not None:
        from redline.auth.supabase_auth import auth_manager
        if auth_manager is not None:
            app.config['auth_manager'] = auth_manager
            if auth_manager.is_available():
                logger.info("Supabase Auth Manager initialized successfully")
            else:
                logger.warning("Supabase Auth Manager not fully configured (check environment variables)")
        else:
            logger.warning("auth_manager import returned None")
            app.config['auth_manager'] = None
    else:
        logger.warning("Supabase Auth module not available at redline.auth.supabase_auth")
        app.config['auth_manager'] = None

    # Access control middleware - check JWT token and subscription BEFORE processing request
    @app.before_request
    def check_access():
        """Check if user has valid JWT token and active subscription"""
        # Skip access control for public endpoints
        public_endpoints = ('static', 'health', 'register', 'payments.payment_tab',
                          'payments.packages', 'payments.create_checkout',
                          'payments.success', 'payments.cancel', 'payments.webhook',
                          'main.index', 'main.dashboard', 'main.help',
                          'auth.signup', 'auth.login', 'auth.logout', 'auth.status')

        # Public API paths (don't require authentication)
        public_api_paths = ['/api/register', '/api/status', '/health',
                           '/auth/signup', '/auth/login', '/auth/logout', '/auth/status',
                           '/payments/webhook', '/payments/subscription',
                           '/payments/subscription-success', '/payments/subscription-cancel']

        # Allow public endpoints
        if request.endpoint in public_endpoints or request.path.startswith('/static'):
            return

        if request.path in public_api_paths:
            return

        # Allow base HTML page routes (UI pages don't require auth)
        path = request.path.rstrip('/')
        base_html_routes = ['/data', '/analysis', '/download', '/converter',
                           '/tasks', '/settings', '/api-keys', '/payments']

        if path in base_html_routes:
            return  # Allow HTML pages without authentication

        # Exclude health/status endpoints
        if request.path in ['/health', '/tasks/health', '/api/status', '/status']:
            return

        # Public download endpoints (allow guest access)
        public_download_paths = ['/download/download', '/download/batch-download']
        if request.path in public_download_paths:
            return  # Allow downloads without authentication
        
        # Check if this is an API endpoint that requires authentication
        api_endpoints_requiring_auth = [
            '/api/files', '/api/upload', '/api/data',
            '/data/load', '/data/filter', '/data/files',
            '/analysis/analyze',
            '/user-data/',
            '/converter/convert', '/converter/batch-convert',
            '/tasks/list', '/tasks/queue', '/tasks/submit', '/tasks/cleanup', '/tasks/cancel',
            '/processing/upload', '/processing/jobs'
        ]

        # Check if this path matches any API endpoint
        is_api_endpoint = any(request.path.startswith(endpoint) for endpoint in api_endpoints_requiring_auth)

        # Also check for /api/* routes (but exclude public ones)
        if request.path.startswith('/api/') and request.path not in public_api_paths:
            is_api_endpoint = True

        # If it's not an API endpoint, allow it (it's an HTML page)
        if not is_api_endpoint:
            return

        # Get auth manager
        auth_mgr = app.config.get('auth_manager')
        if not auth_mgr:
            logger.error("Auth manager not initialized")
            return jsonify({
                'error': 'Authentication system not available',
                'code': 'AUTH_UNAVAILABLE'
            }), 500

        # Extract JWT token from request
        token = auth_mgr.extract_token_from_request(request)

        # Special case: /api/files can be called without auth (returns empty list)
        if request.path == '/api/files' and not token:
            logger.debug("/api/files called without token (public page)")
            return jsonify({'files': [], 'total': 0}), 200

        # Require token for all other API endpoints
        if not token:
            logger.warning(f"No JWT token provided for {request.path}")
            return jsonify({
                'error': 'Authentication required',
                'message': 'Please provide a valid JWT token in Authorization header or cookie',
                'code': 'NO_TOKEN'
            }), 401

        # Verify token and get user
        user = auth_mgr.get_user_from_token(token)

        if not user:
            logger.warning(f"Invalid or expired token for {request.path}")
            return jsonify({
                'error': 'Invalid or expired token',
                'message': 'Please log in again',
                'code': 'INVALID_TOKEN'
            }), 401

        # Check subscription status (skip if Stripe is disabled)
        subscription_status = user.get('subscription_status', 'inactive')
        
        # Check if Stripe is disabled or not configured
        stripe_disabled = os.environ.get('STRIPE_DISABLED', 'false').lower() in ('true', '1', 'yes')
        
        # Check Price ID validity
        metered_price_id = os.environ.get('STRIPE_PRICE_ID_METERED', '').strip()
        if '#' in metered_price_id:
            metered_price_id = metered_price_id.split('#')[0].strip()
        price_id_invalid = metered_price_id and not metered_price_id.startswith('price_')
        
        stripe_not_configured = (
            not os.environ.get('STRIPE_SECRET_KEY') or
            not metered_price_id or
            price_id_invalid
        )
        
        # Only enforce subscription requirement if Stripe is enabled and configured
        if not stripe_disabled and not stripe_not_configured:
            if subscription_status not in ['active', 'trialing']:
                logger.warning(f"User {user.get('email')} has inactive subscription: {subscription_status}")
                return jsonify({
                    'error': 'No active subscription',
                    'message': 'Please subscribe to access VarioSync',
                    'code': 'INACTIVE_SUBSCRIPTION',
                    'subscription_status': subscription_status
                }), 403
        else:
            # Stripe is disabled - allow access without subscription
            logger.debug(f"Stripe disabled/not configured - allowing access for user {user.get('email')} without subscription check")

        # Store user context in g for use in routes
        g.user_id = user['id']
        g.email = user['email']
        g.stripe_customer_id = user.get('stripe_customer_id')
        g.subscription_status = subscription_status
        g.user = user

        logger.debug(f"Authenticated user {g.email} for {request.path}")

    # Add cache headers to static files
    @app.after_request
    def add_response_headers(response):
        """Add cache control headers to responses."""
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
    from redline.web.routes.auth import auth_bp
    from redline.web.routes.processing import processing_bp

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
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(processing_bp, url_prefix='/processing')
    
    # Apply rate limits to specific routes after blueprint registration
    if limiter:
        # Exempt health check endpoints from rate limiting (Docker health checks are frequent)
        from redline.web.routes.main_index import health, status
        from redline.web.routes.tasks_status import health_check
        limiter.exempt(health)
        limiter.exempt(status)
        limiter.exempt(health_check)
        logger.info("Health check endpoints (/health, /status, /tasks/health) exempted from rate limiting")
        
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
    
    # Health check endpoint - exempted from rate limiting (defined in main_index blueprint)
    # The actual route is in redline.web.routes.main_index and is exempted above
    
    logger.info("VarioSync Web application created successfully")
    
    # Store socketio for potential use
    app.config['socketio'] = socketio
    
    # For Gunicorn, return only the app
    return app

def main():
    """Main entry point for the web application (development mode only)."""
    logger.info("Starting VarioSync Web Application...")
    
    # Validate environment configuration before creating app
    host = os.environ.get('HOST', '0.0.0.0')
    port_str = os.environ.get('WEB_PORT', os.environ.get('PORT', '8080'))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    # Validate port is a valid integer
    if not port_str.isdigit():
        logger.error(f"Invalid port value: {port_str}. Must be a numeric value.")
        sys.exit(1)
    
    port = int(port_str)
    
    # Validate port is in valid range
    if port < 1 or port > 65535:
        logger.error(f"Port {port} is out of valid range (1-65535)")
        sys.exit(1)
    
    # Create application
    app = create_app()
    if app is None:
        logger.error("Failed to create Flask application")
        sys.exit(1)
    
    socketio = app.config.get('socketio')
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    
    # Start the application (development mode with SocketIO)
    if socketio is not None and hasattr(socketio, 'run'):
        # Check if it's MockSocketIO (which handles allow_unsafe_werkzeug internally)
        is_mock = type(socketio).__name__ == 'MockSocketIO'
        
        if is_mock:
            # MockSocketIO filters out unsupported params
            logger.info("Using MockSocketIO for server startup")
            socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=(not debug))
        else:
            # Real SocketIO - check if allow_unsafe_werkzeug is supported
            import inspect
            run_signature = inspect.signature(socketio.run)
            supports_unsafe_werkzeug = 'allow_unsafe_werkzeug' in run_signature.parameters
            
            if not debug and supports_unsafe_werkzeug:
                logger.info("Starting SocketIO with allow_unsafe_werkzeug=True")
                socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
            else:
                logger.info("Starting SocketIO in standard mode")
                socketio.run(app, host=host, port=port, debug=debug)
    else:
        # Fallback to Flask dev server
        logger.info("SocketIO not available, using Flask development server")
        app.run(host=host, port=port, debug=debug)

# Create app instance for Gunicorn
app = create_app()

if __name__ == '__main__':
    main()
