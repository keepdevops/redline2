"""
Settings configuration routes for VarioSync Web GUI
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
    logger.debug("Processing get config request")

    # Determine config file path
    config_file = os.path.join(os.getcwd(), 'data_config.ini')
    logger.debug(f"Config file path: {config_file}")

    config = configparser.ConfigParser()
    config_exists = os.path.exists(config_file)

    # Load existing config if present (legitimate exception handling for file I/O)
    if config_exists:
        try:
            config.read(config_file)
            logger.debug(f"Loaded config with {len(config.sections())} sections")
        except PermissionError as e:
            logger.error(f"Permission denied reading config file: {str(e)}")
            return jsonify({'error': 'Permission denied reading configuration file', 'code': 'PERMISSION_DENIED'}), 403
        except OSError as e:
            logger.error(f"OS error reading config file: {str(e)}")
            return jsonify({'error': f'File system error reading configuration: {str(e)}', 'code': 'OS_ERROR'}), 500
        except configparser.Error as e:
            logger.error(f"Config parsing error: {str(e)}")
            return jsonify({'error': f'Invalid configuration file format: {str(e)}', 'code': 'CONFIG_PARSE_ERROR'}), 500
        except Exception as e:
            logger.error(f"Unexpected error reading config file: {str(e)}")
            return jsonify({'error': f'Failed to read configuration file: {str(e)}', 'code': 'CONFIG_READ_ERROR'}), 500
    else:
        logger.info(f"Config file does not exist: {config_file}")

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
    merged_sections = 0
    for section, options in default_config.items():
        if section not in config_dict:
            config_dict[section] = options
            merged_sections += 1
        else:
            for key, value in options.items():
                if key not in config_dict[section]:
                    config_dict[section][key] = value

    logger.info(f"Config retrieved: {len(config_dict)} sections, {merged_sections} merged from defaults")

    return jsonify({
        'config': config_dict,
        'config_file': config_file,
        'config_exists': config_exists
    })

@settings_config_bp.route('/config', methods=['POST'])
def update_config():
    """Update application configuration."""
    # Get request data
    data = request.get_json()

    if not data:
        logger.warning("Update config request with empty body")
        return jsonify({'error': 'Request body is required'}), 400

    if not isinstance(data, dict):
        logger.error(f"Update config request with invalid data type: {type(data)}")
        return jsonify({'error': 'Request body must be JSON object'}), 400

    # Validate config field
    new_config = data.get('config')

    if not new_config:
        logger.warning("Update config request missing config field")
        return jsonify({'error': 'No configuration provided'}), 400

    if not isinstance(new_config, dict):
        logger.error(f"Update config request config has invalid type: {type(new_config)}")
        return jsonify({'error': 'Configuration must be an object'}), 400

    if len(new_config) == 0:
        logger.warning("Update config request with empty config")
        return jsonify({'error': 'Configuration cannot be empty'}), 400

    logger.info(f"Processing config update request: {len(new_config)} sections")

    config_file = os.path.join(os.getcwd(), 'data_config.ini')
    logger.debug(f"Config file path: {config_file}")

    # Create backup of existing config (legitimate exception handling for file operations)
    if os.path.exists(config_file):
        backup_file = f"{config_file}.backup"
        try:
            os.rename(config_file, backup_file)
            logger.info(f"Created config backup: {backup_file}")
        except PermissionError as e:
            logger.error(f"Permission denied creating config backup: {str(e)}")
            return jsonify({'error': 'Permission denied creating configuration backup', 'code': 'PERMISSION_DENIED'}), 403
        except OSError as e:
            logger.error(f"OS error creating config backup: {str(e)}")
            return jsonify({'error': f'File system error creating backup: {str(e)}', 'code': 'OS_ERROR'}), 500
        except Exception as e:
            logger.error(f"Unexpected error creating config backup: {str(e)}")
            return jsonify({'error': f'Failed to backup configuration: {str(e)}', 'code': 'BACKUP_ERROR'}), 500
    else:
        logger.debug("No existing config file to backup")

    # Write new configuration
    config = configparser.ConfigParser()

    # Validate and add sections
    sections_added = 0
    for section, options in new_config.items():
        if not isinstance(section, str):
            logger.warning(f"Skipping invalid section with non-string key: {type(section)}")
            continue

        if not isinstance(options, dict):
            logger.warning(f"Skipping section '{section}' with non-dict value: {type(options)}")
            continue

        try:
            config.add_section(section)
            sections_added += 1

            # Add options to section
            for key, value in options.items():
                if not isinstance(key, str):
                    logger.warning(f"Skipping option in section '{section}' with non-string key: {type(key)}")
                    continue
                config.set(section, key, str(value))

        except configparser.DuplicateSectionError as e:
            logger.warning(f"Duplicate section '{section}': {str(e)}")
            continue
        except ValueError as e:
            logger.error(f"Invalid value in section '{section}': {str(e)}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error adding section '{section}': {str(e)}")
            continue

    if sections_added == 0:
        logger.error("No valid sections found in config update")
        return jsonify({'error': 'No valid configuration sections provided'}), 400

    # Write config file (legitimate exception handling for file I/O)
    try:
        with open(config_file, 'w') as f:
            config.write(f)
        logger.info(f"Config file written successfully: {sections_added} sections")
    except PermissionError as e:
        logger.error(f"Permission denied writing config file: {str(e)}")
        return jsonify({'error': 'Permission denied writing configuration file', 'code': 'PERMISSION_DENIED'}), 403
    except OSError as e:
        logger.error(f"OS error writing config file: {str(e)}")
        return jsonify({'error': f'File system error writing configuration: {str(e)}', 'code': 'OS_ERROR'}), 500
    except IOError as e:
        logger.error(f"I/O error writing config file: {str(e)}")
        return jsonify({'error': f'I/O error writing configuration: {str(e)}', 'code': 'IO_ERROR'}), 500
    except Exception as e:
        logger.error(f"Unexpected error writing config file: {str(e)}")
        return jsonify({'error': f'Failed to write configuration file: {str(e)}', 'code': 'CONFIG_WRITE_ERROR'}), 500

    # Verify file was written
    if not os.path.exists(config_file):
        logger.error(f"Config file was not created: {config_file}")
        return jsonify({'error': 'Failed to create configuration file'}), 500

    logger.info("Configuration updated successfully")

    return jsonify({
        'message': 'Configuration updated successfully',
        'config_file': config_file,
        'sections': sections_added
    })

@settings_config_bp.route('/reset-config')
def reset_config():
    """Reset configuration to defaults."""
    logger.info("Processing config reset request")

    config_file = os.path.join(os.getcwd(), 'data_config.ini')
    logger.debug(f"Config file path: {config_file}")

    # Create timestamped backup (legitimate exception handling for file operations)
    if os.path.exists(config_file):
        backup_file = f"{config_file}.backup.{int(time.time())}"
        try:
            os.rename(config_file, backup_file)
            logger.info(f"Created timestamped config backup: {backup_file}")
        except PermissionError as e:
            logger.error(f"Permission denied creating config backup: {str(e)}")
            return jsonify({'error': 'Permission denied creating configuration backup', 'code': 'PERMISSION_DENIED'}), 403
        except OSError as e:
            logger.error(f"OS error creating config backup: {str(e)}")
            return jsonify({'error': f'File system error creating backup: {str(e)}', 'code': 'OS_ERROR'}), 500
        except Exception as e:
            logger.error(f"Unexpected error creating config backup: {str(e)}")
            return jsonify({'error': f'Failed to backup configuration: {str(e)}', 'code': 'BACKUP_ERROR'}), 500
    else:
        logger.debug("No existing config file to backup")

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

    logger.debug(f"Creating default config with {len(default_config)} sections")

    config = configparser.ConfigParser()

    # Add default sections (legitimate exception handling for configparser operations)
    sections_added = 0
    for section, options in default_config.items():
        try:
            config.add_section(section)
            sections_added += 1

            for key, value in options.items():
                config.set(section, key, str(value))

        except configparser.DuplicateSectionError as e:
            logger.warning(f"Duplicate default section '{section}': {str(e)}")
            continue
        except ValueError as e:
            logger.error(f"Invalid value in default section '{section}': {str(e)}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error adding default section '{section}': {str(e)}")
            continue

    if sections_added == 0:
        logger.error("Failed to add any default sections")
        return jsonify({'error': 'Failed to create default configuration'}), 500

    # Write config file (legitimate exception handling for file I/O)
    try:
        with open(config_file, 'w') as f:
            config.write(f)
        logger.info(f"Default config file written successfully: {sections_added} sections")
    except PermissionError as e:
        logger.error(f"Permission denied writing default config file: {str(e)}")
        return jsonify({'error': 'Permission denied writing configuration file', 'code': 'PERMISSION_DENIED'}), 403
    except OSError as e:
        logger.error(f"OS error writing default config file: {str(e)}")
        return jsonify({'error': f'File system error writing configuration: {str(e)}', 'code': 'OS_ERROR'}), 500
    except IOError as e:
        logger.error(f"I/O error writing default config file: {str(e)}")
        return jsonify({'error': f'I/O error writing configuration: {str(e)}', 'code': 'IO_ERROR'}), 500
    except Exception as e:
        logger.error(f"Unexpected error writing default config file: {str(e)}")
        return jsonify({'error': f'Failed to write configuration file: {str(e)}', 'code': 'CONFIG_WRITE_ERROR'}), 500

    # Verify file was written
    if not os.path.exists(config_file):
        logger.error(f"Config file was not created: {config_file}")
        return jsonify({'error': 'Failed to create configuration file'}), 500

    logger.info("Configuration reset to defaults successfully")

    return jsonify({
        'message': 'Configuration reset to defaults',
        'config_file': config_file,
        'sections': sections_added
    })

