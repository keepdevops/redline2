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
    # Check if Stripe is explicitly disabled via environment variable
    stripe_disabled = os.environ.get('STRIPE_DISABLED', 'false').lower() in ('true', '1', 'yes')
    
    # Check if Stripe is not configured (missing keys or invalid price ID)
    metered_price_id = os.environ.get('STRIPE_PRICE_ID_METERED', '').strip()
    if '#' in metered_price_id:
        metered_price_id = metered_price_id.split('#')[0].strip()
    
    # Price ID is invalid if it doesn't start with 'price_'
    price_id_invalid = metered_price_id and not metered_price_id.startswith('price_')
    
    stripe_not_configured = (
        not PaymentConfig.STRIPE_SECRET_KEY or 
        not PaymentConfig.STRIPE_PUBLISHABLE_KEY or
        not metered_price_id or
        price_id_invalid
    )
    
    # If Stripe is disabled or not configured, return friendly message
    if stripe_disabled or stripe_not_configured:
        if stripe_disabled:
            logger.info("Checkout request received but Stripe is disabled (STRIPE_DISABLED=true)")
            return jsonify({
                'error': 'Stripe payments are currently disabled',
                'message': 'Payment processing is temporarily unavailable. Please contact support for assistance.',
                'disabled': True
            }), 503
        else:
            logger.info("Checkout request received but Stripe is not configured")
            return jsonify({
                'error': 'Stripe payments are not configured',
                'message': 'Payment processing is not available. Please contact support for assistance.',
                'disabled': True
            }), 503
    
    # Validate Stripe availability
    if not STRIPE_AVAILABLE:
        logger.error("Checkout request received but Stripe library not available")
        return jsonify({
            'error': 'Stripe is not available',
            'message': 'Payment processing is temporarily unavailable. Please contact support for assistance.',
            'disabled': True
        }), 503

    if not stripe:
        logger.error("Checkout request received but stripe module is None")
        return jsonify({
            'error': 'Stripe is not available',
            'message': 'Payment processing is temporarily unavailable. Please contact support for assistance.',
            'disabled': True
        }), 503

    # Validate payment configuration
    if not PaymentConfig.validate():
        logger.error("Checkout request received but PaymentConfig validation failed")
        return jsonify({
            'error': 'Payment configuration is invalid',
            'message': 'Payment processing is not properly configured. Please contact support for assistance.',
            'disabled': True
        }), 503

    # Get request data
    data = request.get_json()

    if not data:
        logger.warning("Checkout request with empty body")
        return jsonify({'error': 'Request body is required'}), 400

    if not isinstance(data, dict):
        logger.error(f"Checkout request with invalid data type: {type(data)}")
        return jsonify({'error': 'Request body must be JSON object'}), 400

    # Validate email
    email = data.get('email')

    if not email:
        logger.warning("Checkout request missing email field")
        return jsonify({'error': 'Email is required'}), 400

    if not isinstance(email, str):
        logger.error(f"Checkout request email has invalid type: {type(email)}")
        return jsonify({'error': 'Email must be a string'}), 400

    if '@' not in email or len(email) < 3:
        logger.warning(f"Checkout request with invalid email format: {email}")
        return jsonify({'error': 'Invalid email format'}), 400

    logger.info(f"Processing subscription checkout for email: {email}")

    # metered_price_id was already retrieved and validated above
    # At this point, we know it's valid (starts with 'price_') because we checked earlier

    logger.debug(f"Using metered price ID: {metered_price_id}")

    # Validate host URL for callback URLs
    host_url = request.host_url.rstrip('/')

    if not host_url:
        logger.error("Cannot determine host URL for checkout callbacks")
        return jsonify({'error': 'Server configuration error'}), 500

    if not host_url.startswith('http'):
        logger.error(f"Invalid host URL format: {host_url}")
        return jsonify({'error': 'Server configuration error'}), 500

    success_url = f"{host_url}/payments/subscription-success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{host_url}/payments/subscription-cancel"

    logger.debug(f"Checkout URLs - success: {success_url}, cancel: {cancel_url}")

    # Create Stripe checkout session
    logger.debug(f"Creating Stripe checkout session for email: {email}")

    # Note: Stripe API calls can raise specific exceptions - this is legitimate exception handling
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': metered_price_id,
                'quantity': 1,
            }],
            mode='subscription',
            customer_email=email,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'email': email
            },
            allow_promotion_codes=True,
            billing_address_collection='auto'
        )
    except stripe.error.InvalidRequestError as e:
        logger.error(f"Stripe invalid request error creating checkout for {email}: {str(e)}")
        return jsonify({'error': f'Invalid payment request: {str(e)}'}), 400
    except stripe.error.AuthenticationError as e:
        logger.error(f"Stripe authentication error creating checkout for {email}: {str(e)}")
        return jsonify({'error': 'Payment service authentication failed'}), 500
    except stripe.error.APIConnectionError as e:
        logger.error(f"Stripe API connection error creating checkout for {email}: {str(e)}")
        return jsonify({'error': 'Payment service temporarily unavailable'}), 503
    except stripe.error.RateLimitError as e:
        logger.error(f"Stripe rate limit error creating checkout for {email}: {str(e)}")
        return jsonify({'error': 'Payment service rate limit reached, please try again later'}), 429
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating checkout for {email}: {str(e)}")
        return jsonify({'error': f'Payment processing error: {str(e)}'}), 500

    # Validate checkout session response
    if not checkout_session:
        logger.error(f"Stripe checkout creation returned no session for email: {email}")
        return jsonify({'error': 'Failed to create checkout session'}), 500

    if not hasattr(checkout_session, 'url') or not checkout_session.url:
        logger.error(f"Stripe checkout session missing URL for email: {email}")
        return jsonify({'error': 'Failed to create checkout session'}), 500

    if not hasattr(checkout_session, 'id') or not checkout_session.id:
        logger.error(f"Stripe checkout session missing ID for email: {email}")
        return jsonify({'error': 'Failed to create checkout session'}), 500

    logger.info(f"Successfully created Stripe checkout session for {email} (session_id: {checkout_session.id})")

    return jsonify({
        'checkout_url': checkout_session.url,
        'session_id': checkout_session.id
    }), 200

