#!/usr/bin/env python3
"""
REDLINE Database Migration Utilities
Helpers for migrating from local DuckDB to Supabase.
"""

import os
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime

try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False

from .supabase_client import SupabaseClient
from .supabase_models import TimeSeriesCollection, TimeSeriesMetadata

logger = logging.getLogger(__name__)


class MigrationHelper:
    """Helper for migrating data from local DuckDB to Supabase."""
    
    def __init__(self, supabase_client: SupabaseClient, duckdb_path: Optional[str] = None):
        """
        Initialize migration helper.
        
        Args:
            supabase_client: Configured Supabase client
            duckdb_path: Path to local DuckDB file (optional)
        """
        self.supabase = supabase_client
        self.duckdb_path = duckdb_path
        self.logger = logging.getLogger(__name__)
    
    def migrate_user_configs(self, user_id: str, local_configs: Dict[str, Any]) -> bool:
        """
        Migrate user configurations from local to Supabase.
        
        Args:
            user_id: User UUID
            local_configs: Dictionary of local configuration
            
        Returns:
            True if successful
        """
        try:
            # Migrate API downloader configs
            if 'api_downloaders' in local_configs:
                for name, config in local_configs['api_downloaders'].items():
                    self.supabase.client.table('api_downloader_configs').insert({
                        'user_id': user_id,
                        'name': name,
                        'config_json': config
                    }).execute()
            
            # Migrate analysis configs
            if 'analysis_configs' in local_configs:
                for name, config in local_configs['analysis_configs'].items():
                    self.supabase.client.table('analysis_configs').insert({
                        'user_id': user_id,
                        'name': name,
                        'config_json': config
                    }).execute()
            
            self.logger.info(f"Migrated configs for user {user_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error migrating configs: {e}")
            return False
    
    def migrate_time_series_metadata(self, user_id: str, collection_name: str,
                                   series_data: List[Dict[str, Any]]) -> bool:
        """
        Migrate time-series metadata from local to Supabase.
        
        Args:
            user_id: User UUID
            collection_name: Name for the collection
            series_data: List of series metadata dictionaries
            
        Returns:
            True if successful
        """
        try:
            # Create collection
            collection = self.supabase.create_collection(
                user_id=user_id,
                name=collection_name,
                description=f"Migrated from local storage on {datetime.utcnow().isoformat()}"
            )
            
            if not collection:
                self.logger.error("Failed to create collection")
                return False
            
            # Migrate each series
            for series in series_data:
                self.supabase.create_series_metadata(
                    collection_id=collection.id,
                    series_id=series.get('series_id', series.get('ticker', 'unknown')),
                    measurement_keys=series.get('measurement_keys', 
                                              list(series.get('measurements', {}).keys())),
                    name=series.get('name'),
                    description=series.get('description'),
                    source_format=series.get('format'),
                    storage_key=series.get('storage_key'),
                    storage_bucket=series.get('storage_bucket'),
                    first_timestamp=series.get('first_timestamp'),
                    last_timestamp=series.get('last_timestamp'),
                    row_count=series.get('row_count')
                )
            
            self.logger.info(f"Migrated {len(series_data)} series to collection {collection_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error migrating time-series metadata: {e}")
            return False
    
    def export_duckdb_metadata(self, duckdb_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Export metadata from DuckDB for migration.
        
        Args:
            duckdb_path: Path to DuckDB file (uses instance path if not provided)
            
        Returns:
            Dictionary with exported metadata
        """
        if not DUCKDB_AVAILABLE:
            self.logger.error("DuckDB not available")
            return {}
        
        db_path = duckdb_path or self.duckdb_path
        if not db_path or not os.path.exists(db_path):
            self.logger.warning(f"DuckDB file not found: {db_path}")
            return {}
        
        try:
            conn = duckdb.connect(db_path)
            
            # Get table names
            tables = conn.execute("SHOW TABLES").fetchall()
            
            metadata = {
                'tables': [],
                'series_info': []
            }
            
            for table in tables:
                table_name = table[0]
                # Get schema
                schema = conn.execute(f"DESCRIBE {table_name}").fetchall()
                
                # Get row count
                row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                
                # Get date range if timestamp column exists
                date_range = None
                try:
                    date_range = conn.execute(
                        f"SELECT MIN(timestamp), MAX(timestamp) FROM {table_name}"
                    ).fetchone()
                except:
                    pass
                
                metadata['tables'].append({
                    'name': table_name,
                    'schema': [{'column': col[0], 'type': col[1]} for col in schema],
                    'row_count': row_count,
                    'date_range': date_range
                })
            
            conn.close()
            return metadata
        except Exception as e:
            self.logger.error(f"Error exporting DuckDB metadata: {e}")
            return {}


def create_initial_subscription(user_id: str, supabase_client: SupabaseClient, 
                                initial_hours: float = 0.0) -> bool:
    """
    Create initial subscription for a user.
    
    Args:
        user_id: User UUID
        supabase_client: Supabase client
        initial_hours: Initial hours to grant
        
    Returns:
        True if successful
    """
    try:
        supabase_client.client.table('user_subscriptions').insert({
            'user_id': user_id,
            'status': 'active',
            'remaining_hours': initial_hours
        }).execute()
        return True
    except Exception as e:
        logger.error(f"Error creating initial subscription: {e}")
        return False


def seed_subscription_plans(supabase_client: SupabaseClient) -> bool:
    """
    Seed default subscription plans if they don't exist.
    
    Args:
        supabase_client: Supabase client
        
    Returns:
        True if successful
    """
    try:
        plans = [
            {'name': '5 Hours Pack', 'hours': 5, 'price_usd': 25.00, 'sort_order': 1},
            {'name': '10 Hours Pack', 'hours': 10, 'price_usd': 45.00, 'sort_order': 2},
            {'name': '20 Hours Pack', 'hours': 20, 'price_usd': 80.00, 'sort_order': 3},
            {'name': '50 Hours Pack', 'hours': 50, 'price_usd': 180.00, 'sort_order': 4}
        ]
        
        for plan in plans:
            try:
                supabase_client.client.table('subscription_plans').insert(plan).execute()
            except Exception:
                # Plan might already exist, skip
                pass
        
        logger.info("Seeded subscription plans")
        return True
    except Exception as e:
        logger.error(f"Error seeding subscription plans: {e}")
        return False
