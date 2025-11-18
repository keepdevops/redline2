"""
Data filtering routes registry for REDLINE Web GUI
Handles data filtering, export, and cleaning operations

This module now serves as a central registry for all data filtering blueprints.
Individual route modules are organized by functionality.
"""

from flask import Blueprint

# Import all data filtering blueprints
from .data_filtering_filter import data_filtering_filter_bp
from .data_filtering_clean import data_filtering_clean_bp

# Main data filtering blueprint - registers all sub-blueprints
data_filtering_bp = Blueprint('data_filtering', __name__)

# Register all sub-blueprints with the main data filtering blueprint
# Use url_prefix to maintain route structure
data_filtering_bp.register_blueprint(data_filtering_filter_bp, url_prefix='')
data_filtering_bp.register_blueprint(data_filtering_clean_bp, url_prefix='')
