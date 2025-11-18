#!/usr/bin/env python3
"""
Payment webhook routes for REDLINE Web GUI
Handles Stripe webhook events
"""

from flask import Blueprint, request, jsonify
import logging
import os
import requests

try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    stripe = None

from redline.payment.config import PaymentConfig

payments_webhook_bp = Blueprint('payments_webhook', __name__)
logger = logging.getLogger(__name__)

# Initialize Stripe if available
if STRIPE_AVAILABLE and PaymentConfig.STRIPE_SECRET_KEY:
    stripe.api_key = PaymentConfig.STRIPE_SECRET_KEY

@payments_webhook_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    if not STRIPE_AVAILABLE:
        logger.warning("Stripe webhook received but Stripe is not available")
        return jsonify({'error': 'Stripe is not available'}), 503
    
    if not PaymentConfig.STRIPE_WEBHOOK_SECRET:
        logger.warning("Stripe webhook received but STRIPE_WEBHOOK_SECRET is not set")
        return jsonify({'error': 'Webhook secret not configured'}), 500
    
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, PaymentConfig.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        license_key = session['metadata'].get('license_key')
        hours = float(session['metadata'].get('hours', 0))
        
        if license_key and hours > 0:
            # Add hours to license
            license_server_url = PaymentConfig.LICENSE_SERVER_URL
            require_license_server = os.environ.get('REQUIRE_LICENSE_SERVER', 'false').lower() == 'true'
            
            try:
                response = requests.post(
                    f'{license_server_url}/api/licenses/{license_key}/hours',
                    json={'hours': hours},
                    timeout=10
                )
            except requests.exceptions.ConnectionError:
                # License server unavailable - log payment but can't add hours
                if not require_license_server:
                    logger.warning(f"License server unavailable, payment processed but hours not added to server for {license_key}")
                    # Log payment anyway
                    try:
                        from redline.database.usage_storage import usage_storage
                        if usage_storage:
                            usage_storage.log_payment(
                                license_key=license_key,
                                hours=hours,
                                amount=session['amount_total'] / 100,
                                currency=session['currency'],
                                payment_id=session['id'],
                                status='completed'
                            )
                    except Exception as e:
                        logger.warning(f"Failed to log payment: {str(e)}")
                    return jsonify({'received': True}), 200
                else:
                    logger.error(f"License server unavailable and REQUIRE_LICENSE_SERVER=true")
                    return jsonify({'received': True, 'warning': 'License server unavailable'}), 200
            
            try:
                if response.status_code == 200:
                    result = response.json()
                    
                    # Log payment to persistent storage
                    try:
                        from redline.database.usage_storage import usage_storage
                        if usage_storage:
                            usage_storage.log_payment(
                                license_key=license_key,
                                hours_purchased=hours,
                                amount_paid=session.get('amount_total', 0) / 100.0,  # Convert cents to dollars
                                stripe_session_id=session.get('id'),
                                payment_id=session.get('payment_intent'),
                                payment_status='completed',
                                currency=session.get('currency', 'usd')
                            )
                    except Exception as e:
                        logger.warning(f"Failed to log payment to storage: {str(e)}")
                    
                    logger.info(f"Added {hours} hours to license {license_key} via webhook")
                else:
                    logger.error(f"Failed to add hours via webhook: {response.text}")
            except Exception as e:
                logger.error(f"Error adding hours via webhook: {str(e)}")
    
    return jsonify({'received': True}), 200

