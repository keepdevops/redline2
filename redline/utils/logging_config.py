#!/usr/bin/env python3
"""
REDLINE Logging Configuration
Centralized logging setup and configuration.
"""

import logging
import logging.handlers
import os
import sys
from typing import Optional, Dict, Any
from datetime import datetime

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: Optional[str] = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    console_output: bool = True
) -> logging.Logger:
    """
    Setup centralized logging for REDLINE application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        log_format: Custom log format (optional)
        max_file_size: Maximum size of log file before rotation
        backup_count: Number of backup log files to keep
        console_output: Whether to output logs to console
        
    Returns:
        Configured logger instance
    """
    # Default log format
    if log_format is None:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        try:
            # Ensure log directory exists
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            # Create rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_file_size,
                backupCount=backup_count
            )
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
        except Exception as e:
            # If file logging fails, log to console
            logger.error(f"Failed to setup file logging: {str(e)}")
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

def set_log_level(logger_name: str, level: str):
    """
    Set logging level for a specific logger.
    
    Args:
        logger_name: Name of the logger
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.getLogger(logger_name).setLevel(numeric_level)

def log_performance(func):
    """
    Decorator to log function performance.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function
    """
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"{func.__name__} completed in {duration:.3f} seconds")
            return result
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.error(f"{func.__name__} failed after {duration:.3f} seconds: {str(e)}")
            raise
    
    return wrapper

def log_function_call(func):
    """
    Decorator to log function calls with parameters.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function
    """
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        
        # Log function call
        args_str = ', '.join([str(arg) for arg in args])
        kwargs_str = ', '.join([f"{k}={v}" for k, v in kwargs.items()])
        params_str = ', '.join(filter(None, [args_str, kwargs_str]))
        
        logger.debug(f"Calling {func.__name__}({params_str})")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} returned: {type(result).__name__}")
            return result
            
        except Exception as e:
            logger.error(f"{func.__name__} raised {type(e).__name__}: {str(e)}")
            raise
    
    return wrapper

class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return get_logger(self.__class__.__module__ + '.' + self.__class__.__name__)

def configure_third_party_logging():
    """Configure logging for third-party libraries."""
    # Reduce verbosity of third-party libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)
    
    # Set specific levels for REDLINE modules
    logging.getLogger('redline').setLevel(logging.DEBUG)

def get_logging_stats() -> Dict[str, Any]:
    """
    Get logging statistics.
    
    Returns:
        Dictionary with logging statistics
    """
    stats = {
        'total_loggers': len(logging.Logger.manager.loggerDict),
        'handlers': [],
        'log_levels': {}
    }
    
    # Get handler information
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler_info = {
            'type': type(handler).__name__,
            'level': handler.level,
            'formatter': type(handler.formatter).__name__ if handler.formatter else None
        }
        
        if hasattr(handler, 'baseFilename'):
            handler_info['filename'] = handler.baseFilename
        
        stats['handlers'].append(handler_info)
    
    # Get logger levels
    for name, logger in logging.Logger.manager.loggerDict.items():
        if isinstance(logger, logging.Logger):
            stats['log_levels'][name] = logger.level
    
    return stats

def create_log_entry(message: str, level: str = "INFO", module: str = None, **kwargs) -> Dict[str, Any]:
    """
    Create a structured log entry.
    
    Args:
        message: Log message
        level: Log level
        module: Module name
        **kwargs: Additional fields
        
    Returns:
        Dictionary representing log entry
    """
    entry = {
        'timestamp': datetime.now().isoformat(),
        'level': level.upper(),
        'message': message,
        'module': module
    }
    
    # Add additional fields
    entry.update(kwargs)
    
    return entry

def log_structured_data(data: Dict[str, Any], level: str = "INFO", logger_name: str = None):
    """
    Log structured data in a consistent format.
    
    Args:
        data: Data to log
        level: Log level
        logger_name: Logger name
    """
    logger = get_logger(logger_name or __name__)
    
    # Convert data to string representation
    data_str = ', '.join([f"{k}={v}" for k, v in data.items()])
    
    # Log based on level
    log_method = getattr(logger, level.lower(), logger.info)
    log_method(f"Structured data: {data_str}")
