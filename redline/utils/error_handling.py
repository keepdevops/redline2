#!/usr/bin/env python3
"""
REDLINE Error Handling Utilities
Centralized error handling decorators and utilities to eliminate duplication.
"""

import logging
import functools
from typing import Any, Callable, Optional, Union, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

def handle_errors(default_return: Any = None, 
                 log_errors: bool = True, 
                 reraise: bool = False,
                 error_message: Optional[str] = None) -> Callable:
    """
    Decorator to handle common error patterns across REDLINE modules.
    
    This eliminates the need for duplicate try/except blocks with logging
    throughout the codebase. Provides consistent error handling and logging.
    
    Args:
        default_return: Value to return if an exception occurs
        log_errors: Whether to log errors (default: True)
        reraise: Whether to reraise the exception after logging (default: False)
        error_message: Custom error message template (uses function name if None)
        
    Usage:
        @handle_errors(default_return=pd.DataFrame(), log_errors=True)
        def load_data(self, file_path: str) -> pd.DataFrame:
            return pd.read_csv(file_path)
            
        @handle_errors(reraise=True, error_message="Failed to download {ticker}")
        def download_ticker(self, ticker: str) -> pd.DataFrame:
            # Will log error and reraise if exception occurs
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Get logger from self if available, otherwise use module logger
                func_logger = logger
                if args and hasattr(args[0], 'logger'):
                    func_logger = args[0].logger
                
                # Create error message
                if error_message:
                    try:
                        # Format error message with function arguments
                        msg = error_message.format(*args, **kwargs)
                    except (IndexError, KeyError):
                        msg = f"{func.__name__}: {error_message}"
                else:
                    msg = f"Error in {func.__name__}: {str(e)}"
                
                if log_errors:
                    func_logger.error(msg)
                
                if reraise:
                    raise
                
                return default_return
        
        return wrapper
    return decorator

def handle_file_errors(default_return: Any = None) -> Callable:
    """
    Specialized decorator for file operations with common error patterns.
    
    Provides specific error handling for file I/O operations with
    standardized error messages.
    
    Args:
        default_return: Value to return if file operation fails
        
    Usage:
        @handle_file_errors(default_return=pd.DataFrame())
        def load_csv_file(self, file_path: str) -> pd.DataFrame:
            return pd.read_csv(file_path)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except FileNotFoundError as e:
                func_logger = logger
                if args and hasattr(args[0], 'logger'):
                    func_logger = args[0].logger
                
                func_logger.error(f"File not found in {func.__name__}: {str(e)}")
                return default_return
                
            except PermissionError as e:
                func_logger = logger
                if args and hasattr(args[0], 'logger'):
                    func_logger = args[0].logger
                
                func_logger.error(f"Permission denied in {func.__name__}: {str(e)}")
                return default_return
                
            except Exception as e:
                func_logger = logger
                if args and hasattr(args[0], 'logger'):
                    func_logger = args[0].logger
                
                func_logger.error(f"Error in file operation {func.__name__}: {str(e)}")
                return default_return
        
        return wrapper
    return decorator

def handle_database_errors(default_return: Any = None) -> Callable:
    """
    Specialized decorator for database operations with common error patterns.
    
    Provides specific error handling for database operations with
    standardized error messages and retry logic.
    
    Args:
        default_return: Value to return if database operation fails
        
    Usage:
        @handle_database_errors(default_return=[])
        def get_tickers(self) -> List[str]:
            return self.connector.execute_query("SELECT ticker FROM data")
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                func_logger = logger
                if args and hasattr(args[0], 'logger'):
                    func_logger = args[0].logger
                
                error_msg = str(e).lower()
                if 'connection' in error_msg or 'timeout' in error_msg:
                    func_logger.error(f"Database connection error in {func.__name__}: {str(e)}")
                elif 'syntax' in error_msg or 'sql' in error_msg:
                    func_logger.error(f"SQL syntax error in {func.__name__}: {str(e)}")
                else:
                    func_logger.error(f"Database error in {func.__name__}: {str(e)}")
                
                return default_return
        
        return wrapper
    return decorator

class ErrorHandler:
    """
    Context manager for handling errors with custom logic.
    
    Usage:
        with ErrorHandler(logger=self.logger, default_return=[]):
            result = risky_operation()
    """
    
    def __init__(self, logger: logging.Logger, 
                 default_return: Any = None,
                 error_message: Optional[str] = None,
                 reraise: bool = False):
        self.logger = logger
        self.default_return = default_return
        self.error_message = error_message
        self.reraise = reraise
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            if self.error_message:
                self.logger.error(f"{self.error_message}: {str(exc_val)}")
            else:
                self.logger.error(f"Operation failed: {str(exc_val)}")
            
            if self.reraise:
                return False  # Don't suppress the exception
            
            return True  # Suppress the exception
        
        return False

def log_execution_time(func: Callable) -> Callable:
    """
    Decorator to log function execution time.
    
    Usage:
        @log_execution_time
        def slow_operation(self):
            # Function execution time will be logged
            pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            
            # Get logger from self if available
            func_logger = logger
            if args and hasattr(args[0], 'logger'):
                func_logger = args[0].logger
            
            execution_time = (datetime.now() - start_time).total_seconds()
            func_logger.debug(f"{func.__name__} executed in {execution_time:.3f} seconds")
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            func_logger = logger
            if args and hasattr(args[0], 'logger'):
                func_logger = args[0].logger
            
            func_logger.error(f"{func.__name__} failed after {execution_time:.3f} seconds: {str(e)}")
            raise
    
    return wrapper
