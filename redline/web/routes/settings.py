"""
Settings routes registry for REDLINE Web GUI
Handles application configuration and settings

This module now serves as a central registry for all settings blueprints.
Individual route modules are organized by functionality.
"""

from flask import Blueprint

# Import all settings blueprints
from .settings_config import settings_config_bp
from .settings_system import settings_system_bp
from .settings_database import settings_database_bp

# Main settings blueprint - registers all sub-blueprints
settings_bp = Blueprint('settings', __name__)

# Add route aliases to maintain backward compatibility with templates
from flask import render_template

@settings_bp.route('/', endpoint='settings_tab')
def settings_tab():
    """Alias for settings_config.settings_tab"""
    return render_template('settings_tab.html')

# Register all sub-blueprints with the main settings blueprint
# Use url_prefix to maintain route structure
settings_bp.register_blueprint(settings_config_bp, url_prefix='')
settings_bp.register_blueprint(settings_system_bp, url_prefix='')
settings_bp.register_blueprint(settings_database_bp, url_prefix='')
