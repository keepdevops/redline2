#!/usr/bin/env python3
"""
Payment tab routes for VarioSync Web GUI
Handles subscription success pages and subscription management
"""

from flask import Blueprint, request, jsonify, render_template, session as flask_session
import logging
import os
import traceback

try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    stripe = None

from redline.payment.config import PaymentConfig

payments_tab_bp = Blueprint('payments_tab', __name__)
logger = logging.getLogger(__name__)

# Initialize Stripe if available
if STRIPE_AVAILABLE and PaymentConfig.STRIPE_SECRET_KEY:
    stripe.api_key = PaymentConfig.STRIPE_SECRET_KEY

@payments_tab_bp.route('/subscription', methods=['GET'])
def subscription_page():
    """Render subscription management page"""
    return render_template('subscription.html')


@payments_tab_bp.route('/success', methods=['GET'])
def payment_success():
    """DEPRECATED: Old pay-per-hour success page"""
    return render_template('payment_success.html',
                         success=False,
                         error='This payment method is deprecated. Please use subscription-based billing.',
                         redirect_url='/payments/subscription'), 410

@payments_tab_bp.route('/subscription-success', methods=['GET'])
def subscription_success():
    """Handle successful subscription signup"""
    try:
        session_id = request.args.get('session_id')

        if not session_id or not STRIPE_AVAILABLE:
            return render_template('subscription_success.html',
                                 success=False,
                                 error='Invalid session'), 400

        # Retrieve checkout session
        try:
            session = stripe.checkout.Session.retrieve(session_id, expand=['subscription'])
        except Exception as stripe_err:
            error_msg = str(stripe_err) if str(stripe_err) else 'Invalid subscription session'
            logger.error(f"Stripe API error: {error_msg}")
            return render_template('subscription_success.html',
                                 success=False,
                                 error=f'Subscription verification error: {error_msg}'), 400

        if session.status == 'complete':
            customer_email = session.get('customer_email') or session.get('customer_details', {}).get('email')
            customer_id = session.get('customer')
            subscription = session.get('subscription')

            logger.info(f"Subscription success: email={customer_email}, customer={customer_id}")

            # Update user in Supabase with Stripe customer ID
            try:
                from redline.database.supabase_client import supabase_client
                if supabase_client.is_available():
                    user = supabase_client.get_user_by_email(customer_email)
                    if user:
                        supabase_client.update_user(user['id'], {
                            'stripe_customer_id': customer_id,
                            'subscription_status': 'active'
                        })
                        logger.info(f"Updated user {customer_email} with subscription")
            except Exception as e:
                logger.error(f"Failed to update user: {str(e)}")

            return render_template('subscription_success.html',
                                 success=True,
                                 email=customer_email,
                                 subscription_id=subscription.id if subscription else None)
        else:
            return render_template('subscription_success.html',
                                 success=False,
                                 error=f'Subscription status: {session.status}'), 400

    except Exception as e:
        error_msg = str(e) if str(e) else 'Unknown error occurred'
        logger.error(f"Error in subscription_success: {error_msg}")
        logger.error(traceback.format_exc())
        return render_template('subscription_success.html',
                             success=False,
                             error=error_msg), 500

@payments_tab_bp.route('/subscription-cancel', methods=['GET'])
def subscription_cancel():
    """Handle subscription cancellation page"""
    return render_template('subscription_cancel.html')

@payments_tab_bp.route('/packages', methods=['GET'])
def get_packages():
    """
    DEPRECATED: Old hour packages endpoint.
    Now using subscription-based pricing with metered billing.
    """
    return jsonify({
        'error': 'Hour packages are deprecated',
        'message': 'VarioSync now uses subscription-based pricing with metered billing',
        'redirect': '/payments/subscription'
    }), 410

# Note: payment_tab route is defined in payments.py as an alias
# to maintain backward compatibility with templates using url_for('payments.payment_tab')
