#!/usr/bin/env python3
"""
API Keys routes registry for REDLINE Web GUI
Helps users get free API keys for data sources

This module now serves as a central registry for all API keys blueprints.
Individual route modules are organized by functionality.
"""

from flask import Blueprint

# Import all API keys blueprints
from .api_keys_sources import api_keys_sources_bp
from .api_keys_management import api_keys_management_bp
from .api_keys_testing import api_keys_testing_bp

# Main API keys blueprint - registers all sub-blueprints
api_keys_bp = Blueprint('api_keys', __name__)

# Add route aliases to maintain backward compatibility with templates
from flask import render_template

@api_keys_bp.route('/', endpoint='api_keys_page')
def api_keys_page():
    """Alias for api_keys_management.api_keys_page"""
    return render_template('api_keys_page.html')

# Register all sub-blueprints with the main API keys blueprint
# Use url_prefix to maintain route structure
api_keys_bp.register_blueprint(api_keys_sources_bp, url_prefix='')
api_keys_bp.register_blueprint(api_keys_management_bp, url_prefix='')
api_keys_bp.register_blueprint(api_keys_testing_bp, url_prefix='')
