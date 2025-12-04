"""
Data tab template routes for REDLINE Web GUI.
Handles rendering of data tab pages.
"""

from flask import Blueprint, render_template

data_tab_bp = Blueprint('data_tab', __name__)


@data_tab_bp.route('/')
def data_tab():
    """Data tab main page - redirects to multi-file view."""
    from flask import redirect
    return redirect('/data/multi')


@data_tab_bp.route('/browser')
def file_browser():
    """File browser page - browse and load files from anywhere on the system."""
    return render_template('file_browser.html')


@data_tab_bp.route('/stooq')
def stooq_downloader():
    """Stooq data downloader page."""
    return render_template('stooq_downloader.html')


@data_tab_bp.route('/multi')
def data_tab_multi():
    """Multi-file data tab."""
    return render_template('data_tab_multi_file.html')


@data_tab_bp.route('/debug')
def data_tab_debug():
    """Data tab debug page."""
    return render_template('data_tab_debug.html')


@data_tab_bp.route('/simple')
def data_tab_simple():
    """Data tab simple version."""
    return render_template('data_tab_simple.html')

