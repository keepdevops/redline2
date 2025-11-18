#!/usr/bin/env python3
"""
API Keys management routes for REDLINE Web GUI
Handles saving, loading, and displaying API keys
"""

from flask import Blueprint, render_template, request, jsonify, session
import logging
import os
import json
from ...utils.config_paths import get_api_keys_file, get_custom_apis_file, ensure_config_dir

api_keys_management_bp = Blueprint('api_keys_management', __name__)
logger = logging.getLogger(__name__)

# Note: api_keys_page route is defined in api_keys.py as an alias
# to maintain backward compatibility with templates using url_for('api_keys.api_keys_page')

@api_keys_management_bp.route('/save', methods=['POST'])
def save_api_keys():
    """Save API keys to user session or config file."""
    try:
        data = request.get_json()
        api_keys = data.get('api_keys', {})
        custom_apis = data.get('custom_apis', {})  # New: custom API configurations
        
        # Validate API keys
        valid_keys = {}
        for source, key in api_keys.items():
            if key and key.strip():
                valid_keys[source] = key.strip()
        
        # Validate custom API configurations
        valid_custom_apis = {}
        for api_id, api_config in custom_apis.items():
            if api_config and isinstance(api_config, dict):
                # Validate required fields - allow APIs without api_key (can be added later)
                if api_config.get('name') and api_config.get('base_url') and api_config.get('endpoint'):
                    # Ensure all required fields are present
                    validated_config = {
                        'name': api_config.get('name'),
                        'base_url': api_config.get('base_url'),
                        'endpoint': api_config.get('endpoint'),
                        'api_key': api_config.get('api_key', ''),
                        'rate_limit_per_minute': api_config.get('rate_limit_per_minute', 60),
                        'date_format': api_config.get('date_format', 'YYYY-MM-DD'),
                        'ticker_param': api_config.get('ticker_param', 'symbol'),
                        'api_key_param': api_config.get('api_key_param', 'apikey'),
                        'start_date_param': api_config.get('start_date_param', 'from'),
                        'end_date_param': api_config.get('end_date_param', 'to'),
                        'data_path': api_config.get('data_path', 'data'),
                        'response_format': api_config.get('response_format', 'json')
                    }
                    valid_custom_apis[api_id] = validated_config
        
        # Save to session (temporary)
        session['api_keys'] = valid_keys
        session['custom_apis'] = valid_custom_apis
        
        # Also save to config files for persistence (in hidden directory)
        # Ensure config directory exists with proper permissions
        ensure_config_dir()
        
        # Save standard API keys to hidden directory
        config_file = get_api_keys_file()
        with open(config_file, 'w') as f:
            json.dump(valid_keys, f, indent=2)
        # Set secure permissions (rw-------)
        os.chmod(config_file, 0o600)
        
        # Save custom API configurations to hidden directory
        custom_apis_file = get_custom_apis_file()
        with open(custom_apis_file, 'w') as f:
            json.dump(valid_custom_apis, f, indent=2)
        # Set secure permissions (rw-------)
        os.chmod(custom_apis_file, 0o600)
        
        logger.info(f"Saved API keys for sources: {list(valid_keys.keys())}")
        logger.info(f"Saved custom API configurations: {list(valid_custom_apis.keys())}")
        
        return jsonify({
            'message': f'Successfully saved API keys for {len(valid_keys)} sources and {len(valid_custom_apis)} custom APIs',
            'saved_sources': list(valid_keys.keys()),
            'saved_custom_apis': list(valid_custom_apis.keys())
        })
        
    except Exception as e:
        logger.error(f"Error saving API keys: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_keys_management_bp.route('/load')
def load_api_keys():
    """Load saved API keys and custom API configurations."""
    try:
        # Try to load from session first
        api_keys = session.get('api_keys', {})
        custom_apis = session.get('custom_apis', {})
        
        # Try to load from config files (in hidden directory)
        # Load standard API keys from hidden directory
        config_file = get_api_keys_file()
        if config_file.exists():
            with open(config_file, 'r') as f:
                file_keys = json.load(f)
                api_keys.update(file_keys)
        
        # Also check old location for migration
        old_config_file = 'data/api_keys.json'
        if os.path.exists(old_config_file):
            try:
                with open(old_config_file, 'r') as f:
                    old_keys = json.load(f)
                    api_keys.update(old_keys)
                # Migrate to new location
                if api_keys:
                    ensure_config_dir()
                    with open(config_file, 'w') as f:
                        json.dump(api_keys, f, indent=2)
                    os.chmod(config_file, 0o600)
                logger.info("Migrated API keys from data/ to ~/.redline/")
            except Exception as e:
                logger.warning(f"Error migrating API keys: {e}")
        
        # Load custom API configurations from hidden directory
        custom_apis_file = get_custom_apis_file()
        if custom_apis_file.exists():
            try:
                with open(custom_apis_file, 'r') as f:
                    file_custom_apis = json.load(f)
                    # Filter and normalize custom APIs to ensure they have required fields
                    for api_id, api_config in file_custom_apis.items():
                        if api_config and isinstance(api_config, dict):
                            # Only include if it has minimum required fields
                            if api_config.get('name') and api_config.get('base_url') and api_config.get('endpoint'):
                                # Normalize the config to ensure all fields are present
                                normalized_config = {
                                    'name': api_config.get('name'),
                                    'base_url': api_config.get('base_url'),
                                    'endpoint': api_config.get('endpoint'),
                                    'api_key': api_config.get('api_key', ''),
                                    'rate_limit_per_minute': api_config.get('rate_limit_per_minute', 60),
                                    'date_format': api_config.get('date_format', 'YYYY-MM-DD'),
                                    'ticker_param': api_config.get('ticker_param', 'symbol'),
                                    'api_key_param': api_config.get('api_key_param', 'apikey'),
                                    'start_date_param': api_config.get('start_date_param', 'from'),
                                    'end_date_param': api_config.get('end_date_param', 'to'),
                                    'data_path': api_config.get('data_path', 'data'),
                                    'response_format': api_config.get('response_format', 'json')
                                }
                                custom_apis[api_id] = normalized_config
            except Exception as e:
                logger.warning(f"Error loading custom APIs from file: {str(e)}")
        
        # Also check old location for migration
        old_custom_apis_file = 'data/custom_apis.json'
        if os.path.exists(old_custom_apis_file):
            try:
                with open(old_custom_apis_file, 'r') as f:
                    old_custom_apis = json.load(f)
                    for api_id, api_config in old_custom_apis.items():
                        if api_config and isinstance(api_config, dict):
                            if api_config.get('name') and api_config.get('base_url') and api_config.get('endpoint'):
                                normalized_config = {
                                    'name': api_config.get('name'),
                                    'base_url': api_config.get('base_url'),
                                    'endpoint': api_config.get('endpoint'),
                                    'api_key': api_config.get('api_key', ''),
                                    'rate_limit_per_minute': api_config.get('rate_limit_per_minute', 60),
                                    'date_format': api_config.get('date_format', 'YYYY-MM-DD'),
                                    'ticker_param': api_config.get('ticker_param', 'symbol'),
                                    'api_key_param': api_config.get('api_key_param', 'apikey'),
                                    'start_date_param': api_config.get('start_date_param', 'from'),
                                    'end_date_param': api_config.get('end_date_param', 'to'),
                                    'data_path': api_config.get('data_path', 'data'),
                                    'response_format': api_config.get('response_format', 'json')
                                }
                                custom_apis[api_id] = normalized_config
                # Migrate to new location
                if custom_apis:
                    ensure_config_dir()
                    with open(custom_apis_file, 'w') as f:
                        json.dump(custom_apis, f, indent=2)
                    os.chmod(custom_apis_file, 0o600)
                logger.info("Migrated custom APIs from data/ to ~/.redline/")
            except Exception as e:
                logger.warning(f"Error migrating custom APIs: {e}")
        
        return jsonify({
            'api_keys': api_keys,
            'custom_apis': custom_apis
        })
        
    except Exception as e:
        logger.error(f"Error loading API keys: {str(e)}")
        return jsonify({'error': str(e)}), 500

