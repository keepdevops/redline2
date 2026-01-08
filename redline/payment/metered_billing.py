#!/usr/bin/env python3
"""
Stripe Metered Billing Manager for REDLINE
Reports usage to Stripe for metered billing subscriptions
"""

import stripe
import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from redline.database.supabase_client import supabase_client

logger = logging.getLogger(__name__)


class MeteredBillingManager:
    """Reports usage to Stripe for metered billing"""

    def __init__(self):
        """Initialize Stripe API with secret key"""
        self.stripe_secret_key = os.environ.get('STRIPE_SECRET_KEY')
        self.price_id = os.environ.get('STRIPE_PRICE_ID_METERED')

        if not self.stripe_secret_key:
            logger.warning("STRIPE_SECRET_KEY not configured")
        else:
            stripe.api_key = self.stripe_secret_key

        if not self.price_id:
            logger.warning("STRIPE_PRICE_ID_METERED not configured")

    def is_available(self) -> bool:
        """Check if metered billing is properly configured"""
        return bool(self.stripe_secret_key and self.price_id)

    # ========================================================================
    # USAGE REPORTING
    # ========================================================================

    def report_usage(self, stripe_customer_id: str, hours_used: float,
                    user_id: Optional[str] = None,
                    idempotency_key: Optional[str] = None) -> bool:
        """
        Report usage to Stripe metered billing

        Args:
            stripe_customer_id: Stripe customer ID
            hours_used: Number of hours to report (can be fractional)
            user_id: Optional Supabase user ID for logging
            idempotency_key: Optional idempotency key to prevent duplicate charges

        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            logger.error("Cannot report usage: Metered billing not configured (missing STRIPE_SECRET_KEY or STRIPE_PRICE_ID_METERED)")
            return False

        # Validate inputs
        if not stripe_customer_id:
            logger.error("Cannot report usage: stripe_customer_id is empty or None")
            return False

        if not isinstance(stripe_customer_id, str):
            logger.error(f"Cannot report usage: stripe_customer_id must be string, got {type(stripe_customer_id)}")
            return False

        if not stripe_customer_id.startswith('cus_'):
            logger.error(f"Cannot report usage: invalid Stripe customer ID format: {stripe_customer_id} (expected 'cus_' prefix)")
            return False

        if not isinstance(hours_used, (int, float)):
            logger.error(f"Cannot report usage: hours_used must be numeric, got {type(hours_used)}")
            return False

        if hours_used <= 0:
            logger.error(f"Cannot report usage: invalid usage amount: {hours_used} hours (must be positive)")
            return False

        if hours_used > 1000:
            logger.warning(f"Unusually large usage amount: {hours_used} hours for customer {stripe_customer_id}")

        logger.info(f"Reporting usage for customer {stripe_customer_id}: {hours_used} hours")

        # Get active subscription for customer
        logger.debug(f"Fetching active subscriptions for customer {stripe_customer_id}")
        subscriptions = stripe.Subscription.list(
            customer=stripe_customer_id,
            limit=1,
            status='active'
        )

        if not subscriptions:
            logger.error(f"Stripe API returned no result for customer {stripe_customer_id}")
            return False

        if not hasattr(subscriptions, 'data') or subscriptions.data is None:
            logger.error(f"Stripe API response has no data attribute for customer {stripe_customer_id}")
            return False

        if len(subscriptions.data) == 0:
            logger.warning(f"No active subscription found for customer {stripe_customer_id}")
            return False

        subscription = subscriptions.data[0]
        logger.debug(f"Found active subscription: {subscription['id']}")

        # Find the metered subscription item
        if 'items' not in subscription:
            logger.error(f"Subscription {subscription['id']} has no items attribute")
            return False

        if 'data' not in subscription['items']:
            logger.error(f"Subscription {subscription['id']} items have no data attribute")
            return False

        metered_item = None
        for item in subscription['items']['data']:
            if 'price' not in item or 'id' not in item['price']:
                logger.warning(f"Subscription item missing price information, skipping")
                continue

            if item['price']['id'] == self.price_id:
                metered_item = item
                logger.debug(f"Found metered item: {item['id']}")
                break

        if not metered_item:
            logger.error(f"Metered price {self.price_id} not found in subscription {subscription['id']}")
            return False

        subscription_item_id = metered_item['id']

        # Convert hours to usage units (multiply by 100 for cents precision)
        # Example: 0.5 hours = 50 units, 1.25 hours = 125 units
        usage_quantity = int(hours_used * 100)
        logger.debug(f"Converting {hours_used} hours to {usage_quantity} usage units")

        # Create usage record
        extra_params = {
            'timestamp': int(datetime.utcnow().timestamp()),
            'action': 'increment'
        }

        if idempotency_key:
            if not isinstance(idempotency_key, str):
                logger.error(f"idempotency_key must be string, got {type(idempotency_key)}")
                return False
            extra_params['idempotency_key'] = idempotency_key
            logger.debug(f"Using idempotency key: {idempotency_key}")

        logger.info(f"Creating usage record: {usage_quantity} units for subscription item {subscription_item_id}")
        usage_record = stripe.SubscriptionItem.create_usage_record(
            subscription_item_id,
            quantity=usage_quantity,
            **extra_params
        )

        logger.info(
            f"Successfully reported {hours_used} hours ({usage_quantity} units) "
            f"for customer {stripe_customer_id}"
        )

        # Log usage to Supabase if user_id provided
        if user_id:
            if not supabase_client.is_available():
                logger.warning("Supabase not available, skipping usage logging to database")
            else:
                logger.debug(f"Logging usage to Supabase for user {user_id}")
                success = supabase_client.log_usage(
                    user_id=user_id,
                    stripe_customer_id=stripe_customer_id,
                    hours_used=hours_used
                )
                if not success:
                    logger.warning(f"Failed to log usage to Supabase for user {user_id}")
                    # Don't fail the whole operation if Supabase logging fails

        return True

    def report_usage_batch(self, usage_records: list) -> Dict[str, Any]:
        """
        Report multiple usage records in batch

        Args:
            usage_records: List of dicts with keys:
                - stripe_customer_id: str
                - hours_used: float
                - user_id: Optional[str]
                - idempotency_key: Optional[str]

        Returns:
            Dict with success count, failure count, and errors
        """
        results = {
            'success_count': 0,
            'failure_count': 0,
            'errors': []
        }

        for record in usage_records:
            stripe_customer_id = record.get('stripe_customer_id')
            hours_used = record.get('hours_used')
            user_id = record.get('user_id')
            idempotency_key = record.get('idempotency_key')

            if not stripe_customer_id or not hours_used:
                results['failure_count'] += 1
                results['errors'].append({
                    'record': record,
                    'error': 'Missing required fields'
                })
                continue

            success = self.report_usage(
                stripe_customer_id,
                hours_used,
                user_id,
                idempotency_key
            )

            if success:
                results['success_count'] += 1
            else:
                results['failure_count'] += 1
                results['errors'].append({
                    'stripe_customer_id': stripe_customer_id,
                    'error': 'Failed to report usage'
                })

        logger.info(
            f"Batch usage reporting: {results['success_count']} succeeded, "
            f"{results['failure_count']} failed"
        )

        return results

    # ========================================================================
    # USAGE RETRIEVAL
    # ========================================================================

    def get_current_usage(self, stripe_customer_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current billing period usage for a customer

        Args:
            stripe_customer_id: Stripe customer ID

        Returns:
            Dict with usage info or None if not found
        """
        if not self.is_available():
            logger.error("Metered billing not configured")
            return None

        try:
            # Get active subscription
            subscriptions = stripe.Subscription.list(
                customer=stripe_customer_id,
                limit=1,
                status='active'
            )

            if not subscriptions.data:
                logger.warning(f"No active subscription for customer {stripe_customer_id}")
                return None

            subscription = subscriptions.data[0]

            # Find metered item
            metered_item = None
            for item in subscription['items']['data']:
                if item['price']['id'] == self.price_id:
                    metered_item = item
                    break

            if not metered_item:
                logger.warning(f"Metered price not found in subscription")
                return None

            # Get usage records for current period
            current_period_start = subscription['current_period_start']
            current_period_end = subscription['current_period_end']

            usage_records = stripe.SubscriptionItem.list_usage_record_summaries(
                metered_item['id'],
                limit=100
            )

            total_usage_units = sum(record['total_usage'] for record in usage_records.data)
            total_hours = total_usage_units / 100.0  # Convert units back to hours

            return {
                'stripe_customer_id': stripe_customer_id,
                'subscription_id': subscription['id'],
                'current_period_start': current_period_start,
                'current_period_end': current_period_end,
                'total_usage_units': total_usage_units,
                'total_hours': total_hours,
                'usage_records_count': len(usage_records.data)
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error getting usage: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting usage: {str(e)}")
            return None

    # ========================================================================
    # SUBSCRIPTION MANAGEMENT
    # ========================================================================

    def get_subscription_info(self, stripe_customer_id: str) -> Optional[Dict[str, Any]]:
        """
        Get subscription information for a customer

        Args:
            stripe_customer_id: Stripe customer ID

        Returns:
            Dict with subscription info or None if not found
        """
        if not self.is_available():
            logger.error("Metered billing not configured")
            return None

        try:
            # Get active subscription
            subscriptions = stripe.Subscription.list(
                customer=stripe_customer_id,
                limit=1,
                status='active'
            )

            if not subscriptions.data:
                return None

            subscription = subscriptions.data[0]

            return {
                'subscription_id': subscription['id'],
                'status': subscription['status'],
                'current_period_start': subscription['current_period_start'],
                'current_period_end': subscription['current_period_end'],
                'cancel_at_period_end': subscription['cancel_at_period_end'],
                'created': subscription['created'],
                'items': [
                    {
                        'id': item['id'],
                        'price_id': item['price']['id'],
                        'product_id': item['price']['product']
                    }
                    for item in subscription['items']['data']
                ]
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error getting subscription: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting subscription: {str(e)}")
            return None

    def cancel_subscription(self, stripe_customer_id: str,
                           immediately: bool = False) -> bool:
        """
        Cancel a customer's subscription

        Args:
            stripe_customer_id: Stripe customer ID
            immediately: If True, cancel immediately. If False, cancel at period end.

        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            logger.error("Metered billing not configured")
            return False

        try:
            # Get active subscription
            subscriptions = stripe.Subscription.list(
                customer=stripe_customer_id,
                limit=1,
                status='active'
            )

            if not subscriptions.data:
                logger.warning(f"No active subscription to cancel for {stripe_customer_id}")
                return False

            subscription = subscriptions.data[0]

            if immediately:
                # Cancel immediately
                stripe.Subscription.delete(subscription['id'])
                logger.info(f"Immediately canceled subscription {subscription['id']}")
            else:
                # Cancel at period end
                stripe.Subscription.modify(
                    subscription['id'],
                    cancel_at_period_end=True
                )
                logger.info(f"Scheduled cancellation at period end for {subscription['id']}")

            return True

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error canceling subscription: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error canceling subscription: {str(e)}")
            return False


# Global instance
metered_billing_manager = MeteredBillingManager()
