"""
ML tab routes for REDLINE Web GUI
Main route handlers for machine learning operations
"""

from flask import Blueprint, render_template

ml_tab_bp = Blueprint('ml_tab', __name__)


@ml_tab_bp.route('/')
def ml_tab():
    """ML tab main page."""
    return render_template('ml_tab.html')

