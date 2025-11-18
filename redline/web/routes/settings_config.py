"""
Settings configuration routes for REDLINE Web GUI
Handles application configuration management
"""

from flask import Blueprint, render_template, request, jsonify
import logging
import os
import time
import configparser

settings_config_bp = Blueprint('settings_config', __name__)
logger = logging.getLogger(__name__)

# Note: settings_tab route is defined in settings.py as an alias
# to maintain backward compatibility with templates using url_for('settings.settings_tab')

@settings_config_bp.route('/config')
def get_config():
    """Get current application configuration."""
    try:
        config_file = os.path.join(os.getcwd(), 'data_config.ini')
        
        config = configparser.ConfigParser()
        if os.path.exists(config_file):
            config.read(config_file)
        
        # Convert to dictionary format
        config_dict = {}
        for section in config.sections():
            config_dict[section] = dict(config[section])
        
        # Add default configurations if not present
        default_config = {
            'data_sources': {
                'yahoo_enabled': 'true',
                'stooq_enabled': 'true',
                'default_source': 'yahoo'
            },
            'display': {
                'max_rows': '1000',
                'auto_refresh': 'false',
                'theme': 'light'
            },
            'performance': {
                'chunk_size': '10000',
                'max_memory': '1GB',
                'parallel_processing': 'true'
            },
            'export': {
                'default_format': 'csv',
                'include_metadata': 'true',
                'compression': 'none'
            }
        }
        
        # Merge with existing config
        for section, options in default_config.items():
            if section not in config_dict:
                config_dict[section] = options
            else:
                for key, value in options.items():
                    if key not in config_dict[section]:
                        config_dict[section][key] = value
        
        return jsonify({
            'config': config_dict,
            'config_file': config_file,
            'config_exists': os.path.exists(config_file)
        })
        
    except Exception as e:
        logger.error(f"Error getting configuration: {str(e)}")
        return jsonify({'error': str(e)}), 500

@settings_config_bp.route('/config', methods=['POST'])
def update_config():
    """Update application configuration."""
    try:
        data = request.get_json()
        new_config = data.get('config')
        
        if not new_config:
            return jsonify({'error': 'No configuration provided'}), 400
        
        config_file = os.path.join(os.getcwd(), 'data_config.ini')
        
        config = configparser.ConfigParser()
        
        # Create backup of existing config
        if os.path.exists(config_file):
            backup_file = f"{config_file}.backup"
            os.rename(config_file, backup_file)
        
        # Write new configuration
        for section, options in new_config.items():
            config.add_section(section)
            for key, value in options.items():
                config.set(section, key, str(value))
        
        with open(config_file, 'w') as f:
            config.write(f)
        
        return jsonify({
            'message': 'Configuration updated successfully',
            'config_file': config_file
        })
        
    except Exception as e:
        logger.error(f"Error updating configuration: {str(e)}")
        return jsonify({'error': str(e)}), 500

@settings_config_bp.route('/reset-config')
def reset_config():
    """Reset configuration to defaults."""
    try:
        config_file = os.path.join(os.getcwd(), 'data_config.ini')
        
        # Create backup
        if os.path.exists(config_file):
            backup_file = f"{config_file}.backup.{int(time.time())}"
            os.rename(config_file, backup_file)
        
        # Create default configuration
        default_config = {
            'data_sources': {
                'yahoo_enabled': 'true',
                'stooq_enabled': 'true',
                'default_source': 'yahoo'
            },
            'display': {
                'max_rows': '1000',
                'auto_refresh': 'false',
                'theme': 'light'
            },
            'performance': {
                'chunk_size': '10000',
                'max_memory': '1GB',
                'parallel_processing': 'true'
            },
            'export': {
                'default_format': 'csv',
                'include_metadata': 'true',
                'compression': 'none'
            }
        }
        
        config = configparser.ConfigParser()
        for section, options in default_config.items():
            config.add_section(section)
            for key, value in options.items():
                config.set(section, key, str(value))
        
        with open(config_file, 'w') as f:
            config.write(f)
        
        return jsonify({
            'message': 'Configuration reset to defaults',
            'config_file': config_file
        })
        
    except Exception as e:
        logger.error(f"Error resetting configuration: {str(e)}")
        return jsonify({'error': str(e)}), 500

