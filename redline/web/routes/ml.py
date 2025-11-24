"""
ML routes for REDLINE Web GUI
Route handlers for machine learning operations

This module now serves as a central registry for all ML blueprints.
Individual route modules are organized by functionality.
"""

from flask import Blueprint

# Import all ML blueprints
from .ml_tab import ml_tab_bp
from .analysis_ml import analysis_ml_bp
from .analysis_sklearn import analysis_sklearn_bp

# Main ML blueprint - registers all sub-blueprints
ml_bp = Blueprint('ml', __name__)

# Register all sub-blueprints with the main ML blueprint
# Use url_prefix to maintain route structure
ml_bp.register_blueprint(ml_tab_bp, url_prefix='')
ml_bp.register_blueprint(analysis_ml_bp, url_prefix='')
ml_bp.register_blueprint(analysis_sklearn_bp, url_prefix='')

