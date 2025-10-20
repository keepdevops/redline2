#!/usr/bin/env python3
"""
REDLINE Logging Mixin
Centralized logging setup to eliminate duplication across all modules.
"""

import logging
from typing import Optional

class LoggingMixin:
    """
    Mixin class to provide consistent logging capabilities to any class.
    
    This eliminates the need for duplicate logging initialization across
    all REDLINE modules. Simply inherit from this class to get a logger
    property that automatically uses the correct module name.
    
    Usage:
        class MyClass(LoggingMixin):
            def some_method(self):
                self.logger.info("This will use the correct logger")
                self.logger.error("Error messages work too")
    """
    
    @property
    def logger(self) -> logging.Logger:
        """
        Get logger instance for the current class.
        
        Returns:
            Logger instance with module.class name
        """
        if not hasattr(self, '_logger'):
            # Use module.class format for better log organization
            module_name = self.__class__.__module__
            class_name = self.__class__.__name__
            logger_name = f"{module_name}.{class_name}"
            self._logger = logging.getLogger(logger_name)
        return self._logger
    
    def setup_logger(self, level: Optional[str] = None, 
                    formatter: Optional[logging.Formatter] = None) -> logging.Logger:
        """
        Setup logger with custom level and formatter.
        
        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            formatter: Custom formatter for log messages
            
        Returns:
            Configured logger instance
        """
        logger = self.logger
        
        if level:
            numeric_level = getattr(logging, level.upper(), logging.INFO)
            logger.setLevel(numeric_level)
        
        if formatter:
            # Remove existing handlers to avoid duplicates
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
            
            # Add new handler with custom formatter
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
