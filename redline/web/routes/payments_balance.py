#!/usr/bin/env python3
"""
Payment balance and history routes for VarioSync Web GUI
Handles Stripe subscription status and usage history
"""

from flask import Blueprint, request, jsonify, current_app, g
import logging
import os

payments_balance_bp = Blueprint('payments_balance', __name__)
logger = logging.getLogger(__name__)

# Rate limit: 1000 per hour (balance is polled frequently)
@payments_balance_bp.route('/balance', methods=['GET'])
def get_balance():
    """Get Stripe subscription status and usage for authenticated user"""
    # Get user info from g (set by auth middleware)
    user_id = getattr(g, 'user_id', None)
    email = getattr(g, 'email', None)
    stripe_customer_id = getattr(g, 'stripe_customer_id', None)
    subscription_status = getattr(g, 'subscription_status', 'inactive')

    # Validate authentication
    if not user_id:
        logger.warning("Balance request without authenticated user")
        return jsonify({
            'error': 'Authentication required',
            'success': False,
            'subscription_status': 'inactive'
        }), 401

    if not isinstance(user_id, str):
        logger.error(f"Balance request with invalid user_id type: {type(user_id)}")
        return jsonify({
            'error': 'Invalid authentication data',
            'success': False
        }), 401

    logger.debug(f"Processing balance request for user_id: {user_id}")

    # Import and validate Stripe
    try:
        import stripe
    except ImportError:
        logger.error("Balance request received but Stripe library not installed")
        return jsonify({
            'error': 'Payment system not available',
            'success': False
        }), 503

    # Set Stripe API key
    stripe_secret_key = os.environ.get('STRIPE_SECRET_KEY')
    if not stripe_secret_key:
        logger.warning(f"Balance request for {user_id} but STRIPE_SECRET_KEY not configured")
        # Still return basic info without Stripe data
        return jsonify({
            'success': True,
            'user_id': user_id,
            'email': email,
            'subscription_status': subscription_status,
            'stripe_customer_id': stripe_customer_id,
            'warning': 'Stripe not configured'
        }), 200

    stripe.api_key = stripe_secret_key

    # Build base result
    result = {
        'success': True,
        'user_id': user_id,
        'email': email,
        'subscription_status': subscription_status,
        'stripe_customer_id': stripe_customer_id
    }

    # Get subscription details from Stripe
    if stripe_customer_id:
        if not isinstance(stripe_customer_id, str):
            logger.error(f"stripe_customer_id has invalid type: {type(stripe_customer_id)}")
        elif not stripe_customer_id.startswith('cus_'):
            logger.warning(f"stripe_customer_id has unexpected format: {stripe_customer_id}")
        else:
            logger.debug(f"Fetching Stripe subscription data for customer: {stripe_customer_id}")

            # Note: Stripe API calls can raise specific exceptions - legitimate exception handling
            try:
                subscriptions = stripe.Subscription.list(
                    customer=stripe_customer_id,
                    limit=10
                )

                if subscriptions and hasattr(subscriptions, 'data') and subscriptions.data:
                    logger.debug(f"Found {len(subscriptions.data)} subscriptions for customer {stripe_customer_id}")

                    # Get the most recent active subscription
                    active_sub = None
                    for sub in subscriptions.data:
                        if hasattr(sub, 'status') and sub.status in ['active', 'trialing']:
                            active_sub = sub
                            logger.debug(f"Found active subscription: {sub.id} (status: {sub.status})")
                            break

                    if active_sub:
                        result['subscription'] = {
                            'id': active_sub.id,
                            'status': active_sub.status,
                            'current_period_start': active_sub.current_period_start,
                            'current_period_end': active_sub.current_period_end,
                            'cancel_at_period_end': active_sub.cancel_at_period_end
                        }

                        # Get usage for metered subscription items
                        if hasattr(active_sub, '__getitem__') and 'items' in active_sub:
                            for item in active_sub['items'].data:
                                if (hasattr(item, 'price') and hasattr(item.price, 'recurring') and
                                    item.price.recurring and
                                    hasattr(item.price.recurring, 'usage_type') and
                                    item.price.recurring.usage_type == 'metered'):

                                    logger.debug(f"Fetching usage records for metered item: {item.id}")
                                    usage_records = stripe.SubscriptionItem.list_usage_record_summaries(
                                        item.id,
                                        limit=100
                                    )

                                    if usage_records and hasattr(usage_records, 'data'):
                                        total_usage = sum(getattr(record, 'total_usage', 0) for record in usage_records.data)
                                        result['usage'] = {
                                            'total_hours': total_usage / 100,  # Convert units to hours (units = hours * 100)
                                            'period_start': active_sub.current_period_start,
                                            'period_end': active_sub.current_period_end
                                        }
                                        logger.debug(f"Total usage: {total_usage} units ({total_usage/100} hours)")
                    else:
                        logger.debug(f"No active subscription found for customer {stripe_customer_id}")

                # Get upcoming invoice to show estimated cost
                try:
                    upcoming_invoice = stripe.Invoice.upcoming(customer=stripe_customer_id)
                    if upcoming_invoice:
                        result['upcoming_invoice'] = {
                            'amount_due': upcoming_invoice.amount_due / 100,  # Convert cents to dollars
                            'currency': upcoming_invoice.currency,
                            'period_start': upcoming_invoice.period_start,
                            'period_end': upcoming_invoice.period_end
                        }
                        logger.debug(f"Upcoming invoice: ${upcoming_invoice.amount_due / 100}")
                except stripe.error.InvalidRequestError as e:
                    # No upcoming invoice (new customer or no active subscription)
                    logger.debug(f"No upcoming invoice for customer {stripe_customer_id}: {str(e)}")

            except stripe.error.InvalidRequestError as e:
                logger.error(f"Stripe invalid request getting subscription for {stripe_customer_id}: {str(e)}")
                result['stripe_error'] = str(e)
            except stripe.error.AuthenticationError as e:
                logger.error(f"Stripe authentication error for {stripe_customer_id}: {str(e)}")
                result['stripe_error'] = 'Authentication failed'
            except stripe.error.APIConnectionError as e:
                logger.error(f"Stripe API connection error for {stripe_customer_id}: {str(e)}")
                result['stripe_error'] = 'Service temporarily unavailable'
            except stripe.error.StripeError as e:
                logger.error(f"Stripe API error for {stripe_customer_id}: {str(e)}")
                result['stripe_error'] = str(e)

    # Get usage history from Supabase
    from redline.database.supabase_client import supabase_client

    if supabase_client.is_available():
        logger.debug(f"Fetching usage history from Supabase for user: {user_id}")
        usage_history = supabase_client.get_usage_history(user_id, limit=100)

        if usage_history:
            if not isinstance(usage_history, list):
                logger.warning(f"Usage history returned unexpected type: {type(usage_history)}")
            else:
                result['usage_history'] = usage_history
                # Calculate totals
                total_hours = sum(record.get('processing_hours', 0) for record in usage_history if isinstance(record, dict))
                result['total_usage_hours'] = total_hours
                logger.debug(f"Found {len(usage_history)} usage records, total: {total_hours} hours")
    else:
        logger.debug("Supabase client not available, skipping usage history")

    logger.info(f"Successfully processed balance request for user: {user_id}")
    return jsonify(result), 200

@payments_balance_bp.route('/history', methods=['GET'])
def get_history():
    """Get usage and payment history from Stripe and Supabase"""
    try:
        # Get user info from g (set by auth middleware)
        user_id = getattr(g, 'user_id', None)
        stripe_customer_id = getattr(g, 'stripe_customer_id', None)
        history_type = request.args.get('type', 'all')  # 'all', 'usage', 'payment'

        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401

        result = {
            'usage_history': [],
            'payment_history': [],
            'invoices': []
        }

        # Get usage history from Supabase
        if history_type in ('all', 'usage'):
            try:
                from redline.database.supabase_client import supabase_client
                if supabase_client.is_available():
                    usage_history = supabase_client.get_usage_history(user_id, limit=100)
                    result['usage_history'] = usage_history

                    # Calculate totals
                    total_hours = sum(record.get('processing_hours', 0) for record in usage_history)
                    result['total_hours_used'] = total_hours
            except Exception as e:
                logger.warning(f"Failed to get usage history: {str(e)}")

        # Get payment history from Stripe
        if history_type in ('all', 'payment') and stripe_customer_id:
            try:
                import stripe
                stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

                # Get invoices
                invoices = stripe.Invoice.list(
                    customer=stripe_customer_id,
                    limit=50
                )

                result['invoices'] = [{
                    'id': inv.id,
                    'amount_paid': inv.amount_paid / 100,  # Convert cents to dollars
                    'amount_due': inv.amount_due / 100,
                    'currency': inv.currency,
                    'status': inv.status,
                    'created': inv.created,
                    'period_start': inv.period_start,
                    'period_end': inv.period_end,
                    'invoice_pdf': inv.invoice_pdf
                } for inv in invoices.data]

                # Get charges (payments)
                charges = stripe.Charge.list(
                    customer=stripe_customer_id,
                    limit=50
                )

                result['payment_history'] = [{
                    'id': charge.id,
                    'amount': charge.amount / 100,
                    'currency': charge.currency,
                    'status': charge.status,
                    'created': charge.created,
                    'description': charge.description,
                    'receipt_url': charge.receipt_url
                } for charge in charges.data]

                # Calculate payment totals
                total_paid = sum(inv['amount_paid'] for inv in result['invoices'])
                result['total_amount_paid'] = total_paid

            except ImportError:
                logger.error("Stripe library not installed")
            except Exception as e:
                logger.warning(f"Failed to get payment history from Stripe: {str(e)}")

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

