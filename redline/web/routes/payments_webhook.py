#!/usr/bin/env python3
"""
Payment webhook routes for VarioSync Web GUI
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
    """Handle Stripe webhook events (payment completion)"""
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
        user_id = session['metadata'].get('user_id')
        hours = float(session['metadata'].get('hours', 0))

        if user_id and hours > 0:
            try:
                # Add hours to Supabase user_hours table
                from redline.auth.supabase_auth import supabase_auth
                success = supabase_auth.add_hours(user_id, hours)

                if success:
                    # Log payment to DuckDB
                    try:
                        from redline.database.usage_storage import usage_storage
                        if usage_storage:
                            usage_storage.log_payment(
                                user_id=user_id,
                                hours_purchased=hours,
                                amount_paid=session.get('amount_total', 0) / 100.0,
                                stripe_session_id=session.get('id'),
                                payment_id=session.get('payment_intent'),
                                payment_status='completed',
                                currency=session.get('currency', 'usd')
                            )
                    except Exception as e:
                        logger.warning(f"Failed to log payment to storage: {str(e)}")

                    logger.info(f"Added {hours} hours to user {user_id} via webhook")
                else:
                    logger.error(f"Failed to add hours to user {user_id}")

            except Exception as e:
                logger.error(f"Error processing webhook for user {user_id}: {str(e)}")

    return jsonify({'received': True}), 200

