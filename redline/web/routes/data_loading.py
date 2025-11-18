"""
Data loading routes registry for REDLINE Web GUI
Handles file loading, uploading, and data import operations

This module now serves as a central registry for all data loading blueprints.
Individual route modules are organized by functionality.
"""

from flask import Blueprint

# Import all data loading blueprints
from .data_loading_single import data_loading_single_bp
from .data_loading_multiple import data_loading_multiple_bp

# Main data loading blueprint - registers all sub-blueprints
data_loading_bp = Blueprint('data_loading', __name__)

# Register all sub-blueprints with the main data loading blueprint
# Use url_prefix to maintain route structure
data_loading_bp.register_blueprint(data_loading_single_bp, url_prefix='')
data_loading_bp.register_blueprint(data_loading_multiple_bp, url_prefix='')
