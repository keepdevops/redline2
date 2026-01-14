#!/usr/bin/env python3
"""
Supabase Client for REDLINE
Handles user management, job tracking, and usage logging
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Supabase client for user management and data storage"""

    def __init__(self):
        """Initialize Supabase client with credentials from environment"""
        if not SUPABASE_AVAILABLE:
            logger.warning("Supabase package not available. Install with: pip install supabase")
            self.client = None
            return

        self.url = os.environ.get('SUPABASE_URL')
        self.service_key = os.environ.get('SUPABASE_SERVICE_KEY')  # Service key for admin operations
        self.anon_key = os.environ.get('SUPABASE_ANON_KEY')  # Anon key for client-side

        # Validate URL format
        if not self.url:
            logger.warning("SUPABASE_URL not set in environment variables")
            self.client = None
            return

        if not self.url.startswith('https://'):
            logger.error(f"Invalid SUPABASE_URL format: {self.url}. Must start with https://")
            self.client = None
            return

        # Improved URL validation - check for supabase.co domain or localhost (for dev)
        if 'supabase.co' not in self.url and 'localhost' not in self.url and '127.0.0.1' not in self.url:
            logger.warning(f"SUPABASE_URL does not contain 'supabase.co' domain: {self.url}. This might be incorrect.")

        # Validate service key
        if not self.service_key:
            logger.warning("SUPABASE_SERVICE_KEY not set in environment variables")
            self.client = None
            return

        # Improved service key validation - check for JWT-like format instead of arbitrary length
        if len(self.service_key) < 50:
            logger.warning(f"SUPABASE_SERVICE_KEY appears short ({len(self.service_key)} chars). Supabase keys are typically 100+ characters.")

        # Basic JWT format check (should have two dots for header.payload.signature)
        if self.service_key.count('.') != 2:
            logger.warning(f"SUPABASE_SERVICE_KEY does not appear to be a valid JWT format (expected 2 dots, found {self.service_key.count('.')})")

        # Validate anon key (optional but recommended)
        if not self.anon_key:
            logger.info("SUPABASE_ANON_KEY not set. This is optional but recommended for client-side operations.")
        elif len(self.anon_key) < 50:
            logger.warning(f"SUPABASE_ANON_KEY appears short ({len(self.anon_key)} chars). Supabase keys are typically 100+ characters.")
        elif self.anon_key.count('.') != 2:
            logger.warning(f"SUPABASE_ANON_KEY does not appear to be a valid JWT format")

        # Attempt to create client
        logger.info(f"Initializing Supabase client with URL: {self.url}")
        self.client: Optional[Client] = create_client(self.url, self.service_key)

        if self.client:
            logger.info("Supabase client initialized successfully")
        else:
            logger.error("Failed to initialize Supabase client: create_client returned None")
            self.client = None

    def is_available(self) -> bool:
        """Check if Supabase client is available and configured"""
        return self.client is not None

    # ========================================================================
    # USER MANAGEMENT
    # ========================================================================

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user from Supabase by user ID

        Args:
            user_id: Supabase user ID (UUID)

        Returns:
            User data dict or None if not found
        """
        if not self.client:
            logger.warning("Cannot get user by ID: Supabase client not available")
            return None

        if not user_id:
            logger.error("Cannot get user: user_id is empty or None")
            return None

        if not isinstance(user_id, str):
            logger.error(f"Cannot get user: user_id must be string, got {type(user_id)}")
            return None

        logger.debug(f"Fetching user by ID: {user_id}")
        result = self.client.table('users').select('*').eq('id', user_id).execute()

        if not result:
            logger.warning(f"User query returned no result for ID: {user_id}")
            return None

        if not hasattr(result, 'data') or result.data is None:
            logger.warning(f"User query result has no data attribute for ID: {user_id}")
            return None

        if len(result.data) == 0:
            logger.info(f"User not found with ID: {user_id}")
            return None

        logger.debug(f"Successfully retrieved user: {user_id}")
        return result.data[0]

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user from Supabase by email

        Args:
            email: User email address

        Returns:
            User data dict or None if not found
        """
        if not self.client:
            logger.warning("Cannot get user by email: Supabase client not available")
            return None

        if not email:
            logger.error("Cannot get user: email is empty or None")
            return None

        if not isinstance(email, str):
            logger.error(f"Cannot get user: email must be string, got {type(email)}")
            return None

        if '@' not in email:
            logger.error(f"Cannot get user: email format invalid (missing @): {email}")
            return None

        logger.debug(f"Fetching user by email: {email}")
        result = self.client.table('users').select('*').eq('email', email).execute()

        if not result or not hasattr(result, 'data') or result.data is None:
            logger.warning(f"User query returned no valid result for email: {email}")
            return None

        if len(result.data) == 0:
            logger.info(f"User not found with email: {email}")
            return None

        logger.debug(f"Successfully retrieved user by email: {email}")
        return result.data[0]

    def get_user_by_stripe_customer(self, stripe_customer_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by Stripe customer ID

        Args:
            stripe_customer_id: Stripe customer ID

        Returns:
            User data dict or None if not found
        """
        if not self.client:
            logger.warning("Cannot get user by Stripe customer: Supabase client not available")
            return None

        if not stripe_customer_id:
            logger.error("Cannot get user: stripe_customer_id is empty or None")
            return None

        if not isinstance(stripe_customer_id, str):
            logger.error(f"Cannot get user: stripe_customer_id must be string, got {type(stripe_customer_id)}")
            return None

        if not stripe_customer_id.startswith('cus_'):
            logger.warning(f"Stripe customer ID has unexpected format: {stripe_customer_id} (expected 'cus_' prefix)")

        logger.debug(f"Fetching user by Stripe customer ID: {stripe_customer_id}")
        result = self.client.table('users').select('*').eq('stripe_customer_id', stripe_customer_id).execute()

        if not result or not hasattr(result, 'data') or result.data is None:
            logger.warning(f"User query returned no valid result for Stripe customer: {stripe_customer_id}")
            return None

        if len(result.data) == 0:
            logger.info(f"User not found with Stripe customer ID: {stripe_customer_id}")
            return None

        logger.debug(f"Successfully retrieved user by Stripe customer ID: {stripe_customer_id}")
        return result.data[0]

    def create_user_profile(self, user_id: str, email: str, stripe_customer_id: str,
                           name: Optional[str] = None, company: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Create user profile after Supabase Auth signup

        Args:
            user_id: Supabase user ID (from auth.users)
            email: User email
            stripe_customer_id: Stripe customer ID
            name: User name (optional)
            company: User company (optional)

        Returns:
            Created user data or None on failure
        """
        if not self.client:
            logger.warning("Cannot create user profile: Supabase client not available")
            return None

        # Validate required inputs
        if not user_id:
            logger.error("Cannot create user profile: user_id is empty or None")
            return None

        if not email:
            logger.error("Cannot create user profile: email is empty or None")
            return None

        if '@' not in email:
            logger.error(f"Cannot create user profile: invalid email format: {email}")
            return None

        if not stripe_customer_id:
            logger.warning(f"Creating user profile without Stripe customer ID for {email}")

        logger.info(f"Creating user profile for {email} (user_id: {user_id})")

        user_data = {
            'id': user_id,
            'email': email,
            'stripe_customer_id': stripe_customer_id,
            'subscription_status': 'inactive',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }

        if name:
            user_data['name'] = name
            logger.debug(f"Added name to user profile: {name}")

        if company:
            user_data['company'] = company
            logger.debug(f"Added company to user profile: {company}")

        result = self.client.table('users').insert(user_data).execute()

        if not result:
            logger.error(f"Failed to create user profile: No result from insert operation for {email}")
            return None

        if not hasattr(result, 'data') or result.data is None:
            logger.error(f"Failed to create user profile: Result has no data attribute for {email}")
            return None

        if len(result.data) == 0:
            logger.error(f"Failed to create user profile: Insert returned empty data for {email}")
            return None

        logger.info(f"Successfully created user profile for {email} (user_id: {user_id})")
        return result.data[0]

    def update_subscription_status(self, user_id: str, status: str,
                                   subscription_id: Optional[str] = None,
                                   period_start: Optional[datetime] = None,
                                   period_end: Optional[datetime] = None) -> bool:
        """
        Update user subscription status

        Args:
            user_id: Supabase user ID
            status: Subscription status (active, inactive, past_due, canceled)
            subscription_id: Stripe subscription ID (optional)
            period_start: Billing period start (optional)
            period_end: Billing period end (optional)

        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.warning("Cannot update subscription status: Supabase client not available")
            return False

        # Validate inputs
        if not user_id:
            logger.error("Cannot update subscription status: user_id is empty or None")
            return False

        if not status:
            logger.error("Cannot update subscription status: status is empty or None")
            return False

        valid_statuses = ['active', 'inactive', 'past_due', 'canceled', 'trialing', 'unpaid']
        if status not in valid_statuses:
            logger.error(f"Cannot update subscription status: invalid status '{status}'. Must be one of {valid_statuses}")
            return False

        logger.info(f"Updating subscription status for user {user_id} to {status}")

        update_data = {
            'subscription_status': status,
            'updated_at': datetime.utcnow().isoformat()
        }

        if subscription_id:
            if not subscription_id.startswith('sub_'):
                logger.warning(f"Subscription ID has unexpected format: {subscription_id} (expected 'sub_' prefix)")
            update_data['stripe_subscription_id'] = subscription_id
            logger.debug(f"Including subscription_id in update: {subscription_id}")

        if period_start:
            if not isinstance(period_start, datetime):
                logger.error(f"period_start must be datetime object, got {type(period_start)}")
                return False
            update_data['current_period_start'] = period_start.isoformat()
            logger.debug(f"Including period_start in update: {period_start}")

        if period_end:
            if not isinstance(period_end, datetime):
                logger.error(f"period_end must be datetime object, got {type(period_end)}")
                return False
            update_data['current_period_end'] = period_end.isoformat()
            logger.debug(f"Including period_end in update: {period_end}")

        result = self.client.table('users').update(update_data).eq('id', user_id).execute()

        if not result:
            logger.error(f"Failed to update subscription status: No result from update operation for user {user_id}")
            return False

        logger.info(f"Successfully updated subscription status for user {user_id} to {status}")
        return True

    # ========================================================================
    # JOB TRACKING
    # ========================================================================

    def create_job(self, user_id: str, job_type: str, input_s3_path: str,
                   output_s3_path: Optional[str] = None, metadata: Optional[Dict] = None) -> Optional[str]:
        """
        Create a new processing job

        Args:
            user_id: Supabase user ID
            job_type: Type of job (csv_to_parquet, aggregate, clean, etc.)
            input_s3_path: S3 path to input file
            output_s3_path: S3 path for output file (optional)
            metadata: Additional job metadata (optional)

        Returns:
            Job ID (UUID) or None on failure
        """
        if not self.client:
            return None

        try:
            job_data = {
                'user_id': user_id,
                'job_type': job_type,
                'status': 'queued',
                'input_s3_path': input_s3_path,
                'created_at': datetime.utcnow().isoformat()
            }

            if output_s3_path:
                job_data['output_s3_path'] = output_s3_path
            if metadata:
                job_data['metadata'] = metadata

            result = self.client.table('processing_jobs').insert(job_data).execute()

            if result.data and len(result.data) > 0:
                job_id = result.data[0]['id']
                logger.info(f"Created job {job_id} for user {user_id}, type: {job_type}")
                return job_id
            return None
        except Exception as e:
            logger.error(f"Error creating job: {str(e)}")
            return None

    def update_job_status(self, job_id: str, status: str, **kwargs) -> bool:
        """
        Update job status and optional fields

        Args:
            job_id: Job ID (UUID)
            status: New status (queued, processing, completed, failed)
            **kwargs: Additional fields to update (modal_call_id, error_message, etc.)

        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            return False

        try:
            update_data = {
                'status': status,
            }

            # Add timestamp based on status
            if status == 'processing':
                update_data['started_at'] = datetime.utcnow().isoformat()
            elif status in ('completed', 'failed'):
                update_data['completed_at'] = datetime.utcnow().isoformat()

            # Add any additional fields
            update_data.update(kwargs)

            result = self.client.table('processing_jobs').update(update_data).eq('id', job_id).execute()

            logger.info(f"Updated job {job_id} status to {status}")
            return True
        except Exception as e:
            logger.error(f"Error updating job status: {str(e)}")
            return False

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job by ID

        Args:
            job_id: Job ID (UUID)

        Returns:
            Job data dict or None if not found
        """
        if not self.client:
            return None

        try:
            result = self.client.table('processing_jobs').select('*').eq('id', job_id).execute()
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting job {job_id}: {str(e)}")
            return None

    def get_user_jobs(self, user_id: str, limit: int = 50, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get jobs for a user

        Args:
            user_id: Supabase user ID
            limit: Maximum number of jobs to return
            status: Filter by status (optional)

        Returns:
            List of job data dicts
        """
        if not self.client:
            return []

        try:
            query = self.client.table('processing_jobs').select('*').eq('user_id', user_id)

            if status:
                query = query.eq('status', status)

            query = query.order('created_at', desc=True).limit(limit)
            result = query.execute()

            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting user jobs: {str(e)}")
            return []

    # ========================================================================
    # USAGE TRACKING
    # ========================================================================

    def log_usage(self, user_id: str, stripe_customer_id: str, hours_used: float,
                  job_id: Optional[str] = None, api_endpoint: Optional[str] = None,
                  session_id: Optional[str] = None) -> bool:
        """
        Log usage to Supabase

        Args:
            user_id: Supabase user ID
            stripe_customer_id: Stripe customer ID
            hours_used: Hours of usage
            job_id: Related job ID (optional)
            api_endpoint: API endpoint used (optional)
            session_id: Session ID (optional)

        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            return False

        try:
            usage_data = {
                'user_id': user_id,
                'stripe_customer_id': stripe_customer_id,
                'hours_used': hours_used,
                'usage_timestamp': datetime.utcnow().isoformat(),
                'created_at': datetime.utcnow().isoformat()
            }

            if job_id:
                usage_data['job_id'] = job_id
            if api_endpoint:
                usage_data['api_endpoint'] = api_endpoint
            if session_id:
                usage_data['session_id'] = session_id

            result = self.client.table('usage_history').insert(usage_data).execute()

            logger.info(f"Logged {hours_used} hours usage for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error logging usage: {str(e)}")
            return False

    def get_user_usage(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get usage history for a user

        Args:
            user_id: Supabase user ID
            limit: Maximum number of records to return

        Returns:
            List of usage records
        """
        if not self.client:
            return []

        try:
            result = self.client.table('usage_history').select('*').eq('user_id', user_id)\
                .order('usage_timestamp', desc=True).limit(limit).execute()

            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting user usage: {str(e)}")
            return []

    # ========================================================================
    # PAYMENT TRACKING
    # ========================================================================

    def log_payment(self, user_id: str, stripe_customer_id: str, amount_paid: float,
                   stripe_session_id: Optional[str] = None, stripe_payment_intent: Optional[str] = None,
                   stripe_invoice_id: Optional[str] = None, currency: str = 'usd') -> bool:
        """
        Log payment to Supabase

        Args:
            user_id: Supabase user ID
            stripe_customer_id: Stripe customer ID
            amount_paid: Amount paid in dollars
            stripe_session_id: Stripe checkout session ID (optional)
            stripe_payment_intent: Stripe payment intent ID (optional)
            stripe_invoice_id: Stripe invoice ID (optional)
            currency: Currency code (default: usd)

        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            return False

        try:
            payment_data = {
                'user_id': user_id,
                'stripe_customer_id': stripe_customer_id,
                'amount_paid': amount_paid,
                'currency': currency,
                'payment_status': 'succeeded',
                'payment_date': datetime.utcnow().isoformat(),
                'created_at': datetime.utcnow().isoformat()
            }

            if stripe_session_id:
                payment_data['stripe_session_id'] = stripe_session_id
            if stripe_payment_intent:
                payment_data['stripe_payment_intent'] = stripe_payment_intent
            if stripe_invoice_id:
                payment_data['stripe_invoice_id'] = stripe_invoice_id

            result = self.client.table('payment_history').insert(payment_data).execute()

            logger.info(f"Logged payment of ${amount_paid} for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error logging payment: {str(e)}")
            return False

    def get_user_payments(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get payment history for a user

        Args:
            user_id: Supabase user ID
            limit: Maximum number of records to return

        Returns:
            List of payment records
        """
        if not self.client:
            return []

        try:
            result = self.client.table('payment_history').select('*').eq('user_id', user_id)\
                .order('payment_date', desc=True).limit(limit).execute()

            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error getting user payments: {str(e)}")
            return []


# Global instance
supabase_client = SupabaseClient()
