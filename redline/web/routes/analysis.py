"""
Analysis routes for REDLINE Web GUI
Route handlers for data analysis and statistical operations

This module now serves as a central registry for all analysis blueprints.
Individual route modules are organized by functionality.
"""

from flask import Blueprint

# Import all analysis blueprints
from .analysis_tab import analysis_tab_bp
from .analysis_export import analysis_export_bp
from .analysis_charts import analysis_charts_bp
from .analysis_ml import analysis_ml_bp
from .analysis_visualization import analysis_visualization_bp
from .analysis_sklearn import analysis_sklearn_bp

# Main analysis blueprint - registers all sub-blueprints
analysis_bp = Blueprint('analysis', __name__)

# Register all sub-blueprints with the main analysis blueprint
# Use url_prefix to maintain route structure
analysis_bp.register_blueprint(analysis_tab_bp, url_prefix='')
analysis_bp.register_blueprint(analysis_export_bp, url_prefix='')
analysis_bp.register_blueprint(analysis_charts_bp, url_prefix='')
analysis_bp.register_blueprint(analysis_ml_bp, url_prefix='')
analysis_bp.register_blueprint(analysis_visualization_bp, url_prefix='')
analysis_bp.register_blueprint(analysis_sklearn_bp, url_prefix='')
