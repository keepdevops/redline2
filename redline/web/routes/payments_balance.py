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
        # Pre-validation with if-else
        if not isinstance(stripe_customer_id, str):
            logger.error(f"stripe_customer_id has invalid type for user {user_id}: {type(stripe_customer_id)}")
        elif not stripe_customer_id.startswith('cus_'):
            logger.warning(f"stripe_customer_id has unexpected format for user {user_id}: {stripe_customer_id}")
        else:
            logger.debug(f"Fetching Stripe subscription data for customer: {stripe_customer_id}")

            # Note: Stripe API calls can raise specific exceptions - legitimate exception handling
            try:
                subscriptions = stripe.Subscription.list(
                    customer=stripe_customer_id,
                    limit=10
                )

                # Validate subscription response
                if not subscriptions:
                    logger.warning(f"Stripe returned no subscriptions object for customer {stripe_customer_id}")
                elif not hasattr(subscriptions, 'data'):
                    logger.error(f"Stripe subscriptions missing 'data' attribute for customer {stripe_customer_id}")
                elif not subscriptions.data:
                    logger.debug(f"No subscriptions found for customer {stripe_customer_id}")
                else:
                    logger.debug(f"Found {len(subscriptions.data)} subscriptions for customer {stripe_customer_id}")

                    # Get the most recent active subscription
                    active_sub = None
                    for sub in subscriptions.data:
                        if hasattr(sub, 'status') and sub.status in ['active', 'trialing']:
                            active_sub = sub
                            logger.debug(f"Found active subscription: {sub.id} (status: {sub.status})")
                            break

                    if active_sub:
                        # Validate required fields before using
                        if not hasattr(active_sub, 'id'):
                            logger.error(f"Active subscription missing 'id' field for customer {stripe_customer_id}")
                        elif not hasattr(active_sub, 'status'):
                            logger.error(f"Active subscription missing 'status' field for customer {stripe_customer_id}")
                        else:
                            result['subscription'] = {
                                'id': active_sub.id,
                                'status': active_sub.status,
                                'current_period_start': getattr(active_sub, 'current_period_start', None),
                                'current_period_end': getattr(active_sub, 'current_period_end', None),
                                'cancel_at_period_end': getattr(active_sub, 'cancel_at_period_end', False)
                            }

                            # Get usage for metered subscription items
                            if hasattr(active_sub, '__getitem__') and 'items' in active_sub:
                                if not hasattr(active_sub['items'], 'data'):
                                    logger.warning(f"Subscription items missing 'data' attribute for customer {stripe_customer_id}")
                                else:
                                    for item in active_sub['items'].data:
                                        if (hasattr(item, 'price') and hasattr(item.price, 'recurring') and
                                            item.price.recurring and
                                            hasattr(item.price.recurring, 'usage_type') and
                                            item.price.recurring.usage_type == 'metered'):

                                            if not hasattr(item, 'id'):
                                                logger.warning(f"Metered item missing 'id' field for customer {stripe_customer_id}")
                                                continue

                                            logger.debug(f"Fetching usage records for metered item: {item.id}")

                                            try:
                                                usage_records = stripe.SubscriptionItem.list_usage_record_summaries(
                                                    item.id,
                                                    limit=100
                                                )

                                                if not usage_records:
                                                    logger.debug(f"No usage records returned for item {item.id}")
                                                elif not hasattr(usage_records, 'data'):
                                                    logger.warning(f"Usage records missing 'data' attribute for item {item.id}")
                                                else:
                                                    total_usage = sum(getattr(record, 'total_usage', 0) for record in usage_records.data)
                                                    result['usage'] = {
                                                        'total_hours': total_usage / 100,  # Convert units to hours (units = hours * 100)
                                                        'period_start': active_sub.current_period_start,
                                                        'period_end': active_sub.current_period_end
                                                    }
                                                    logger.debug(f"Total usage: {total_usage} units ({total_usage/100} hours)")
                                            except stripe.error.InvalidRequestError as e:
                                                logger.warning(f"Invalid request fetching usage records for item {item.id}: {str(e)}")
                                            except stripe.error.StripeError as e:
                                                logger.warning(f"Stripe error fetching usage records for item {item.id}: {str(e)}")
                    else:
                        logger.debug(f"No active subscription found for customer {stripe_customer_id}")

                # Get upcoming invoice to show estimated cost
                logger.debug(f"Fetching upcoming invoice for customer {stripe_customer_id}")

                try:
                    upcoming_invoice = stripe.Invoice.upcoming(customer=stripe_customer_id)

                    if not upcoming_invoice:
                        logger.debug(f"No upcoming invoice returned for customer {stripe_customer_id}")
                    elif not hasattr(upcoming_invoice, 'amount_due'):
                        logger.warning(f"Upcoming invoice missing 'amount_due' for customer {stripe_customer_id}")
                    else:
                        result['upcoming_invoice'] = {
                            'amount_due': upcoming_invoice.amount_due / 100,  # Convert cents to dollars
                            'currency': getattr(upcoming_invoice, 'currency', 'usd'),
                            'period_start': getattr(upcoming_invoice, 'period_start', None),
                            'period_end': getattr(upcoming_invoice, 'period_end', None)
                        }
                        logger.debug(f"Upcoming invoice: ${upcoming_invoice.amount_due / 100}")
                except stripe.error.InvalidRequestError as e:
                    # No upcoming invoice (new customer or no active subscription) - this is expected
                    logger.debug(f"No upcoming invoice for customer {stripe_customer_id}: {str(e)}")
                except stripe.error.StripeError as e:
                    logger.warning(f"Stripe error fetching upcoming invoice for {stripe_customer_id}: {str(e)}")

            except stripe.error.InvalidRequestError as e:
                logger.error(f"Stripe invalid request getting subscription for {stripe_customer_id} (user {user_id}): {str(e)}")
                result['stripe_error'] = str(e)
            except stripe.error.AuthenticationError as e:
                logger.error(f"Stripe authentication error for {stripe_customer_id} (user {user_id}): {str(e)}")
                result['stripe_error'] = 'Authentication failed'
            except stripe.error.APIConnectionError as e:
                logger.error(f"Stripe API connection error for {stripe_customer_id} (user {user_id}): {str(e)}")
                result['stripe_error'] = 'Service temporarily unavailable'
            except stripe.error.RateLimitError as e:
                logger.error(f"Stripe rate limit error for {stripe_customer_id} (user {user_id}): {str(e)}")
                result['stripe_error'] = 'Rate limit reached, please try again later'
            except stripe.error.StripeError as e:
                logger.error(f"Stripe API error for {stripe_customer_id} (user {user_id}): {type(e).__name__}: {str(e)}")
                result['stripe_error'] = str(e)
            except Exception as e:
                logger.error(f"Unexpected error fetching subscription for {stripe_customer_id} (user {user_id}): {type(e).__name__}: {str(e)}")
                result['stripe_error'] = 'Unexpected error occurred'

    # Get usage history from Supabase
    # Pre-validation with if-else
    try:
        from redline.database.supabase_client import supabase_client
    except ImportError as e:
        logger.warning(f"Failed to import supabase_client for user {user_id}: {str(e)}")
        supabase_client = None

    if supabase_client and supabase_client.is_available():
        logger.debug(f"Fetching usage history from Supabase for user: {user_id}")

        try:
            usage_history = supabase_client.get_usage_history(user_id, limit=100)

            if not usage_history:
                logger.debug(f"No usage history returned for user: {user_id}")
            elif not isinstance(usage_history, list):
                logger.warning(f"Usage history returned unexpected type for user {user_id}: {type(usage_history)}")
            else:
                result['usage_history'] = usage_history
                # Calculate totals
                total_hours = sum(record.get('processing_hours', 0) for record in usage_history if isinstance(record, dict))
                result['total_usage_hours'] = total_hours
                logger.debug(f"Found {len(usage_history)} usage records for user {user_id}, total: {total_hours} hours")
        except AttributeError as e:
            logger.error(f"AttributeError fetching usage history for user {user_id}: {str(e)}")
        except TypeError as e:
            logger.error(f"TypeError fetching usage history for user {user_id}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error fetching usage history for user {user_id}: {type(e).__name__}: {str(e)}")
    else:
        logger.debug(f"Supabase client not available for user {user_id}, skipping usage history")

    logger.info(f"Successfully processed balance request for user: {user_id}")
    return jsonify(result), 200

@payments_balance_bp.route('/history', methods=['GET'])
def get_history():
    """Get usage and payment history from Stripe and Supabase"""
    # Get user info from g (set by auth middleware)
    user_id = getattr(g, 'user_id', None)
    stripe_customer_id = getattr(g, 'stripe_customer_id', None)
    history_type = request.args.get('type', 'all')  # 'all', 'usage', 'payment'

    # Pre-validation with if-else
    if not user_id:
        logger.warning("History request without authenticated user")
        return jsonify({'error': 'Authentication required', 'code': 'NOT_AUTHENTICATED'}), 401

    if not isinstance(user_id, str):
        logger.error(f"History request with invalid user_id type: {type(user_id)}")
        return jsonify({'error': 'Invalid authentication data', 'code': 'INVALID_USER_ID'}), 401

    if not isinstance(history_type, str):
        logger.error(f"History request with invalid type parameter: {type(history_type)}")
        return jsonify({'error': 'Invalid request parameters', 'code': 'INVALID_TYPE'}), 400

    if history_type not in ('all', 'usage', 'payment'):
        logger.warning(f"History request with invalid type value for user {user_id}: {history_type}")
        return jsonify({'error': 'Type must be "all", "usage", or "payment"', 'code': 'INVALID_TYPE_VALUE'}), 400

    logger.debug(f"Processing history request for user {user_id}, type: {history_type}")

    result = {
        'success': True,
        'user_id': user_id,
        'usage_history': [],
        'payment_history': [],
        'invoices': []
    }

    # Get usage history from Supabase
    if history_type in ('all', 'usage'):
        try:
            from redline.database.supabase_client import supabase_client
        except ImportError as e:
            logger.warning(f"Failed to import supabase_client for user {user_id}: {str(e)}")
            result['warnings'] = result.get('warnings', [])
            result['warnings'].append('Usage history service not available')
            supabase_client = None

        if supabase_client and supabase_client.is_available():
            logger.debug(f"Fetching usage history from Supabase for user {user_id}")

            try:
                usage_history = supabase_client.get_usage_history(user_id, limit=100)

                if not usage_history:
                    logger.debug(f"No usage history returned for user {user_id}")
                    result['usage_history'] = []
                elif not isinstance(usage_history, list):
                    logger.warning(f"Usage history returned unexpected type for user {user_id}: {type(usage_history)}")
                    result['usage_history'] = []
                else:
                    result['usage_history'] = usage_history
                    # Calculate totals - validate each record is a dict
                    total_hours = sum(
                        record.get('processing_hours', 0)
                        for record in usage_history
                        if isinstance(record, dict)
                    )
                    result['total_hours_used'] = total_hours
                    logger.debug(f"Found {len(usage_history)} usage records for user {user_id}, total: {total_hours} hours")
            except AttributeError as e:
                logger.error(f"AttributeError fetching usage history for user {user_id}: {str(e)}")
                result['warnings'] = result.get('warnings', [])
                result['warnings'].append('Failed to fetch usage history')
            except TypeError as e:
                logger.error(f"TypeError fetching usage history for user {user_id}: {str(e)}")
                result['warnings'] = result.get('warnings', [])
                result['warnings'].append('Failed to fetch usage history')
            except Exception as e:
                logger.error(f"Unexpected error fetching usage history for user {user_id}: {type(e).__name__}: {str(e)}")
                result['warnings'] = result.get('warnings', [])
                result['warnings'].append('Failed to fetch usage history')
        else:
            logger.debug(f"Supabase client not available for user {user_id}, skipping usage history")

    # Get payment history from Stripe
    if history_type in ('all', 'payment'):
        # Pre-validation with if-else
        if not stripe_customer_id:
            logger.debug(f"No Stripe customer ID for user {user_id}, skipping payment history")
        elif not isinstance(stripe_customer_id, str):
            logger.error(f"stripe_customer_id has invalid type for user {user_id}: {type(stripe_customer_id)}")
        elif not stripe_customer_id.startswith('cus_'):
            logger.warning(f"stripe_customer_id has unexpected format for user {user_id}: {stripe_customer_id}")
        else:
            logger.debug(f"Fetching payment history from Stripe for customer {stripe_customer_id}")

            try:
                import stripe
            except ImportError as e:
                logger.error(f"Stripe library not installed for user {user_id}: {str(e)}")
                result['warnings'] = result.get('warnings', [])
                result['warnings'].append('Payment history service not available')
                stripe = None

            if stripe:
                stripe_secret_key = os.environ.get('STRIPE_SECRET_KEY')

                if not stripe_secret_key:
                    logger.warning(f"STRIPE_SECRET_KEY not configured for user {user_id} payment history")
                    result['warnings'] = result.get('warnings', [])
                    result['warnings'].append('Stripe not configured')
                else:
                    stripe.api_key = stripe_secret_key

                    # Get invoices - Note: Stripe API calls require try-except for external service errors
                    try:
                        invoices = stripe.Invoice.list(
                            customer=stripe_customer_id,
                            limit=50
                        )

                        if not invoices:
                            logger.warning(f"No invoices object returned for customer {stripe_customer_id}")
                        elif not hasattr(invoices, 'data'):
                            logger.error(f"Invoices missing 'data' attribute for customer {stripe_customer_id}")
                        else:
                            result['invoices'] = [{
                                'id': getattr(inv, 'id', None),
                                'amount_paid': getattr(inv, 'amount_paid', 0) / 100,  # Convert cents to dollars
                                'amount_due': getattr(inv, 'amount_due', 0) / 100,
                                'currency': getattr(inv, 'currency', 'usd'),
                                'status': getattr(inv, 'status', 'unknown'),
                                'created': getattr(inv, 'created', None),
                                'period_start': getattr(inv, 'period_start', None),
                                'period_end': getattr(inv, 'period_end', None),
                                'invoice_pdf': getattr(inv, 'invoice_pdf', None)
                            } for inv in invoices.data]
                            logger.debug(f"Found {len(invoices.data)} invoices for customer {stripe_customer_id}")
                    except stripe.error.InvalidRequestError as e:
                        logger.error(f"Stripe invalid request fetching invoices for {stripe_customer_id}: {str(e)}")
                        result['warnings'] = result.get('warnings', [])
                        result['warnings'].append('Failed to fetch invoices')
                    except stripe.error.AuthenticationError as e:
                        logger.error(f"Stripe authentication error for {stripe_customer_id}: {str(e)}")
                        result['warnings'] = result.get('warnings', [])
                        result['warnings'].append('Stripe authentication failed')
                    except stripe.error.APIConnectionError as e:
                        logger.error(f"Stripe API connection error for {stripe_customer_id}: {str(e)}")
                        result['warnings'] = result.get('warnings', [])
                        result['warnings'].append('Stripe temporarily unavailable')
                    except stripe.error.StripeError as e:
                        logger.error(f"Stripe error fetching invoices for {stripe_customer_id}: {type(e).__name__}: {str(e)}")
                        result['warnings'] = result.get('warnings', [])
                        result['warnings'].append('Failed to fetch invoices')
                    except Exception as e:
                        logger.error(f"Unexpected error fetching invoices for {stripe_customer_id}: {type(e).__name__}: {str(e)}")
                        result['warnings'] = result.get('warnings', [])
                        result['warnings'].append('Failed to fetch invoices')

                    # Get charges (payments)
                    try:
                        charges = stripe.Charge.list(
                            customer=stripe_customer_id,
                            limit=50
                        )

                        if not charges:
                            logger.warning(f"No charges object returned for customer {stripe_customer_id}")
                        elif not hasattr(charges, 'data'):
                            logger.error(f"Charges missing 'data' attribute for customer {stripe_customer_id}")
                        else:
                            result['payment_history'] = [{
                                'id': getattr(charge, 'id', None),
                                'amount': getattr(charge, 'amount', 0) / 100,
                                'currency': getattr(charge, 'currency', 'usd'),
                                'status': getattr(charge, 'status', 'unknown'),
                                'created': getattr(charge, 'created', None),
                                'description': getattr(charge, 'description', None),
                                'receipt_url': getattr(charge, 'receipt_url', None)
                            } for charge in charges.data]
                            logger.debug(f"Found {len(charges.data)} charges for customer {stripe_customer_id}")
                    except stripe.error.InvalidRequestError as e:
                        logger.error(f"Stripe invalid request fetching charges for {stripe_customer_id}: {str(e)}")
                        result['warnings'] = result.get('warnings', [])
                        result['warnings'].append('Failed to fetch payment history')
                    except stripe.error.AuthenticationError as e:
                        logger.error(f"Stripe authentication error fetching charges for {stripe_customer_id}: {str(e)}")
                        result['warnings'] = result.get('warnings', [])
                        result['warnings'].append('Stripe authentication failed')
                    except stripe.error.APIConnectionError as e:
                        logger.error(f"Stripe API connection error fetching charges for {stripe_customer_id}: {str(e)}")
                        result['warnings'] = result.get('warnings', [])
                        result['warnings'].append('Stripe temporarily unavailable')
                    except stripe.error.StripeError as e:
                        logger.error(f"Stripe error fetching charges for {stripe_customer_id}: {type(e).__name__}: {str(e)}")
                        result['warnings'] = result.get('warnings', [])
                        result['warnings'].append('Failed to fetch payment history')
                    except Exception as e:
                        logger.error(f"Unexpected error fetching charges for {stripe_customer_id}: {type(e).__name__}: {str(e)}")
                        result['warnings'] = result.get('warnings', [])
                        result['warnings'].append('Failed to fetch payment history')

                    # Calculate payment totals - validate invoice structure
                    if result['invoices']:
                        try:
                            total_paid = sum(
                                inv.get('amount_paid', 0)
                                for inv in result['invoices']
                                if isinstance(inv, dict)
                            )
                            result['total_amount_paid'] = total_paid
                            logger.debug(f"Total amount paid for customer {stripe_customer_id}: ${total_paid}")
                        except TypeError as e:
                            logger.warning(f"TypeError calculating payment totals for {stripe_customer_id}: {str(e)}")
                        except KeyError as e:
                            logger.warning(f"KeyError calculating payment totals for {stripe_customer_id}: {str(e)}")
                        except Exception as e:
                            logger.warning(f"Unexpected error calculating payment totals for {stripe_customer_id}: {str(e)}")

    logger.info(f"Successfully processed history request for user {user_id} (type: {history_type})")
    return jsonify(result), 200

