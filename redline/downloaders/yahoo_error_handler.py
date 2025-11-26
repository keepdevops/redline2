#!/usr/bin/env python3
"""
Yahoo Finance Error Handler
Handles error detection, classification, and user-friendly error messages.
"""

import logging
from typing import Tuple
from .exceptions import RateLimitError

logger = logging.getLogger(__name__)


class YahooErrorHandler:
    """Helper class for handling errors in Yahoo Finance downloads."""
    
    @staticmethod
    def detect_error_type(error: Exception, error_msg: str) -> Tuple[str, bool]:
        """
        Detect the type of error from yfinance.
        
        Args:
            error: The exception object
            error_msg: String representation of the error
            
        Returns:
            Tuple of (error_type, is_rate_limit) where error_type is one of:
            'rate_limit', 'yfinance_error', 'curl_error', 'other'
        """
        error_lower = error_msg.lower()
        
        # Detect rate limiting indicators
        is_rate_limit = (
            "too many requests" in error_lower or
            "rate limit" in error_lower or
            "429" in error_msg or
            "throttled" in error_lower or
            ("exceeded" in error_lower and "request" in error_lower)
        )
        
        # Check for HTTPError with 429 status
        if hasattr(error, 'response'):
            try:
                if hasattr(error.response, 'status_code'):
                    if error.response.status_code == 429:
                        is_rate_limit = True
            except:
                pass
        
        if is_rate_limit:
            return 'rate_limit', True
        
        # Detect yfinance library errors (including browser impersonation issues)
        is_yfinance_error = (
            "impersonating" in error_lower or
            "user-agent" in error_lower or
            "not supported" in error_lower or
            "yfinance" in error_lower or
            ("chrome" in error_lower and "not supported" in error_lower) or
            ("impersonating chrome" in error_lower)
        )
        
        if is_yfinance_error:
            return 'yfinance_error', False
        
        # Detect curl_cffi errors
        is_curl_error = (
            "curl_cffi" in error_lower or
            "setopt" in error_lower or
            "curl" in error_lower
        )
        
        if is_curl_error:
            return 'curl_error', False
        
        return 'other', False
    
    @staticmethod
    def handle_rate_limit_error(ticker: str, min_interval: float) -> RateLimitError:
        """
        Handle rate limit error by creating RateLimitError with retry info.
        
        Args:
            ticker: Ticker symbol
            min_interval: Minimum request interval in seconds
            
        Returns:
            RateLimitError with retry information
        """
        logger.warning(f"Rate limited for {ticker} from Yahoo Finance")
        retry_after = int(min_interval * 12)  # Suggest waiting ~12x the interval
        return RateLimitError(
            f'Rate limit exceeded for Yahoo Finance while downloading {ticker}',
            retry_after=retry_after,
            source='yahoo'
        )
    
    @staticmethod
    def create_error_message(error_type: str, error_msg: str, ticker: str) -> str:
        """
        Create user-friendly error message based on error type.
        
        Args:
            error_type: Type of error ('yfinance_error', 'curl_error', 'other')
            error_msg: Original error message
            ticker: Ticker symbol
            
        Returns:
            User-friendly error message
        """
        if error_type == 'yfinance_error':
            return (
                f'yfinance library error: {error_msg}. '
                f'This may be a temporary issue with Yahoo Finance. '
                f'Please try again in a few moments or use a different data source (e.g., Stooq).'
            )
        
        elif error_type == 'curl_error':
            # Provide specific guidance for curl errors
            if 'setopt' in error_msg.lower() and ('10002' in error_msg or '43' in error_msg or 'curl: (43)' in error_msg):
                return (
                    f'curl_cffi library error (curl error 43): This is a low-level library compatibility issue. '
                    f'Possible solutions: (1) Update curl_cffi: pip install --upgrade curl-cffi, '
                    f'(2) Use Stooq data source instead, (3) Wait a few minutes and retry, '
                    f'or (4) Restart the application. Error details: {error_msg}'
                )
            else:
                return (
                    f'Yahoo Finance connection error (curl_cffi): {error_msg}. '
                    f'This may be a temporary library issue. Try: (1) Use Stooq data source, '
                    f'(2) Wait and retry, or (3) Update curl_cffi: pip install --upgrade curl-cffi'
                )
        
        else:
            return error_msg
    
    @staticmethod
    def is_yfinance_related_error(error_msg: str) -> bool:
        """
        Check if error is related to yfinance/curl (should be propagated to route).
        
        Args:
            error_msg: Error message string
            
        Returns:
            True if error is yfinance/curl related
        """
        error_lower = error_msg.lower()
        return (
            'yfinance' in error_lower or 
            'impersonating' in error_lower or 
            'curl' in error_lower or 
            'setopt' in error_lower or 
            'curl_cffi' in error_lower
        )

