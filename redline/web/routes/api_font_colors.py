"""
API routes for font color operations.
Handles font color configuration and presets.
"""

from flask import Blueprint, request, jsonify, session
import logging
import re

api_font_colors_bp = Blueprint('api_font_colors', __name__)
logger = logging.getLogger(__name__)


@api_font_colors_bp.route('/font-colors', methods=['GET'])
def get_font_colors():
    """Get current font color configuration."""
    try:
        # This would typically come from a database or user preferences
        # For now, return default font color variables
        font_colors = {
            'text-primary': '#1e293b',
            'text-secondary': '#64748b',
            'text-muted': '#94a3b8',
            'text-light': '#cbd5e1',
            'text-dark': '#0f172a',
            'text-white': '#ffffff',
            'text-success': '#059669',
            'text-warning': '#d97706',
            'text-danger': '#dc2626',
            'text-info': '#0891b2',
            'text-link': '#2563eb',
            'text-link-hover': '#1d4ed8'
        }
        
        return jsonify({'font_colors': font_colors})
        
    except Exception as e:
        logger.error(f"Error getting font colors: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_font_colors_bp.route('/font-colors', methods=['POST'])
def set_font_colors():
    """Set custom font color configuration."""
    try:
        data = request.get_json()
        font_colors = data.get('font_colors', {})
        
        # Validate font colors
        valid_color_keys = [
            'text-primary', 'text-secondary', 'text-muted', 'text-light', 
            'text-dark', 'text-white', 'text-success', 'text-warning', 
            'text-danger', 'text-info', 'text-link', 'text-link-hover'
        ]
        
        # Validate color format (basic hex color validation)
        hex_pattern = re.compile(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
        
        for key, value in font_colors.items():
            if key not in valid_color_keys:
                return jsonify({'error': f'Invalid color key: {key}'}), 400
            
            if not hex_pattern.match(value):
                return jsonify({'error': f'Invalid color format for {key}: {value}'}), 400
        
        # Store font colors in session (you could also store in database)
        session['font_colors'] = font_colors
        
        return jsonify({
            'message': 'Font colors updated successfully',
            'font_colors': font_colors
        })
        
    except Exception as e:
        logger.error(f"Error setting font colors: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_font_colors_bp.route('/font-color-presets', methods=['GET'])
def get_font_color_presets():
    """Get available font color presets."""
    try:
        presets = {
            'default': {
                'text-primary': '#1e293b',
                'text-secondary': '#64748b',
                'text-muted': '#94a3b8',
                'text-light': '#cbd5e1',
                'text-dark': '#0f172a',
                'text-white': '#ffffff',
                'text-success': '#059669',
                'text-warning': '#d97706',
                'text-danger': '#dc2626',
                'text-info': '#0891b2',
                'text-link': '#2563eb',
                'text-link-hover': '#1d4ed8'
            },
            'high-contrast': {
                'text-primary': '#000000',
                'text-secondary': '#404040',
                'text-muted': '#808080',
                'text-light': '#c0c0c0',
                'text-dark': '#000000',
                'text-white': '#ffffff',
                'text-success': '#008000',
                'text-warning': '#ff8000',
                'text-danger': '#ff0000',
                'text-info': '#0080ff',
                'text-link': '#0000ff',
                'text-link-hover': '#0000cc'
            },
            'ocean': {
                'text-primary': '#0f172a',
                'text-secondary': '#475569',
                'text-muted': '#64748b',
                'text-light': '#94a3b8',
                'text-dark': '#020617',
                'text-white': '#ffffff',
                'text-success': '#0d9488',
                'text-warning': '#f59e0b',
                'text-danger': '#dc2626',
                'text-info': '#0891b2',
                'text-link': '#0369a1',
                'text-link-hover': '#075985'
            },
            'forest': {
                'text-primary': '#14532d',
                'text-secondary': '#365314',
                'text-muted': '#4b5563',
                'text-light': '#9ca3af',
                'text-dark': '#052e16',
                'text-white': '#ffffff',
                'text-success': '#16a34a',
                'text-warning': '#ca8a04',
                'text-danger': '#dc2626',
                'text-info': '#0891b2',
                'text-link': '#166534',
                'text-link-hover': '#15803d'
            },
            'sunset': {
                'text-primary': '#431407',
                'text-secondary': '#9a3412',
                'text-muted': '#a16207',
                'text-light': '#d97706',
                'text-dark': '#292524',
                'text-white': '#ffffff',
                'text-success': '#16a34a',
                'text-warning': '#f59e0b',
                'text-danger': '#dc2626',
                'text-info': '#0891b2',
                'text-link': '#ea580c',
                'text-link-hover': '#c2410c'
            },
            'monochrome': {
                'text-primary': '#111827',
                'text-secondary': '#374151',
                'text-muted': '#6b7280',
                'text-light': '#9ca3af',
                'text-dark': '#000000',
                'text-white': '#ffffff',
                'text-success': '#059669',
                'text-warning': '#d97706',
                'text-danger': '#dc2626',
                'text-info': '#0891b2',
                'text-link': '#374151',
                'text-link-hover': '#1f2937'
            },
            'dark': {
                'text-primary': '#f9fafb',
                'text-secondary': '#d1d5db',
                'text-muted': '#9ca3af',
                'text-light': '#6b7280',
                'text-dark': '#ffffff',
                'text-white': '#ffffff',
                'text-success': '#10b981',
                'text-warning': '#f59e0b',
                'text-danger': '#ef4444',
                'text-info': '#06b6d4',
                'text-link': '#3b82f6',
                'text-link-hover': '#2563eb'
            },
            'grayscale': {
                'text-primary': '#2d3748',
                'text-secondary': '#4a5568',
                'text-muted': '#718096',
                'text-light': '#a0aec0',
                'text-dark': '#1a202c',
                'text-white': '#ffffff',
                'text-success': '#38a169',
                'text-warning': '#d69e2e',
                'text-danger': '#e53e3e',
                'text-info': '#3182ce',
                'text-link': '#4a5568',
                'text-link-hover': '#2d3748'
            }
        }
        
        return jsonify({'presets': presets})
        
    except Exception as e:
        logger.error(f"Error getting font color presets: {str(e)}")
        return jsonify({'error': str(e)}), 500

