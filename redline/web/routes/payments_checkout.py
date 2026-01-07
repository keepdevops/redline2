#!/usr/bin/env python3
"""
Payment checkout routes for VarioSync Web GUI
Handles Stripe subscription checkout session creation
"""

from flask import Blueprint, request, jsonify, g
import logging
import os

try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    stripe = None

from redline.payment.config import PaymentConfig

payments_checkout_bp = Blueprint('payments_checkout', __name__)
logger = logging.getLogger(__name__)

# Initialize Stripe if available
if STRIPE_AVAILABLE and PaymentConfig.STRIPE_SECRET_KEY:
    stripe.api_key = PaymentConfig.STRIPE_SECRET_KEY

@payments_checkout_bp.route('/create-checkout', methods=['POST'])
def create_checkout():
    """
    DEPRECATED: This endpoint is for the old pay-per-hour model.
    Use /payments/create-subscription-checkout for new subscription-based billing.
    """
    return jsonify({
        'error': 'This endpoint is deprecated',
        'message': 'Please use /payments/create-subscription-checkout for subscription-based billing',
        'redirect': '/payments/subscription'
    }), 410  # 410 Gone

@payments_checkout_bp.route('/create-subscription-checkout', methods=['POST'])
def create_subscription_checkout():
    """Create Stripe checkout session for subscription with metered billing"""
    if not STRIPE_AVAILABLE:
        return jsonify({'error': 'Stripe is not available. Please install stripe package.'}), 503

    if not PaymentConfig.validate():
        return jsonify({'error': 'Payment configuration is invalid. Please set STRIPE_SECRET_KEY and STRIPE_PUBLISHABLE_KEY.'}), 500

    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        # Get metered price ID from environment
        metered_price_id = os.environ.get('STRIPE_PRICE_ID_METERED')
        if not metered_price_id:
            return jsonify({'error': 'Subscription pricing not configured. Please set STRIPE_PRICE_ID_METERED.'}), 500

        # Create Stripe checkout session for subscription
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': metered_price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                customer_email=email,
                success_url=request.host_url.rstrip('/') + '/payments/subscription-success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.host_url.rstrip('/') + '/payments/subscription-cancel',
                metadata={
                    'email': email
                },
                allow_promotion_codes=True,  # Allow discount codes
                billing_address_collection='auto'
            )

            return jsonify({
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id
            }), 200

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            return jsonify({'error': f'Payment processing error: {str(e)}'}), 500

    except Exception as e:
        logger.error(f"Error creating subscription checkout: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

