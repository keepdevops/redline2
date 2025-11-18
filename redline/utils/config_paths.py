#!/usr/bin/env python3
"""
Utility functions for managing configuration file paths.
Sensitive files (API keys, licenses) are stored in a hidden directory.
"""

import os
from pathlib import Path

def get_config_dir() -> Path:
    """
    Get the configuration directory for sensitive files.
    Uses ~/.redline/ for user-specific config.
    
    Returns:
        Path to the configuration directory
    """
    config_dir = Path.home() / '.redline'
    config_dir.mkdir(mode=0o700, exist_ok=True)  # rwx------ permissions
    return config_dir

def get_api_keys_file() -> Path:
    """Get path to API keys file in hidden directory."""
    return get_config_dir() / 'api_keys.json'

def get_custom_apis_file() -> Path:
    """Get path to custom APIs file in hidden directory."""
    return get_config_dir() / 'custom_apis.json'

def get_licenses_file() -> Path:
    """Get path to licenses file in hidden directory."""
    return get_config_dir() / 'licenses.json'

def ensure_config_dir():
    """Ensure the configuration directory exists with proper permissions."""
    config_dir = get_config_dir()
    # Set permissions to rwx------ (700) for security
    os.chmod(config_dir, 0o700)
    return config_dir

