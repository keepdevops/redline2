"""
API routes registry for file operations.
Handles file listing, upload, and deletion.

This module now serves as a central registry for all API file blueprints.
Individual route modules are organized by functionality.
"""

from flask import Blueprint

# Import all API file blueprints
from .api_files_list import api_files_list_bp
from .api_files_operations import api_files_operations_bp

# Main API files blueprint - registers all sub-blueprints
api_files_bp = Blueprint('api_files', __name__)

# Register all sub-blueprints with the main API files blueprint
# Use url_prefix to maintain route structure
api_files_bp.register_blueprint(api_files_list_bp, url_prefix='')
api_files_bp.register_blueprint(api_files_operations_bp, url_prefix='')
