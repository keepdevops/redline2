"""
Stub for OptimizedDatabaseConnector
This was used for local DuckDB connections, but now we use Modal for data processing.
Keeping this stub to prevent import errors.
"""

import logging

logger = logging.getLogger(__name__)


class OptimizedDatabaseConnector:
    """Stub connector - data processing now handled by Modal"""

    def __init__(self, max_connections=8, cache_size=64, cache_ttl=300):
        """Initialize stub connector"""
        self.max_connections = max_connections
        self.cache_size = cache_size
        self.cache_ttl = cache_ttl
        logger.info("Using stub database connector - data processing handled by Modal")

    def get_performance_stats(self):
        """Return empty performance stats"""
        return {
            'active_connections': 0,
            'cache_hit_rate': 0.0,
            'avg_query_time': 0.0,
            'total_queries': 0,
            'message': 'Data processing now handled by Modal - local stats unavailable'
        }

    def close(self):
        """Stub close method"""
        pass
