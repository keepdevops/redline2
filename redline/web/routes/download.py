"""
Download routes registry for REDLINE Web GUI.
Handles data downloading from various sources.

This module acts as a central registry for download sub-blueprints.
"""

from flask import Blueprint
from .download_tab import download_tab_bp
from .download_sources import download_sources_bp
from .download_single import download_single_bp
from .download_batch import download_batch_bp
from .download_history import download_history_bp

download_bp = Blueprint('download', __name__)

# Register sub-blueprints
download_bp.register_blueprint(download_tab_bp)
download_bp.register_blueprint(download_sources_bp)
download_bp.register_blueprint(download_single_bp)
download_bp.register_blueprint(download_batch_bp)
download_bp.register_blueprint(download_history_bp)
