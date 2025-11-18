"""
Main routes registry for REDLINE Web GUI
Provides the main dashboard and navigation

This module now serves as a central registry for all main blueprints.
Individual route modules are organized by functionality.
"""

from flask import Blueprint

# Import all main blueprints
from .main_index import main_index_bp
from .main_auth import main_auth_bp

# Main blueprint - registers all sub-blueprints
main_bp = Blueprint('main', __name__)

# Register all sub-blueprints with the main blueprint FIRST
# Use url_prefix to maintain route structure
main_bp.register_blueprint(main_index_bp, url_prefix='')
main_bp.register_blueprint(main_auth_bp, url_prefix='')

# Add route aliases AFTER sub-blueprints to override and maintain backward compatibility
# These routes will be accessible as 'main.index', 'main.dashboard', etc.
# This ensures templates using url_for('main.index') continue to work
from flask import render_template

@main_bp.route('/', endpoint='index')
def index():
    """Alias for main_index.index - maintains backward compatibility"""
    return render_template('index.html')

@main_bp.route('/dashboard', endpoint='dashboard')
def dashboard():
    """Alias for main_index.dashboard - maintains backward compatibility"""
    return render_template('dashboard.html')

@main_bp.route('/register', endpoint='register')
def register():
    """Alias for main_auth.register - maintains backward compatibility"""
    return render_template('register.html')

@main_bp.route('/help', endpoint='help_page')
def help_page():
    """Alias for main_index.help_page - maintains backward compatibility"""
    return render_template('help.html')
