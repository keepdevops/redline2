#!/usr/bin/env python3
"""
REDLINE Supabase Database Models
Pydantic models matching Supabase tables for type safety and validation.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from uuid import UUID


# ============================================================================
# Base Models
# ============================================================================

class TimestampMixin(BaseModel):
    """Mixin for models with created_at/updated_at timestamps."""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# User & Authentication Models
# ============================================================================

class Profile(TimestampMixin):
    """User profile extending auth.users."""
    id: UUID
    email: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None


class ProfileCreate(BaseModel):
    """Profile creation payload."""
    email: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None


class ProfileUpdate(BaseModel):
    """Profile update payload."""
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None


# ============================================================================
# Subscription Models
# ============================================================================

class SubscriptionPlan(BaseModel):
    """Predefined subscription plan."""
    id: int
    name: str
    hours: float
    price_usd: float
    stripe_price_id: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0
    created_at: Optional[datetime] = None


class SubscriptionPlanCreate(BaseModel):
    """Subscription plan creation payload."""
    name: str
    hours: float
    price_usd: float
    stripe_price_id: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0


class UserSubscription(TimestampMixin):
    """User subscription state with remaining hours."""
    id: int
    user_id: UUID
    plan_id: Optional[int] = None
    status: str = Field(default="active", pattern="^(active|trialing|canceled|past_due)$")
    remaining_hours: float = 0.0
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    stripe_subscription_id: Optional[str] = None


class UserSubscriptionCreate(BaseModel):
    """User subscription creation payload."""
    user_id: UUID
    plan_id: Optional[int] = None
    status: str = "active"
    remaining_hours: float = 0.0
    stripe_subscription_id: Optional[str] = None


class StripeCustomer(BaseModel):
    """Stripe customer mapping."""
    user_id: UUID
    stripe_customer_id: str
    created_at: Optional[datetime] = None


class StripeCustomerCreate(BaseModel):
    """Stripe customer creation payload."""
    user_id: UUID
    stripe_customer_id: str


class StripePayment(BaseModel):
    """Stripe payment audit log."""
    id: int
    user_id: UUID
    stripe_invoice_id: Optional[str] = None
    stripe_payment_intent_id: Optional[str] = None
    amount_usd: float
    hours_granted: float
    status: str = Field(pattern="^(pending|succeeded|failed|refunded)$")
    created_at: Optional[datetime] = None


class StripePaymentCreate(BaseModel):
    """Stripe payment creation payload."""
    user_id: UUID
    stripe_invoice_id: Optional[str] = None
    stripe_payment_intent_id: Optional[str] = None
    amount_usd: float
    hours_granted: float
    status: str = "pending"


# ============================================================================
# Time-Series Data Models
# ============================================================================

class TimeSeriesCollection(TimestampMixin):
    """Logical grouping of time-series data."""
    id: UUID
    user_id: UUID
    name: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class TimeSeriesCollectionCreate(BaseModel):
    """Time-series collection creation payload."""
    name: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class TimeSeriesCollectionUpdate(BaseModel):
    """Time-series collection update payload."""
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class TimeSeriesMetadata(BaseModel):
    """Metadata about a time-series."""
    id: UUID
    collection_id: Optional[UUID] = None
    series_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    measurement_keys: List[str] = Field(..., min_items=1)
    first_timestamp: Optional[datetime] = None
    last_timestamp: Optional[datetime] = None
    row_count: Optional[int] = None
    source_format: Optional[str] = None
    storage_key: Optional[str] = None  # S3/Wasabi key
    storage_bucket: Optional[str] = None  # S3/Wasabi bucket
    last_updated: Optional[datetime] = None


class TimeSeriesMetadataCreate(BaseModel):
    """Time-series metadata creation payload."""
    collection_id: Optional[UUID] = None
    series_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    measurement_keys: List[str] = Field(..., min_items=1)
    source_format: Optional[str] = None
    storage_key: Optional[str] = None
    storage_bucket: Optional[str] = None


class TimeSeriesMetadataUpdate(BaseModel):
    """Time-series metadata update payload."""
    name: Optional[str] = None
    description: Optional[str] = None
    measurement_keys: Optional[List[str]] = None
    first_timestamp: Optional[datetime] = None
    last_timestamp: Optional[datetime] = None
    row_count: Optional[int] = None
    storage_key: Optional[str] = None
    storage_bucket: Optional[str] = None


# ============================================================================
# Configuration Models
# ============================================================================

class APIDownloaderConfig(TimestampMixin):
    """Saved API downloader configuration."""
    id: UUID
    user_id: UUID
    name: str
    config_json: Dict[str, Any]


class APIDownloaderConfigCreate(BaseModel):
    """API downloader config creation payload."""
    name: str
    config_json: Dict[str, Any]


class APIDownloaderConfigUpdate(BaseModel):
    """API downloader config update payload."""
    name: Optional[str] = None
    config_json: Optional[Dict[str, Any]] = None


class AnalysisConfig(TimestampMixin):
    """Saved analysis/ML configuration."""
    id: UUID
    user_id: UUID
    name: str
    config_json: Dict[str, Any]


class AnalysisConfigCreate(BaseModel):
    """Analysis config creation payload."""
    name: str
    config_json: Dict[str, Any]


class AnalysisConfigUpdate(BaseModel):
    """Analysis config update payload."""
    name: Optional[str] = None
    config_json: Optional[Dict[str, Any]] = None


# ============================================================================
# Usage & Audit Models
# ============================================================================

class UsageLog(BaseModel):
    """Usage log entry for billing reconciliation."""
    id: int
    user_id: UUID
    event_type: str  # download, analysis, ml_train, query, etc.
    duration_hours: float
    started_at: datetime
    finished_at: Optional[datetime] = None
    success: bool = True
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None


class UsageLogCreate(BaseModel):
    """Usage log creation payload."""
    event_type: str
    duration_hours: float
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    success: bool = True
    metadata: Optional[Dict[str, Any]] = None


class AuditLog(BaseModel):
    """Audit log entry for compliance."""
    id: int
    user_id: Optional[UUID] = None
    action: str  # create, update, delete, download, etc.
    entity_type: str  # collection, series, config, etc.
    entity_id: Optional[UUID] = None
    timestamp: Optional[datetime] = None
    details: Optional[Dict[str, Any]] = None


class AuditLogCreate(BaseModel):
    """Audit log creation payload."""
    user_id: Optional[UUID] = None
    action: str
    entity_type: str
    entity_id: Optional[UUID] = None
    details: Optional[Dict[str, Any]] = None


# ============================================================================
# Request/Response Models
# ============================================================================

class UsageCheckResponse(BaseModel):
    """Response for usage hours check."""
    has_sufficient_hours: bool
    remaining_hours: float
    required_hours: float


class HoursDeductionResponse(BaseModel):
    """Response for hours deduction."""
    success: bool
    remaining_hours: float
    deducted_hours: float


class HoursAdditionResponse(BaseModel):
    """Response for hours addition."""
    success: bool
    total_hours: float
    added_hours: float
