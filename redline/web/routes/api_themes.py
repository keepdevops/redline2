"""
API routes for theme operations.
Handles theme management.
"""

from flask import Blueprint, request, jsonify
import logging
from .api_font_colors import api_font_colors_bp

api_themes_bp = Blueprint('api_themes', __name__)
logger = logging.getLogger(__name__)

# Register font colors blueprint
api_themes_bp.register_blueprint(api_font_colors_bp)


@api_themes_bp.route('/themes', methods=['GET'])
def get_themes():
    """Get available themes."""
    themes = {
        'theme-default': {
            'name': 'Default',
            'description': 'Default color-blind friendly theme',
            'icon': 'fas fa-circle',
            'color': 'primary'
        },
        'theme-high-contrast': {
            'name': 'High Contrast',
            'description': 'High contrast theme for better visibility',
            'icon': 'fas fa-circle',
            'color': 'danger'
        },
        'theme-ocean': {
            'name': 'Ocean',
            'description': 'Ocean-inspired blue theme',
            'icon': 'fas fa-circle',
            'color': 'info'
        },
        'theme-forest': {
            'name': 'Forest',
            'description': 'Nature-inspired green theme',
            'icon': 'fas fa-circle',
            'color': 'success'
        },
        'theme-sunset': {
            'name': 'Sunset',
            'description': 'Warm sunset colors',
            'icon': 'fas fa-circle',
            'color': 'warning'
        },
        'theme-monochrome': {
            'name': 'Monochrome',
            'description': 'Black and white theme',
            'icon': 'fas fa-circle',
            'color': 'secondary'
        },
        'theme-dark': {
            'name': 'Dark',
            'description': 'Dark mode theme',
            'icon': 'fas fa-moon',
            'color': 'dark'
        }
    }
    
    return jsonify({
        'themes': themes,
        'default': 'theme-default'
    })


@api_themes_bp.route('/theme', methods=['POST'])
def set_theme():
    """Set user theme preference."""
    try:
        data = request.get_json()
        theme = data.get('theme', 'theme-default')
        
        # Validate theme
        valid_themes = [
            'theme-default', 'theme-high-contrast', 'theme-ocean', 
            'theme-forest', 'theme-sunset', 'theme-monochrome', 'theme-dark'
        ]
        
        if theme not in valid_themes:
            return jsonify({'error': 'Invalid theme'}), 400
        
        # TODO: Store theme preference in user session/database
        # For now, just return success
        return jsonify({
            'message': 'Theme preference updated',
            'theme': theme
        })
        
    except Exception as e:
        logger.error(f"Error setting theme: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_themes_bp.route('/theme', methods=['GET'])
def get_theme():
    """Get current theme preference."""
    # TODO: Get theme from user session/database
    # For now, return default
    return jsonify({
        'theme': 'theme-default'
    })
