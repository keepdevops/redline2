#!/usr/bin/env python3
"""
REDLINE Connection Pool
Thread-safe connection pool for database connections.
"""

import logging
import threading
import queue
import os

# Optional dependencies
try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    duckdb = None
    DUCKDB_AVAILABLE = False

logger = logging.getLogger(__name__)


class ConnectionPool:
    """Thread-safe connection pool for database connections."""
    
    def __init__(self, db_path: str, max_connections: int = 10):
        """Initialize connection pool."""
        self.db_path = db_path
        self.max_connections = max_connections
        self.pool = queue.Queue(maxsize=max_connections)
        self.lock = threading.Lock()
        self.active_connections = 0
        self.logger = logging.getLogger(__name__)
        
        # Pre-populate pool with initial connections
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize the connection pool with initial connections."""
        try:
            for _ in range(min(3, self.max_connections)):  # Start with 3 connections
                conn = self._create_connection()
                self.pool.put(conn)
                self.active_connections += 1
            self.logger.info(f"Initialized connection pool with {self.active_connections} connections")
        except Exception as e:
            self.logger.error(f"Failed to initialize connection pool: {str(e)}")
    
    def _create_connection(self):
        """Create a new database connection."""
        if not DUCKDB_AVAILABLE:
            raise ImportError("duckdb not available. Please install duckdb to use database features.")
        
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            conn = duckdb.connect(self.db_path)
            return conn
        except Exception as e:
            self.logger.error(f"Failed to create database connection: {str(e)}")
            raise
    
    def get_connection(self, timeout: int = 30):
        """Get a connection from the pool."""
        try:
            # Try to get existing connection
            conn = self.pool.get(timeout=timeout)
            return conn
        except queue.Empty:
            # Pool is empty, try to create new connection
            with self.lock:
                if self.active_connections < self.max_connections:
                    conn = self._create_connection()
                    self.active_connections += 1
                    self.logger.debug(f"Created new connection. Active: {self.active_connections}")
                    return conn
                else:
                    # Wait for a connection to become available
                    conn = self.pool.get(timeout=timeout)
                    return conn
    
    def return_connection(self, conn):
        """Return a connection to the pool."""
        try:
            self.pool.put_nowait(conn)
        except queue.Full:
            # Pool is full, close the connection
            conn.close()
            with self.lock:
                self.active_connections -= 1
            self.logger.debug(f"Closed excess connection. Active: {self.active_connections}")
    
    def close_all(self):
        """Close all connections in the pool."""
        with self.lock:
            while not self.pool.empty():
                try:
                    conn = self.pool.get_nowait()
                    conn.close()
                except queue.Empty:
                    break
            self.active_connections = 0
        self.logger.info("Closed all connections in pool")

