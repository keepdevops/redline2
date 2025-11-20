"""
REDLINE Data Downloaders
Provides access to various financial data sources.
"""

from .base_downloader import BaseDownloader
from .yahoo_downloader import YahooDownloader
from .stooq_downloader import StooqDownloader
from .multi_source import MultiSourceDownloader
from .generic_api_downloader import GenericAPIDownloader

# Conditionally export Massive.com downloader if available
try:
    from .massive_downloader import MassiveDownloader
    try:
        from .massive_websocket import MassiveWebSocketClient
        __all__ = [
            'BaseDownloader',
            'YahooDownloader',
            'StooqDownloader',
            'MultiSourceDownloader',
            'GenericAPIDownloader',
            'MassiveDownloader',
            'MassiveWebSocketClient'
        ]
    except ImportError:
        __all__ = [
            'BaseDownloader',
            'YahooDownloader',
            'StooqDownloader',
            'MultiSourceDownloader',
            'GenericAPIDownloader',
            'MassiveDownloader'
        ]
except ImportError:
    __all__ = [
        'BaseDownloader',
        'YahooDownloader',
        'StooqDownloader',
        'MultiSourceDownloader',
        'GenericAPIDownloader'
    ]

