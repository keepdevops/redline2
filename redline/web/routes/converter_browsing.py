"""
File browsing routes registry for converter operations.
Handles file system browsing, file listing, and file preview.

This module now serves as a central registry for all converter browsing blueprints.
Individual route modules are organized by functionality.
"""

from flask import Blueprint

# Import all converter browsing blueprints
from .converter_browsing_list import converter_browsing_list_bp
from .converter_browsing_browse import converter_browsing_browse_bp

# Main converter browsing blueprint - registers all sub-blueprints
converter_browsing_bp = Blueprint('converter_browsing', __name__)

# Register all sub-blueprints with the main converter browsing blueprint
# Use url_prefix to maintain route structure
converter_browsing_bp.register_blueprint(converter_browsing_list_bp, url_prefix='')
converter_browsing_bp.register_blueprint(converter_browsing_browse_bp, url_prefix='')
