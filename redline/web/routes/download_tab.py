"""
Download tab main page route.
"""

from flask import Blueprint, render_template
import logging

download_tab_bp = Blueprint('download_tab', __name__)
logger = logging.getLogger(__name__)

@download_tab_bp.route('/')
def download_tab():
    """Download tab main page."""
    return render_template('download_tab.html')

