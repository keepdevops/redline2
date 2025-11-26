#!/usr/bin/env python3
"""
Yahoo Finance Date Handler
Handles date validation, parsing, and period calculation for Yahoo downloads.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class YahooDateHandler:
    """Helper class for handling dates in Yahoo Finance downloads."""
    
    @staticmethod
    def parse_and_validate_dates(start_date: str = None, end_date: str = None) -> Tuple[Optional[datetime], Optional[datetime], str, str]:
        """
        Parse and validate date strings.
        
        Args:
            start_date: Start date string (YYYY-MM-DD)
            end_date: End date string (YYYY-MM-DD)
            
        Returns:
            Tuple of (start_dt, end_dt, start_date, end_date) with validated dates
        """
        # Parse dates
        start_dt = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        
        # Validate dates
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)  # Normalize to midnight
        if end_dt and end_dt > today:
            logger.warning(f"End date {end_date} is in the future, adjusting to today")
            end_dt = today
            end_date = today.strftime('%Y-%m-%d')
        
        if start_dt and end_dt and start_dt > end_dt:
            raise ValueError(f"Start date {start_date} cannot be after end date {end_date}")
        
        # Ensure minimum date range (at least 1 day)
        if start_dt and end_dt:
            days_diff = (end_dt - start_dt).days
            if days_diff < 1:
                logger.warning(f"Date range too short ({days_diff} days), extending to 1 day")
                start_dt = end_dt - timedelta(days=1)
                start_date = start_dt.strftime('%Y-%m-%d')
        
        return start_dt, end_dt, start_date, end_date
    
    @staticmethod
    def calculate_period(days_diff: int) -> str:
        """
        Calculate yfinance period string based on number of days.
        
        Args:
            days_diff: Number of days in the date range
            
        Returns:
            Period string for yfinance (e.g., "5d", "1mo", "1y")
        """
        if days_diff <= 5:
            return "5d"
        elif days_diff <= 30:
            return "1mo"
        elif days_diff <= 90:
            return "3mo"
        elif days_diff <= 180:
            return "6mo"
        elif days_diff <= 365:
            return "1y"
        elif days_diff <= 730:
            return "2y"
        elif days_diff <= 1825:
            return "5y"
        else:
            return "max"
    
    @staticmethod
    def get_inclusive_end_date(end_dt: datetime, today: datetime) -> datetime:
        """
        Get inclusive end date for yfinance (adds 1 day since yfinance's end is exclusive).
        
        Args:
            end_dt: End date
            today: Today's date
            
        Returns:
            Inclusive end date (end_dt + 1 day, but not beyond today + 1)
        """
        end_dt_inclusive = end_dt + timedelta(days=1)
        # Ensure we don't go beyond today
        if end_dt_inclusive > today:
            end_dt_inclusive = today + timedelta(days=1)
        return end_dt_inclusive
    
    @staticmethod
    def normalize_timezone(data, start_dt=None, end_dt=None):
        """
        Normalize timezone-aware index to timezone-naive and filter by date range.
        
        Args:
            data: DataFrame with timezone-aware index
            start_dt: Optional start date for filtering
            end_dt: Optional end date for filtering
            
        Returns:
            DataFrame with timezone-naive index, filtered by date range
        """
        if data.empty:
            return data
        
        # Normalize timezone-aware index to timezone-naive for comparison
        if hasattr(data.index, 'tz') and data.index.tz is not None:
            data.index = data.index.tz_localize(None)
        
        # Filter to the requested date range
        if start_dt:
            data = data[data.index >= start_dt]
        if end_dt:
            # Include data up to and including end date
            data = data[data.index <= end_dt]
        
        return data

