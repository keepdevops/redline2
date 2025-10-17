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
        try:
            if os.path.exists(self.config_path):
                self.config.read(self.config_path)
                self.logger.info(f"Loaded configuration from {self.config_path}")
            else:
                self.logger.info(f"Configuration file not found, creating default at {self.config_path}")
                self.create_default_config()
                
        except Exception as e:
            self.logger.error(f"Error loading configuration: {str(e)}")
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration file."""
        try:
            # Set default values
            for section, options in self.defaults.items():
                if not self.config.has_section(section):
                    self.config.add_section(section)
                
                for option, value in options.items():
                    self.config.set(section, option, value)
            
            # Save to file
            self.save_config()
            
        except Exception as e:
            self.logger.error(f"Error creating default configuration: {str(e)}")
    
    def save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w') as configfile:
                self.config.write(configfile)
            self.logger.info(f"Configuration saved to {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {str(e)}")
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
        try:
            if self.config.has_section(section) and self.config.has_option(section, option):
                value = self.config.get(section, option)
                
                # Try to convert to appropriate type
                if value.isdigit():
                    return int(value)
                elif value.lower() in ('true', 'false'):
                    return value.lower() == 'true'
                else:
                    return value
            else:
                return fallback
                
        except Exception as e:
            self.logger.error(f"Error getting config value [{section}]{option}: {str(e)}")
            return fallback
    
    def set(self, section: str, option: str, value: Any):
        """
        Set configuration value.
        
        Args:
            section: Configuration section
            option: Configuration option
            value: Value to set
        """
        try:
            if not self.config.has_section(section):
                self.config.add_section(section)
            
            self.config.set(section, option, str(value))
            
        except Exception as e:
            self.logger.error(f"Error setting config value [{section}]{option}: {str(e)}")
            raise
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get entire configuration section.
        
        Args:
            section: Configuration section name
            
        Returns:
            Dictionary of section options
        """
        try:
            if self.config.has_section(section):
                return dict(self.config[section])
            else:
                return {}
                
        except Exception as e:
            self.logger.error(f"Error getting config section {section}: {str(e)}")
            return {}
    
    def update_section(self, section: str, options: Dict[str, Any]):
        """
        Update entire configuration section.
        
        Args:
            section: Configuration section name
            options: Dictionary of options to set
        """
        try:
            if not self.config.has_section(section):
                self.config.add_section(section)
            
            for option, value in options.items():
                self.config.set(section, option, str(value))
                
        except Exception as e:
            self.logger.error(f"Error updating config section {section}: {str(e)}")
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
            try:
                os.makedirs(csv_dir, exist_ok=True)
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
        try:
            self.config.clear()
            self.create_default_config()
            self.logger.info("Configuration reset to defaults")
            
        except Exception as e:
            self.logger.error(f"Error resetting configuration: {str(e)}")
            raise
    
    def backup_config(self, backup_path: str = None):
        """
        Create backup of current configuration.
        
        Args:
            backup_path: Path for backup file (optional)
        """
        try:
            if backup_path is None:
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = f"data_config_backup_{timestamp}.ini"
            
            with open(backup_path, 'w') as backup_file:
                self.config.write(backup_file)
            
            self.logger.info(f"Configuration backed up to {backup_path}")
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Error backing up configuration: {str(e)}")
            raise
    
    def get_all_config(self) -> Dict[str, Dict[str, Any]]:
        """Get all configuration as nested dictionary."""
        config_dict = {}
        
        for section in self.config.sections():
            config_dict[section] = self.get_section(section)
        
        return config_dict
