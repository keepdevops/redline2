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
    """Handle Stripe webhook events for subscriptions"""
    # Check if Stripe is available
    if not STRIPE_AVAILABLE:
        logger.error("Stripe webhook received but Stripe library not available")
        return jsonify({'error': 'Stripe is not available'}), 503

    if not stripe:
        logger.error("Stripe webhook received but stripe module is None")
        return jsonify({'error': 'Stripe is not available'}), 503

    # Check webhook secret configuration
    if not PaymentConfig.STRIPE_WEBHOOK_SECRET:
        logger.error("Stripe webhook received but STRIPE_WEBHOOK_SECRET is not configured")
        return jsonify({'error': 'Webhook secret not configured'}), 500

    if not isinstance(PaymentConfig.STRIPE_WEBHOOK_SECRET, str):
        logger.error(f"STRIPE_WEBHOOK_SECRET has invalid type: {type(PaymentConfig.STRIPE_WEBHOOK_SECRET)}")
        return jsonify({'error': 'Webhook secret invalid'}), 500

    if len(PaymentConfig.STRIPE_WEBHOOK_SECRET) < 20:
        logger.error(f"STRIPE_WEBHOOK_SECRET appears invalid (too short: {len(PaymentConfig.STRIPE_WEBHOOK_SECRET)} chars)")
        return jsonify({'error': 'Webhook secret invalid'}), 500

    # Get payload and signature
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    if not payload:
        logger.error("Stripe webhook received with empty payload")
        return jsonify({'error': 'Empty payload'}), 400

    if not sig_header:
        logger.error("Stripe webhook received without Stripe-Signature header")
        return jsonify({'error': 'Missing signature'}), 400

    if not isinstance(sig_header, str):
        logger.error(f"Stripe-Signature header has invalid type: {type(sig_header)}")
        return jsonify({'error': 'Invalid signature format'}), 400

    logger.debug(f"Verifying Stripe webhook signature (payload size: {len(payload)} bytes)")

    # Verify webhook signature
    # Note: This is a legitimate use of try-except as stripe.Webhook.construct_event
    # raises specific exceptions for different verification failures
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, PaymentConfig.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Stripe webhook has invalid payload format: {str(e)}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Stripe webhook signature verification failed: {str(e)}")
        return jsonify({'error': 'Invalid signature'}), 400

    # Validate event structure
    if not event:
        logger.error("Stripe webhook verification succeeded but event is None")
        return jsonify({'error': 'Invalid event'}), 400

    if not isinstance(event, dict):
        logger.error(f"Stripe webhook event has invalid type: {type(event)}")
        return jsonify({'error': 'Invalid event'}), 400

    if 'type' not in event:
        logger.error("Stripe webhook event missing 'type' field")
        return jsonify({'error': 'Invalid event'}), 400

    if 'data' not in event or 'object' not in event.get('data', {}):
        logger.error("Stripe webhook event missing 'data.object' field")
        return jsonify({'error': 'Invalid event'}), 400

    # Import Supabase client
    from redline.database.supabase_client import supabase_client

    if not supabase_client.is_available():
        logger.error("Stripe webhook received but Supabase client not available")
        return jsonify({'error': 'Database not available'}), 503

    event_type = event['type']
    event_id = event.get('id', 'unknown')
    logger.info(f"Processing Stripe webhook event: {event_type} (id: {event_id})")

    # Handle checkout session completed (initial subscription signup)
    if event_type == 'checkout.session.completed':
        session = event['data']['object']
        customer_id = session.get('customer')
        customer_email = session.get('customer_email') or session.get('customer_details', {}).get('email')
        subscription_id = session.get('subscription')

        logger.info(f"Checkout completed: customer={customer_id}, email={customer_email}, subscription={subscription_id}")

        if customer_email and customer_id:
            # Update or create user with Stripe customer ID
            try:
                user = supabase_client.get_user_by_email(customer_email)
                if user:
                    supabase_client.update_user(user['id'], {
                        'stripe_customer_id': customer_id,
                        'subscription_status': 'active' if subscription_id else 'inactive'
                    })
                    logger.info(f"Updated user {customer_email} with Stripe customer ID {customer_id}")
            except Exception as e:
                logger.error(f"Failed to update user with Stripe customer ID: {str(e)}")

    # Handle subscription created
    elif event_type == 'customer.subscription.created':
        subscription = event['data']['object']
        customer_id = subscription['customer']
        status = subscription['status']

        logger.info(f"Subscription created: customer={customer_id}, status={status}")

        try:
            user = supabase_client.get_user_by_stripe_customer_id(customer_id)
            if user:
                supabase_client.update_user(user['id'], {
                    'subscription_status': status,
                    'subscription_id': subscription['id']
                })
                logger.info(f"Updated user subscription status to {status}")
        except Exception as e:
            logger.error(f"Failed to update subscription status: {str(e)}")

    # Handle subscription updated (status changes)
    elif event_type == 'customer.subscription.updated':
        subscription = event['data']['object']
        customer_id = subscription['customer']
        status = subscription['status']

        logger.info(f"Subscription updated: customer={customer_id}, status={status}")

        try:
            user = supabase_client.get_user_by_stripe_customer_id(customer_id)
            if user:
                supabase_client.update_user(user['id'], {
                    'subscription_status': status
                })
                logger.info(f"Updated user subscription status to {status}")
        except Exception as e:
            logger.error(f"Failed to update subscription status: {str(e)}")

    # Handle subscription deleted (cancelled)
    elif event_type == 'customer.subscription.deleted':
        subscription = event['data']['object']
        customer_id = subscription['customer']

        logger.info(f"Subscription deleted: customer={customer_id}")

        try:
            user = supabase_client.get_user_by_stripe_customer_id(customer_id)
            if user:
                supabase_client.update_user(user['id'], {
                    'subscription_status': 'cancelled'
                })
                logger.info(f"Updated user subscription status to cancelled")
        except Exception as e:
            logger.error(f"Failed to update subscription status: {str(e)}")

    # Handle successful invoice payment
    elif event_type == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        customer_id = invoice['customer']
        subscription_id = invoice.get('subscription')

        logger.info(f"Invoice paid: customer={customer_id}, subscription={subscription_id}, amount={invoice['amount_paid']/100}")

        try:
            user = supabase_client.get_user_by_stripe_customer_id(customer_id)
            if user:
                # Log invoice payment
                supabase_client.log_payment(
                    user_id=user['id'],
                    amount=invoice['amount_paid'] / 100,
                    currency=invoice['currency'],
                    stripe_invoice_id=invoice['id'],
                    status='paid'
                )
                logger.info(f"Logged invoice payment for user {user['email']}")
        except Exception as e:
            logger.error(f"Failed to log invoice payment: {str(e)}")

    # Handle failed invoice payment
    elif event_type == 'invoice.payment_failed':
        invoice = event['data']['object']
        customer_id = invoice['customer']

        logger.warning(f"Invoice payment failed: customer={customer_id}")

        try:
            user = supabase_client.get_user_by_stripe_customer_id(customer_id)
            if user:
                # Update subscription status
                supabase_client.update_user(user['id'], {
                    'subscription_status': 'past_due'
                })
                logger.info(f"Updated user subscription status to past_due")
        except Exception as e:
            logger.error(f"Failed to update subscription status: {str(e)}")

    else:
        logger.info(f"Unhandled webhook event type: {event_type}")

    return jsonify({'received': True}), 200

