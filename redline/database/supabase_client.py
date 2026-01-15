#!/usr/bin/env python3
"""
REDLINE Supabase Client
Helper functions for interacting with Supabase database.
"""

import os
import logging
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime, timedelta

try:
    from supabase import create_client, Client
    from supabase.lib.client_options import ClientOptions
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

from .supabase_models import (
    Profile, UserSubscription, TimeSeriesCollection, TimeSeriesMetadata,
    UsageLog, UsageCheckResponse, HoursDeductionResponse, HoursAdditionResponse
)

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Client for interacting with Supabase database."""
    
    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        """
        Initialize Supabase client.
        
        Args:
            url: Supabase project URL (defaults to SUPABASE_URL env var)
            key: Supabase anon/service key (defaults to SUPABASE_KEY env var)
        """
        if not SUPABASE_AVAILABLE:
            raise ImportError(
                "supabase-py is not installed. Install with: pip install supabase"
            )
        
        self.url = url or os.getenv('SUPABASE_URL')
        self.key = key or os.getenv('SUPABASE_KEY')
        
        if not self.url or not self.key:
            raise ValueError(
                "Supabase URL and key must be provided via parameters or "
                "SUPABASE_URL and SUPABASE_KEY environment variables"
            )
        
        self.client: Client = create_client(self.url, self.key)
        self.logger = logging.getLogger(__name__)
    
    # ========================================================================
    # User & Profile Methods
    # ========================================================================
    
    def get_user_profile(self, user_id: UUID) -> Optional[Profile]:
        """Get user profile by ID."""
        try:
            response = self.client.table('profiles').select('*').eq('id', str(user_id)).single().execute()
            return Profile(**response.data) if response.data else None
        except Exception as e:
            self.logger.error(f"Error fetching profile for user {user_id}: {e}")
            return None
    
    def update_user_profile(self, user_id: UUID, updates: Dict[str, Any]) -> Optional[Profile]:
        """Update user profile."""
        try:
            response = self.client.table('profiles').update(updates).eq('id', str(user_id)).execute()
            return Profile(**response.data[0]) if response.data else None
        except Exception as e:
            self.logger.error(f"Error updating profile for user {user_id}: {e}")
            return None
    
    # ========================================================================
    # Subscription & Usage Methods
    # ========================================================================
    
    def get_user_subscription(self, user_id: UUID) -> Optional[UserSubscription]:
        """Get user's subscription."""
        try:
            response = self.client.table('user_subscriptions').select('*').eq('user_id', str(user_id)).single().execute()
            return UserSubscription(**response.data) if response.data else None
        except Exception as e:
            self.logger.error(f"Error fetching subscription for user {user_id}: {e}")
            return None
    
    def check_usage_hours(self, user_id: UUID, required_hours: float = 0.01) -> UsageCheckResponse:
        """
        Check if user has sufficient hours.
        
        Args:
            user_id: User UUID
            required_hours: Minimum hours required
            
        Returns:
            UsageCheckResponse with check result
        """
        try:
            subscription = self.get_user_subscription(user_id)
            if not subscription:
                return UsageCheckResponse(
                    has_sufficient_hours=False,
                    remaining_hours=0.0,
                    required_hours=required_hours
                )
            
            has_sufficient = subscription.remaining_hours >= required_hours
            return UsageCheckResponse(
                has_sufficient_hours=has_sufficient,
                remaining_hours=subscription.remaining_hours,
                required_hours=required_hours
            )
        except Exception as e:
            self.logger.error(f"Error checking usage hours for user {user_id}: {e}")
            return UsageCheckResponse(
                has_sufficient_hours=False,
                remaining_hours=0.0,
                required_hours=required_hours
            )
    
    def deduct_hours(self, user_id: UUID, hours: float) -> HoursDeductionResponse:
        """
        Deduct hours from user's subscription atomically.
        
        Args:
            user_id: User UUID
            hours: Hours to deduct
            
        Returns:
            HoursDeductionResponse with result
        """
        try:
            # Use Supabase RPC function for atomic operation
            response = self.client.rpc('deduct_hours', {
                'p_user_id': str(user_id),
                'p_hours': hours
            }).execute()
            
            success = response.data if response.data else False
            
            # Get updated remaining hours
            subscription = self.get_user_subscription(user_id)
            remaining = subscription.remaining_hours if subscription else 0.0
            
            return HoursDeductionResponse(
                success=success,
                remaining_hours=remaining,
                deducted_hours=hours
            )
        except Exception as e:
            self.logger.error(f"Error deducting hours for user {user_id}: {e}")
            return HoursDeductionResponse(
                success=False,
                remaining_hours=0.0,
                deducted_hours=hours
            )
    
    def add_hours(self, user_id: UUID, hours: float) -> HoursAdditionResponse:
        """
        Add hours to user's subscription.
        
        Args:
            user_id: User UUID
            hours: Hours to add
            
        Returns:
            HoursAdditionResponse with result
        """
        try:
            # Use Supabase RPC function
            self.client.rpc('add_hours', {
                'p_user_id': str(user_id),
                'p_hours': hours
            }).execute()
            
            # Get updated total hours
            subscription = self.get_user_subscription(user_id)
            total = subscription.remaining_hours if subscription else hours
            
            return HoursAdditionResponse(
                success=True,
                total_hours=total,
                added_hours=hours
            )
        except Exception as e:
            self.logger.error(f"Error adding hours for user {user_id}: {e}")
            return HoursAdditionResponse(
                success=False,
                total_hours=0.0,
                added_hours=hours
            )
    
    def get_remaining_hours(self, user_id: UUID) -> float:
        """Get user's remaining hours."""
        subscription = self.get_user_subscription(user_id)
        return subscription.remaining_hours if subscription else 0.0
    
    # ========================================================================
    # Time-Series Collection Methods
    # ========================================================================
    
    def create_collection(self, user_id: UUID, name: str, description: Optional[str] = None, 
                         tags: Optional[List[str]] = None) -> Optional[TimeSeriesCollection]:
        """Create a new time-series collection."""
        try:
            data = {
                'user_id': str(user_id),
                'name': name,
                'description': description,
                'tags': tags
            }
            response = self.client.table('time_series_collections').insert(data).execute()
            return TimeSeriesCollection(**response.data[0]) if response.data else None
        except Exception as e:
            self.logger.error(f"Error creating collection for user {user_id}: {e}")
            return None
    
    def get_collections(self, user_id: UUID) -> List[TimeSeriesCollection]:
        """Get all collections for a user."""
        try:
            response = self.client.table('time_series_collections').select('*').eq('user_id', str(user_id)).execute()
            return [TimeSeriesCollection(**item) for item in response.data]
        except Exception as e:
            self.logger.error(f"Error fetching collections for user {user_id}: {e}")
            return []
    
    def get_collection(self, collection_id: UUID) -> Optional[TimeSeriesCollection]:
        """Get a specific collection by ID."""
        try:
            response = self.client.table('time_series_collections').select('*').eq('id', str(collection_id)).single().execute()
            return TimeSeriesCollection(**response.data) if response.data else None
        except Exception as e:
            self.logger.error(f"Error fetching collection {collection_id}: {e}")
            return None
    
    # ========================================================================
    # Time-Series Metadata Methods
    # ========================================================================
    
    def create_series_metadata(self, collection_id: UUID, series_id: str, 
                               measurement_keys: List[str], **kwargs) -> Optional[TimeSeriesMetadata]:
        """Create metadata for a time-series."""
        try:
            data = {
                'collection_id': str(collection_id),
                'series_id': series_id,
                'measurement_keys': measurement_keys,
                **kwargs
            }
            response = self.client.table('time_series_metadata').insert(data).execute()
            return TimeSeriesMetadata(**response.data[0]) if response.data else None
        except Exception as e:
            self.logger.error(f"Error creating series metadata: {e}")
            return None
    
    def get_series_metadata(self, collection_id: UUID, series_id: str) -> Optional[TimeSeriesMetadata]:
        """Get metadata for a specific series."""
        try:
            response = (
                self.client.table('time_series_metadata')
                .select('*')
                .eq('collection_id', str(collection_id))
                .eq('series_id', series_id)
                .single()
                .execute()
            )
            return TimeSeriesMetadata(**response.data) if response.data else None
        except Exception as e:
            self.logger.error(f"Error fetching series metadata: {e}")
            return None
    
    def update_series_metadata(self, metadata_id: UUID, updates: Dict[str, Any]) -> Optional[TimeSeriesMetadata]:
        """Update series metadata."""
        try:
            response = (
                self.client.table('time_series_metadata')
                .update(updates)
                .eq('id', str(metadata_id))
                .execute()
            )
            return TimeSeriesMetadata(**response.data[0]) if response.data else None
        except Exception as e:
            self.logger.error(f"Error updating series metadata: {e}")
            return None
    
    # ========================================================================
    # Usage Logging Methods
    # ========================================================================
    
    def log_usage(self, user_id: UUID, event_type: str, duration_hours: float,
                  started_at: Optional[datetime] = None, finished_at: Optional[datetime] = None,
                  success: bool = True, metadata: Optional[Dict[str, Any]] = None) -> Optional[UsageLog]:
        """Log usage for billing reconciliation."""
        try:
            data = {
                'user_id': str(user_id),
                'event_type': event_type,
                'duration_hours': duration_hours,
                'started_at': started_at.isoformat() if started_at else datetime.utcnow().isoformat(),
                'finished_at': finished_at.isoformat() if finished_at else None,
                'success': success,
                'metadata': metadata
            }
            response = self.client.table('usage_logs').insert(data).execute()
            return UsageLog(**response.data[0]) if response.data else None
        except Exception as e:
            self.logger.error(f"Error logging usage for user {user_id}: {e}")
            return None
    
    def get_usage_logs(self, user_id: UUID, limit: int = 100, 
                      start_date: Optional[datetime] = None) -> List[UsageLog]:
        """Get usage logs for a user."""
        try:
            query = (
                self.client.table('usage_logs')
                .select('*')
                .eq('user_id', str(user_id))
                .order('started_at', desc=True)
                .limit(limit)
            )
            
            if start_date:
                query = query.gte('started_at', start_date.isoformat())
            
            response = query.execute()
            return [UsageLog(**item) for item in response.data]
        except Exception as e:
            self.logger.error(f"Error fetching usage logs for user {user_id}: {e}")
            return []


# ============================================================================
# Convenience Functions
# ============================================================================

def get_supabase_client() -> SupabaseClient:
    """Get a configured Supabase client from environment variables."""
    return SupabaseClient()
