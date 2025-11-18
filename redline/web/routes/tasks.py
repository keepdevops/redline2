"""
Background Task routes registry for REDLINE Web GUI
Handles asynchronous task processing and monitoring

This module now serves as a central registry for all task blueprints.
Individual route modules are organized by functionality.
"""

from flask import Blueprint

# Import all task blueprints
from .tasks_submit import tasks_submit_bp
from .tasks_status import tasks_status_bp

# Main task blueprint - registers all sub-blueprints
tasks_bp = Blueprint('tasks', __name__)

# Register all sub-blueprints with the main task blueprint
# Use url_prefix to maintain route structure
tasks_bp.register_blueprint(tasks_submit_bp, url_prefix='')
tasks_bp.register_blueprint(tasks_status_bp, url_prefix='')
