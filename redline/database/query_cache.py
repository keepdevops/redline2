#!/usr/bin/env python3
"""
REDLINE Query Cache
Thread-safe query result cache with TTL.
"""

import logging
import threading
import time
import hashlib
from typing import Dict, Any, Optional
import pandas as pd

logger = logging.getLogger(__name__)


class QueryCache:
    """Thread-safe query result cache with TTL."""
    
    def __init__(self, max_size: int = 128, ttl_seconds: int = 300):
        """Initialize query cache."""
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
    
    def _generate_key(self, query: str, params: Dict[str, Any] = None) -> str:
        """Generate cache key for query and parameters."""
        cache_string = f"{query}:{str(params) if params else ''}"
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def get(self, query: str, params: Dict[str, Any] = None) -> Optional[pd.DataFrame]:
        """Get cached query result."""
        with self.lock:
            key = self._generate_key(query, params)
            
            if key in self.cache:
                cached_item = self.cache[key]
                
                # Check TTL
                if time.time() - cached_item['timestamp'] < self.ttl_seconds:
                    self.logger.debug(f"Cache hit for query: {query[:50]}...")
                    return cached_item['result'].copy()
                else:
                    # Expired, remove from cache
                    del self.cache[key]
                    self.logger.debug(f"Cache expired for query: {query[:50]}...")
            
            return None
    
    def set(self, query: str, result: pd.DataFrame, params: Dict[str, Any] = None):
        """Cache query result."""
        with self.lock:
            # Remove oldest entries if cache is full
            while len(self.cache) >= self.max_size:
                oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['timestamp'])
                del self.cache[oldest_key]
            
            key = self._generate_key(query, params)
            self.cache[key] = {
                'result': result.copy(),
                'timestamp': time.time()
            }
            self.logger.debug(f"Cached query result: {query[:50]}...")
    
    def clear(self):
        """Clear all cached results."""
        with self.lock:
            self.cache.clear()
        self.logger.info("Cleared query cache")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'ttl_seconds': self.ttl_seconds,
                'oldest_entry': min((item['timestamp'] for item in self.cache.values()), default=None),
                'newest_entry': max((item['timestamp'] for item in self.cache.values()), default=None)
            }

