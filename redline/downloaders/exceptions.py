#!/usr/bin/env python3
"""
REDLINE Downloader Exceptions
Custom exceptions for downloader operations.
"""


class RateLimitError(Exception):
    """
    Exception raised when rate limit is exceeded for a data source.
    
    Attributes:
        message: Human-readable error message
        retry_after: Number of seconds to wait before retrying (optional)
        source: Name of the data source that rate limited (optional)
    """
    
    def __init__(self, message: str, retry_after: int = None, source: str = None):
        """
        Initialize RateLimitError.
        
        Args:
            message: Human-readable error message
            retry_after: Number of seconds to wait before retrying (optional)
            source: Name of the data source that rate limited (optional)
        """
        self.message = message
        self.retry_after = retry_after
        self.source = source
        super().__init__(self.message)
    
    def __str__(self):
        """Return string representation of the error."""
        base_msg = self.message
        if self.retry_after:
            minutes = self.retry_after // 60
            seconds = self.retry_after % 60
            if minutes > 0:
                time_msg = f"{minutes} minute(s)"
                if seconds > 0:
                    time_msg += f" and {seconds} second(s)"
            else:
                time_msg = f"{seconds} second(s)"
            base_msg += f" Please wait {time_msg} before retrying."
        if self.source:
            base_msg += f" (Source: {self.source})"
        return base_msg
    
    def to_dict(self):
        """
        Convert exception to dictionary for JSON serialization.
        
        Returns:
            Dictionary with error details
        """
        return {
            'error': self.message,
            'retry_after': self.retry_after,
            'source': self.source,
            'type': 'RateLimitError'
        }

