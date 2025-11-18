"""
Data routes for REDLINE Web GUI
Route handlers for data viewing, filtering, and management

This module now serves as a central registry for all data blueprints.
Individual route modules are organized by functionality.
"""

from flask import Blueprint

# Import all data blueprints
from .data_tab import data_tab_bp
from .data_loading import data_loading_bp
from .data_filtering import data_filtering_bp
from .data_browsing import data_browsing_bp

# Main data blueprint - registers all sub-blueprints
data_bp = Blueprint('data', __name__)

# Register all sub-blueprints with the main data blueprint
# Use url_prefix to maintain route structure
data_bp.register_blueprint(data_tab_bp, url_prefix='')
data_bp.register_blueprint(data_loading_bp, url_prefix='')
data_bp.register_blueprint(data_filtering_bp, url_prefix='')
data_bp.register_blueprint(data_browsing_bp, url_prefix='')
