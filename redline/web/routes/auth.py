#!/usr/bin/env python3
"""
Authentication Routes for REDLINE
Handles Supabase Auth integration and Stripe customer creation
"""

from flask import Blueprint, request, jsonify, g, session as flask_session
from redline.database.supabase_client import supabase_client
from redline.auth.supabase_auth import auth_manager
import stripe
import os
import logging

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Create Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    Complete user signup after Supabase Auth
    Creates Stripe customer and user profile in Supabase

    Request JSON:
        - user_id: Supabase user ID (from Supabase Auth)
        - email: User email

    Returns:
        JSON with stripe_customer_id and success status
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'error': 'Request body is required',
                'code': 'NO_DATA'
            }), 400

        user_id = data.get('user_id')
        email = data.get('email')

        if not user_id or not email:
            return jsonify({
                'error': 'user_id and email are required',
                'code': 'MISSING_FIELDS'
            }), 400

        logger.info(f"Processing signup for user {email} ({user_id})")

        # Create Stripe customer
        try:
            customer = stripe.Customer.create(
                email=email,
                metadata={
                    'supabase_user_id': user_id,
                    'product': 'redline'
                }
            )
            logger.info(f"Created Stripe customer {customer.id} for {email}")

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating customer: {str(e)}")
            return jsonify({
                'error': 'Failed to create Stripe customer',
                'code': 'STRIPE_ERROR',
                'details': str(e)
            }), 500

        # Create user profile in Supabase
        try:
            user_profile = supabase_client.create_user_profile(
                user_id=user_id,
                email=email,
                stripe_customer_id=customer.id
            )

            logger.info(f"Created user profile in Supabase for {email}")

        except Exception as e:
            logger.error(f"Error creating user profile: {str(e)}")

            # Rollback: Delete Stripe customer if user profile creation failed
            try:
                stripe.Customer.delete(customer.id)
                logger.info(f"Rolled back Stripe customer {customer.id}")
            except Exception as rollback_error:
                logger.error(f"Failed to rollback Stripe customer: {str(rollback_error)}")

            return jsonify({
                'error': 'Failed to create user profile',
                'code': 'PROFILE_CREATION_ERROR',
                'details': str(e)
            }), 500

        return jsonify({
            'success': True,
            'stripe_customer_id': customer.id,
            'user_id': user_id,
            'message': 'User signup completed successfully'
        }), 201

    except Exception as e:
        logger.error(f"Unexpected error in signup: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR',
            'details': str(e)
        }), 500


@auth_bp.route('/user', methods=['GET'])
def get_current_user():
    """
    Get current authenticated user info

    Requires authentication (JWT token)

    Returns:
        JSON with user profile
    """
    user_id = auth_manager.get_current_user_id()

    if not user_id:
        return jsonify({
            'error': 'Not authenticated',
            'code': 'NOT_AUTHENTICATED'
        }), 401

    try:
        user = supabase_client.get_user_by_id(user_id)

        if not user:
            return jsonify({
                'error': 'User not found',
                'code': 'USER_NOT_FOUND'
            }), 404

        # Remove sensitive fields
        safe_user = {
            'id': user['id'],
            'email': user['email'],
            'stripe_customer_id': user.get('stripe_customer_id'),
            'subscription_status': user.get('subscription_status'),
            'current_period_start': user.get('current_period_start'),
            'current_period_end': user.get('current_period_end'),
            'created_at': user.get('created_at')
        }

        return jsonify(safe_user)

    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        return jsonify({
            'error': 'Failed to get user',
            'code': 'GET_USER_ERROR',
            'details': str(e)
        }), 500


@auth_bp.route('/user/usage', methods=['GET'])
def get_user_usage():
    """
    Get usage history for current user

    Requires authentication (JWT token)

    Query Parameters:
        - limit: Number of records to return (default: 100)

    Returns:
        JSON with usage history
    """
    user_id = auth_manager.get_current_user_id()

    if not user_id:
        return jsonify({
            'error': 'Not authenticated',
            'code': 'NOT_AUTHENTICATED'
        }), 401

    try:
        limit = int(request.args.get('limit', 100))

        if limit < 1 or limit > 1000:
            return jsonify({
                'error': 'Limit must be between 1 and 1000',
                'code': 'INVALID_LIMIT'
            }), 400

        usage_records = supabase_client.get_user_usage(user_id, limit=limit)

        return jsonify({
            'usage_history': usage_records,
            'count': len(usage_records)
        })

    except Exception as e:
        logger.error(f"Error getting usage: {str(e)}")
        return jsonify({
            'error': 'Failed to get usage',
            'code': 'GET_USAGE_ERROR',
            'details': str(e)
        }), 500


@auth_bp.route('/user/payments', methods=['GET'])
def get_user_payments():
    """
    Get payment history for current user

    Requires authentication (JWT token)

    Query Parameters:
        - limit: Number of records to return (default: 50)

    Returns:
        JSON with payment history
    """
    user_id = auth_manager.get_current_user_id()

    if not user_id:
        return jsonify({
            'error': 'Not authenticated',
            'code': 'NOT_AUTHENTICATED'
        }), 401

    try:
        limit = int(request.args.get('limit', 50))

        if limit < 1 or limit > 500:
            return jsonify({
                'error': 'Limit must be between 1 and 500',
                'code': 'INVALID_LIMIT'
            }), 400

        payment_records = supabase_client.get_user_payments(user_id, limit=limit)

        return jsonify({
            'payment_history': payment_records,
            'count': len(payment_records)
        })

    except Exception as e:
        logger.error(f"Error getting payments: {str(e)}")
        return jsonify({
            'error': 'Failed to get payments',
            'code': 'GET_PAYMENTS_ERROR',
            'details': str(e)
        }), 500


@auth_bp.route('/user/subscription', methods=['GET'])
def get_user_subscription():
    """
    Get current subscription info for user

    Requires authentication (JWT token)

    Returns:
        JSON with subscription info from Stripe
    """
    stripe_customer_id = getattr(g, 'stripe_customer_id', None)

    if not stripe_customer_id:
        return jsonify({
            'error': 'No Stripe customer ID',
            'code': 'NO_STRIPE_CUSTOMER'
        }), 400

    try:
        from redline.payment.metered_billing import metered_billing_manager

        subscription_info = metered_billing_manager.get_subscription_info(stripe_customer_id)

        if not subscription_info:
            return jsonify({
                'error': 'No active subscription found',
                'code': 'NO_SUBSCRIPTION'
            }), 404

        # Also get current usage
        usage_info = metered_billing_manager.get_current_usage(stripe_customer_id)

        return jsonify({
            'subscription': subscription_info,
            'usage': usage_info
        })

    except Exception as e:
        logger.error(f"Error getting subscription: {str(e)}")
        return jsonify({
            'error': 'Failed to get subscription',
            'code': 'GET_SUBSCRIPTION_ERROR',
            'details': str(e)
        }), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Logout user (clears session)

    Note: Actual token invalidation is handled by Supabase Auth client-side

    Returns:
        JSON with success message
    """
    try:
        # Clear Flask session
        flask_session.clear()

        # Log user out if available
        user_id = auth_manager.get_current_user_id()
        if user_id:
            logger.info(f"User {user_id} logged out")

        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        })

    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        return jsonify({
            'success': True,  # Still return success even if logging fails
            'message': 'Logged out (with warnings)'
        })


@auth_bp.route('/status', methods=['GET'])
def auth_status():
    """
    Check authentication status

    Returns:
        JSON with authentication status and user info if authenticated
    """
    user_id = auth_manager.get_current_user_id()

    if not user_id:
        return jsonify({
            'authenticated': False
        })

    try:
        user = auth_manager.get_current_user()

        if not user:
            return jsonify({
                'authenticated': False
            })

        return jsonify({
            'authenticated': True,
            'user_id': user['id'],
            'email': user['email'],
            'subscription_status': user.get('subscription_status', 'inactive')
        })

    except Exception as e:
        logger.error(f"Error checking auth status: {str(e)}")
        return jsonify({
            'authenticated': False,
            'error': str(e)
        })
