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

    # Import Supabase client
    try:
        from redline.database.supabase_client import supabase_client
    except ImportError:
        logger.error("Supabase client not available")
        return jsonify({'error': 'Database not available'}), 503

    event_type = event['type']
    logger.info(f"Received Stripe webhook: {event_type}")

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

