#!/usr/bin/env python3
"""
Payment checkout routes for VarioSync Web GUI
Handles Stripe checkout session creation
"""

from flask import Blueprint, request, jsonify, g
import logging
import requests

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
    """Create Stripe checkout session for purchasing hours"""
    if not STRIPE_AVAILABLE:
        return jsonify({'error': 'Stripe is not available. Please install stripe package.'}), 503

    validation_result = PaymentConfig.validate()
    if not validation_result:
        # Get more specific error message
        import os
        secret_key = os.environ.get('STRIPE_SECRET_KEY', '')
        publishable_key = os.environ.get('STRIPE_PUBLISHABLE_KEY', '')
        if secret_key and ('your-secret-key' in secret_key.lower() or secret_key.startswith('sk_test_your-')):
            error_msg = 'STRIPE_SECRET_KEY appears to be a placeholder. Please set a real Stripe API key in your .env file.'
        elif publishable_key and ('your-publishable-key' in publishable_key.lower() or publishable_key.startswith('pk_test_your-')):
            error_msg = 'STRIPE_PUBLISHABLE_KEY appears to be a placeholder. Please set a real Stripe API key in your .env file.'
        elif not secret_key or not publishable_key:
            error_msg = 'Payment configuration is invalid. Please set STRIPE_SECRET_KEY and STRIPE_PUBLISHABLE_KEY in your .env file. Get keys from https://dashboard.stripe.com/test/apikeys'
        else:
            error_msg = 'Payment configuration is invalid. Please check your Stripe API keys in .env file.'
        return jsonify({'error': error_msg}), 500

    try:
        data = request.get_json()

        # User ID comes from JWT (set by middleware)
        user_id = g.user_id
        hours = data.get('hours')
        package_id = data.get('package_id')

        # Get package info or calculate price
        if package_id:
            package = PaymentConfig.get_package_info(package_id)
            if not package:
                return jsonify({'error': 'Invalid package ID'}), 400
            hours = package['hours']
            price_cents = int(package['price'] * 100)
        elif hours:
            price_cents = int(PaymentConfig.calculate_price_from_hours(hours) * 100)
        else:
            return jsonify({'error': 'Either hours or package_id required'}), 400

        # Create Stripe checkout session
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': PaymentConfig.CURRENCY,
                        'product_data': {
                            'name': f'{hours} Hours of VarioSync Access',
                            'description': f'Purchase {hours} hours of access time'
                        },
                        'unit_amount': price_cents,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.host_url.rstrip('/') + '/payments/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.host_url.rstrip('/') + '/payments/cancel',
                metadata={
                    'user_id': str(user_id),
                    'hours': str(hours),
                    'package_id': package_id or ''
                }
            )

            logger.info(f"Stripe checkout session created for user {user_id}: {hours} hours")

            return jsonify({
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id
            }), 200

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            return jsonify({'error': f'Payment processing error: {str(e)}'}), 500

    except Exception as e:
        logger.error(f"Error creating checkout: {str(e)}")
        return jsonify({'error': str(e)}), 500

