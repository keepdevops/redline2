#!/usr/bin/env python3
"""
REDLINE Configuration Management
Handles configuration loading, validation, and management.
"""

import logging
import configparser
import os
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages application configuration."""
    
    def __init__(self, config_path: str = 'data_config.ini'):
        """Initialize configuration manager."""
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        self.logger = logging.getLogger(__name__)
        
        # Default configuration
        self.defaults = {
            'Data': {
                'db_path': 'redline_data.duckdb',
                'csv_dir': 'data',
                'json_dir': 'data/json',
                'parquet_dir': 'data/parquet',
                'cache_size': '1000',
                'thread_count': '4'
            },
            'Display': {
                'rows_per_page': '100',
                'auto_refresh': '0',
                'theme': 'default',
                'font_size': '10'
            },
            'Download': {
                'timeout': '30',
                'max_retries': '3',
                'rate_limit_delay': '1',
                'batch_size': '50'
            },
            'Logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': 'redline.log'
            },
            'Performance': {
                'enable_monitoring': 'true',
                'memory_limit': '1024',
                'cpu_limit': '80'
            }
        }
        
        self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default."""
        # Pre-validation with if-else
        if not self.config_path:
            self.logger.warning("Config path is empty, using default configuration")
            self.create_default_config()
            return
        
        if not isinstance(self.config_path, str):
            self.logger.warning(f"Config path must be a string, got {type(self.config_path)}")
            self.create_default_config()
            return
        
        if not os.path.exists(self.config_path):
            self.logger.info(f"Configuration file not found, creating default at {self.config_path}")
            self.create_default_config()
            return
        
        if not os.path.isfile(self.config_path):
            self.logger.warning(f"Config path exists but is not a file: {self.config_path}")
            self.create_default_config()
            return
        
        if not os.access(self.config_path, os.R_OK):
            self.logger.warning(f"Config file is not readable: {self.config_path}")
            self.create_default_config()
            return
        
        try:
            self.config.read(self.config_path)
            self.logger.info(f"Loaded configuration from {self.config_path}")
        except configparser.Error as e:
            self.logger.error(f"Error parsing configuration file: {str(e)}")
            self.create_default_config()
        except Exception as e:
            self.logger.error(f"Unexpected error loading configuration: {str(e)}")
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration file."""
        # Pre-validation with if-else
        if not self.defaults:
            self.logger.error("No default configuration values defined")
            return

        if not isinstance(self.defaults, dict):
            self.logger.error(f"Defaults must be a dictionary, got {type(self.defaults)}")
            return

        try:
            # Set default values
            for section, options in self.defaults.items():
                if not self.config.has_section(section):
                    self.config.add_section(section)

                for option, value in options.items():
                    self.config.set(section, option, value)

            # Save to file
            self.save_config()

        except configparser.Error as e:
            self.logger.error(f"ConfigParser error creating default configuration: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error creating default configuration: {str(e)}")
    
    def save_config(self):
        """Save configuration to file."""
        # Pre-validation with if-else
        if not self.config_path:
            self.logger.error("Config path is empty, cannot save")
            raise ValueError("Config path cannot be empty")

        if not isinstance(self.config_path, str):
            self.logger.error(f"Config path must be a string, got {type(self.config_path)}")
            raise TypeError(f"Config path must be a string, got {type(self.config_path)}")

        # Check if parent directory exists and is writable
        parent_dir = os.path.dirname(self.config_path)
        if parent_dir and not os.path.exists(parent_dir):
            self.logger.error(f"Parent directory does not exist: {parent_dir}")
            raise FileNotFoundError(f"Parent directory does not exist: {parent_dir}")

        if parent_dir and not os.access(parent_dir, os.W_OK):
            self.logger.error(f"Parent directory is not writable: {parent_dir}")
            raise PermissionError(f"Parent directory is not writable: {parent_dir}")

        try:
            with open(self.config_path, 'w') as configfile:
                self.config.write(configfile)
            self.logger.info(f"Configuration saved to {self.config_path}")

        except PermissionError as e:
            self.logger.error(f"Permission denied writing config file {self.config_path}: {str(e)}")
            raise
        except OSError as e:
            self.logger.error(f"OS error writing config file {self.config_path}: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error saving configuration: {str(e)}")
            raise
    
    def get(self, section: str, option: str, fallback: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            section: Configuration section
            option: Configuration option
            fallback: Fallback value if not found
            
        Returns:
            Configuration value
        """
        # Pre-validation with if-else
        if not section or not isinstance(section, str):
            self.logger.debug(f"Invalid section name: {section}, returning fallback")
            return fallback
        
        if not option or not isinstance(option, str):
            self.logger.debug(f"Invalid option name: {option}, returning fallback")
            return fallback
        
        if not self.config.has_section(section):
            self.logger.debug(f"Section [{section}] not found, returning fallback")
            return fallback
        
        if not self.config.has_option(section, option):
            self.logger.debug(f"Option [{section}]{option} not found, returning fallback")
            return fallback
        
        try:
            value = self.config.get(section, option)
            
            # Type conversion with validation
            if value.isdigit():
                return int(value)
            elif value.lower() in ('true', 'false'):
                return value.lower() == 'true'
            return value
                
        except ValueError as e:
            self.logger.error(f"Error converting config value [{section}]{option}: {str(e)}")
            return fallback
        except Exception as e:
            self.logger.error(f"Unexpected error getting config value [{section}]{option}: {str(e)}")
            return fallback
    
    def set(self, section: str, option: str, value: Any):
        """
        Set configuration value.
        
        Args:
            section: Configuration section
            option: Configuration option
            value: Value to set
        """
        # Pre-validation with if-else
        if not section or not isinstance(section, str):
            self.logger.error(f"Invalid section name: {section}")
            raise ValueError(f"Section name must be a non-empty string, got: {section}")
        
        if not option or not isinstance(option, str):
            self.logger.error(f"Invalid option name: {option}")
            raise ValueError(f"Option name must be a non-empty string, got: {option}")
        
        if value is None:
            self.logger.warning(f"Setting None value for [{section}]{option}")
        
        try:
            if not self.config.has_section(section):
                self.config.add_section(section)
            
            self.config.set(section, option, str(value))
            
        except configparser.Error as e:
            self.logger.error(f"ConfigParser error setting [{section}]{option}: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error setting config value [{section}]{option}: {str(e)}")
            raise
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get entire configuration section.

        Args:
            section: Configuration section name

        Returns:
            Dictionary of section options
        """
        # Pre-validation with if-else
        if not section:
            self.logger.warning("Section name is empty, returning empty dict")
            return {}

        if not isinstance(section, str):
            self.logger.warning(f"Section name must be a string, got {type(section)}, returning empty dict")
            return {}

        if not self.config.has_section(section):
            self.logger.debug(f"Section [{section}] not found, returning empty dict")
            return {}

        try:
            return dict(self.config[section])

        except KeyError as e:
            self.logger.error(f"Key error getting config section [{section}]: {str(e)}")
            return {}
        except Exception as e:
            self.logger.error(f"Unexpected error getting config section [{section}]: {str(e)}")
            return {}
    
    def update_section(self, section: str, options: Dict[str, Any]):
        """
        Update entire configuration section.

        Args:
            section: Configuration section name
            options: Dictionary of options to set
        """
        # Pre-validation with if-else
        if not section or not isinstance(section, str):
            self.logger.error(f"Invalid section name: {section}")
            raise ValueError(f"Section name must be a non-empty string, got: {section}")

        if not options:
            self.logger.warning(f"Options dictionary is empty for section [{section}]")
            return

        if not isinstance(options, dict):
            self.logger.error(f"Options must be a dictionary, got {type(options)}")
            raise TypeError(f"Options must be a dictionary, got {type(options)}")

        try:
            if not self.config.has_section(section):
                self.config.add_section(section)

            for option, value in options.items():
                self.config.set(section, option, str(value))

        except configparser.Error as e:
            self.logger.error(f"ConfigParser error updating section [{section}]: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error updating config section [{section}]: {str(e)}")
            raise
    
    def validate_config(self) -> Dict[str, List[str]]:
        """
        Validate configuration values.
        
        Returns:
            Dictionary of validation errors by section
        """
        errors = {}
        
        try:
            # Validate Data section
            data_errors = self._validate_data_section()
            if data_errors:
                errors['Data'] = data_errors
            
            # Validate Display section
            display_errors = self._validate_display_section()
            if display_errors:
                errors['Display'] = display_errors
            
            # Validate Download section
            download_errors = self._validate_download_section()
            if download_errors:
                errors['Download'] = download_errors
            
            return errors
            
        except Exception as e:
            self.logger.error(f"Error validating configuration: {str(e)}")
            return {'General': [str(e)]}
    
    def _validate_data_section(self) -> List[str]:
        """Validate Data section configuration."""
        errors = []

        # Check required directories
        csv_dir = self.get('Data', 'csv_dir')
        if csv_dir and not os.path.exists(csv_dir):
            # Pre-validation with if-else
            if not isinstance(csv_dir, str):
                errors.append(f"CSV directory path must be a string, got {type(csv_dir)}")
            else:
                # Check if parent directory is writable
                parent_dir = os.path.dirname(csv_dir) or '.'
                if os.path.exists(parent_dir) and not os.access(parent_dir, os.W_OK):
                    errors.append(f"Parent directory is not writable: {parent_dir}")
                else:
                    try:
                        os.makedirs(csv_dir, exist_ok=True)
                    except PermissionError as e:
                        errors.append(f"Permission denied creating CSV directory {csv_dir}: {str(e)}")
                    except OSError as e:
                        errors.append(f"OS error creating CSV directory {csv_dir}: {str(e)}")
                    except Exception as e:
                        errors.append(f"Cannot create CSV directory {csv_dir}: {str(e)}")
        
        # Check numeric values
        cache_size = self.get('Data', 'cache_size', 1000)
        if not isinstance(cache_size, int) or cache_size < 1:
            errors.append("cache_size must be a positive integer")
        
        thread_count = self.get('Data', 'thread_count', 4)
        if not isinstance(thread_count, int) or thread_count < 1 or thread_count > 32:
            errors.append("thread_count must be between 1 and 32")
        
        return errors
    
    def _validate_display_section(self) -> List[str]:
        """Validate Display section configuration."""
        errors = []
        
        # Check numeric values
        rows_per_page = self.get('Display', 'rows_per_page', 100)
        if not isinstance(rows_per_page, int) or rows_per_page < 1:
            errors.append("rows_per_page must be a positive integer")
        
        font_size = self.get('Display', 'font_size', 10)
        if not isinstance(font_size, int) or font_size < 8 or font_size > 24:
            errors.append("font_size must be between 8 and 24")
        
        # Check theme
        theme = self.get('Display', 'theme', 'default')
        valid_themes = ['default', 'clam', 'alt', 'classic', 'vista', 'xpnative']
        if theme not in valid_themes:
            errors.append(f"theme must be one of: {', '.join(valid_themes)}")
        
        return errors
    
    def _validate_download_section(self) -> List[str]:
        """Validate Download section configuration."""
        errors = []
        
        # Check numeric values
        timeout = self.get('Download', 'timeout', 30)
        if not isinstance(timeout, int) or timeout < 1:
            errors.append("timeout must be a positive integer")
        
        max_retries = self.get('Download', 'max_retries', 3)
        if not isinstance(max_retries, int) or max_retries < 0:
            errors.append("max_retries must be a non-negative integer")
        
        return errors
    
    def reset_to_defaults(self):
        """Reset configuration to default values."""
        # Pre-validation with if-else
        if not self.defaults:
            self.logger.error("No default configuration values defined")
            raise ValueError("No default configuration values defined")

        if not isinstance(self.defaults, dict):
            self.logger.error(f"Defaults must be a dictionary, got {type(self.defaults)}")
            raise TypeError(f"Defaults must be a dictionary, got {type(self.defaults)}")

        try:
            self.config.clear()
            self.create_default_config()
            self.logger.info("Configuration reset to defaults")

        except configparser.Error as e:
            self.logger.error(f"ConfigParser error resetting configuration: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error resetting configuration: {str(e)}")
            raise
    
    def backup_config(self, backup_path: str = None):
        """
        Create backup of current configuration.

        Args:
            backup_path: Path for backup file (optional)
        """
        # Generate default backup path if not provided
        if backup_path is None:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"data_config_backup_{timestamp}.ini"

        # Pre-validation with if-else
        if not isinstance(backup_path, str):
            self.logger.error(f"Backup path must be a string, got {type(backup_path)}")
            raise TypeError(f"Backup path must be a string, got {type(backup_path)}")

        if not backup_path:
            self.logger.error("Backup path cannot be empty")
            raise ValueError("Backup path cannot be empty")

        # Check if parent directory exists and is writable
        parent_dir = os.path.dirname(backup_path)
        if parent_dir and not os.path.exists(parent_dir):
            self.logger.error(f"Parent directory does not exist: {parent_dir}")
            raise FileNotFoundError(f"Parent directory does not exist: {parent_dir}")

        if parent_dir and not os.access(parent_dir, os.W_OK):
            self.logger.error(f"Parent directory is not writable: {parent_dir}")
            raise PermissionError(f"Parent directory is not writable: {parent_dir}")

        try:
            with open(backup_path, 'w') as backup_file:
                self.config.write(backup_file)

            self.logger.info(f"Configuration backed up to {backup_path}")
            return backup_path

        except PermissionError as e:
            self.logger.error(f"Permission denied writing backup file {backup_path}: {str(e)}")
            raise
        except OSError as e:
            self.logger.error(f"OS error writing backup file {backup_path}: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error backing up configuration: {str(e)}")
            raise
    
    def get_all_config(self) -> Dict[str, Dict[str, Any]]:
        """Get all configuration as nested dictionary."""
        config_dict = {}
        
        for section in self.config.sections():
            config_dict[section] = self.get_section(section)
        
        return config_dict
