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
    try:
        # Get user info from g (set by auth middleware)
        user_id = getattr(g, 'user_id', None)
        email = getattr(g, 'email', None)
        stripe_customer_id = getattr(g, 'stripe_customer_id', None)
        subscription_status = getattr(g, 'subscription_status', 'inactive')

        if not user_id:
            return jsonify({
                'error': 'Authentication required',
                'success': False,
                'subscription_status': 'inactive'
            }), 401

        # Import Stripe
        try:
            import stripe
            stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
        except ImportError:
            logger.error("Stripe library not installed")
            return jsonify({
                'error': 'Payment system not available',
                'success': False
            }), 503

        result = {
            'success': True,
            'user_id': user_id,
            'email': email,
            'subscription_status': subscription_status,
            'stripe_customer_id': stripe_customer_id
        }

        # Get subscription details from Stripe
        if stripe_customer_id:
            try:
                # Get customer's subscriptions
                subscriptions = stripe.Subscription.list(
                    customer=stripe_customer_id,
                    limit=10
                )

                if subscriptions.data:
                    # Get the most recent active subscription
                    active_sub = None
                    for sub in subscriptions.data:
                        if sub.status in ['active', 'trialing']:
                            active_sub = sub
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
                        for item in active_sub['items'].data:
                            if item.price.recurring and item.price.recurring.usage_type == 'metered':
                                # Get usage records for this billing period
                                usage_records = stripe.SubscriptionItem.list_usage_record_summaries(
                                    item.id,
                                    limit=100
                                )

                                total_usage = sum(record.total_usage for record in usage_records.data)
                                result['usage'] = {
                                    'total_hours': total_usage / 3600,  # Convert seconds to hours
                                    'period_start': active_sub.current_period_start,
                                    'period_end': active_sub.current_period_end
                                }

                # Get upcoming invoice to show estimated cost
                try:
                    upcoming_invoice = stripe.Invoice.upcoming(customer=stripe_customer_id)
                    result['upcoming_invoice'] = {
                        'amount_due': upcoming_invoice.amount_due / 100,  # Convert cents to dollars
                        'currency': upcoming_invoice.currency,
                        'period_start': upcoming_invoice.period_start,
                        'period_end': upcoming_invoice.period_end
                    }
                except stripe.error.InvalidRequestError:
                    # No upcoming invoice (new customer or no active subscription)
                    pass

            except stripe.error.StripeError as e:
                logger.error(f"Stripe API error: {str(e)}")
                result['stripe_error'] = str(e)

        # Get usage history from Supabase
        try:
            from redline.database.supabase_client import supabase_client
            if supabase_client.is_available():
                usage_history = supabase_client.get_usage_history(user_id, limit=100)
                result['usage_history'] = usage_history

                # Calculate totals
                total_hours = sum(record.get('processing_hours', 0) for record in usage_history)
                result['total_usage_hours'] = total_hours
        except Exception as e:
            logger.warning(f"Failed to get usage history: {str(e)}")

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error getting balance: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

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

