"""
Converter routes for REDLINE Web GUI
Handles file format conversion operations

This module now serves as a central registry for all converter blueprints.
Individual route modules are organized by functionality.
"""

from flask import Blueprint

# Import all converter blueprints
from .converter_cleanup import converter_cleanup_bp
from .converter_tab import converter_tab_bp
from .converter_single import converter_single_bp
from .converter_batch import converter_batch_bp
from .converter_merge import converter_merge_bp
from .converter_browsing import converter_browsing_bp

# Main converter blueprint - registers all sub-blueprints
converter_bp = Blueprint('converter', __name__)

# Register all sub-blueprints with the main converter blueprint
# All use empty url_prefix so routes are registered directly under /converter
converter_bp.register_blueprint(converter_cleanup_bp)
converter_bp.register_blueprint(converter_tab_bp)
converter_bp.register_blueprint(converter_single_bp)
converter_bp.register_blueprint(converter_batch_bp)
converter_bp.register_blueprint(converter_merge_bp)
converter_bp.register_blueprint(converter_browsing_bp)
