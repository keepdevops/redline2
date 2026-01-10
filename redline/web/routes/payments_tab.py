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
        except stripe.error.InvalidRequestError as stripe_err:
            error_msg = str(stripe_err) if str(stripe_err) else 'Invalid subscription session'
            logger.error(f"Stripe invalid request error: {error_msg}")
            return render_template('subscription_success.html',
                                 success=False,
                                 error=f'Subscription verification error: {error_msg}'), 400
        except stripe.error.AuthenticationError as stripe_err:
            error_msg = 'Authentication failed'
            logger.error(f"Stripe authentication error: {str(stripe_err)}")
            return render_template('subscription_success.html',
                                 success=False,
                                 error=f'Subscription verification error: {error_msg}'), 500
        except stripe.error.APIConnectionError as stripe_err:
            error_msg = 'Service temporarily unavailable'
            logger.error(f"Stripe API connection error: {str(stripe_err)}")
            return render_template('subscription_success.html',
                                 success=False,
                                 error=f'Subscription verification error: {error_msg}'), 503
        except stripe.error.StripeError as stripe_err:
            error_msg = str(stripe_err) if str(stripe_err) else 'Payment service error'
            logger.error(f"Stripe error: {error_msg}")
            return render_template('subscription_success.html',
                                 success=False,
                                 error=f'Subscription verification error: {error_msg}'), 500
        except Exception as stripe_err:
            error_msg = str(stripe_err) if str(stripe_err) else 'Invalid subscription session'
            logger.error(f"Unexpected error retrieving session: {error_msg}")
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
            except ImportError as e:
                logger.error(f"Import error updating user: {str(e)}")
            except AttributeError as e:
                logger.error(f"Attribute error updating user: {str(e)}")
            except KeyError as e:
                logger.error(f"Missing key updating user: {str(e)}")
            except TypeError as e:
                logger.error(f"Type error updating user: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error updating user: {str(e)}")

            return render_template('subscription_success.html',
                                 success=True,
                                 email=customer_email,
                                 subscription_id=subscription.id if subscription else None)
        else:
            return render_template('subscription_success.html',
                                 success=False,
                                 error=f'Subscription status: {session.status}'), 400

    except AttributeError as e:
        error_msg = str(e) if str(e) else 'Attribute access error'
        logger.error(f"Attribute error in subscription_success: {error_msg}")
        logger.error(traceback.format_exc())
        return render_template('subscription_success.html',
                             success=False,
                             error=error_msg), 500
    except KeyError as e:
        error_msg = str(e) if str(e) else 'Missing data error'
        logger.error(f"Key error in subscription_success: {error_msg}")
        logger.error(traceback.format_exc())
        return render_template('subscription_success.html',
                             success=False,
                             error=error_msg), 500
    except TypeError as e:
        error_msg = str(e) if str(e) else 'Type error'
        logger.error(f"Type error in subscription_success: {error_msg}")
        logger.error(traceback.format_exc())
        return render_template('subscription_success.html',
                             success=False,
                             error=error_msg), 500
    except Exception as e:
        error_msg = str(e) if str(e) else 'Unknown error occurred'
        logger.error(f"Unexpected error in subscription_success: {error_msg}")
        logger.error(traceback.format_exc())
        return render_template('subscription_success.html',
                             success=False,
                             error=error_msg), 500

@payments_tab_bp.route('/subscription-cancel', methods=['GET'])
def subscription_cancel():
    """Handle subscription cancellation page"""
    return render_template('subscription_cancel.html')

# Note: payment_tab route is defined in payments.py as an alias
# to maintain backward compatibility with templates using url_for('payments.payment_tab')
