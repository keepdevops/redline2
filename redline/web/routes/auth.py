#!/usr/bin/env python3
"""
Authentication Routes for REDLINE
Handles Supabase Auth integration and Stripe customer creation
"""

from flask import Blueprint, request, jsonify, g, session as flask_session, render_template
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


@auth_bp.route('/login', methods=['GET'])
def login_page():
    """
    Render login page
    """
    return render_template('login.html')


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Handle user login with Supabase Auth

    Request JSON:
        - email: User email
        - password: User password

    Returns:
        JSON with access_token and user data
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'error': 'Request body is required',
                'code': 'NO_DATA'
            }), 400

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({
                'error': 'Email and password are required',
                'code': 'MISSING_CREDENTIALS'
            }), 400

        logger.info(f"Login attempt for {email}")

        # Authenticate with Supabase
        try:
            auth_response = supabase_client.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if not auth_response.user:
                return jsonify({
                    'error': 'Invalid email or password',
                    'code': 'INVALID_CREDENTIALS'
                }), 401

            # Get user profile from database
            user_profile = supabase_client.get_user_by_id(auth_response.user.id)

            logger.info(f"User {email} logged in successfully")

            return jsonify({
                'success': True,
                'access_token': auth_response.session.access_token,
                'refresh_token': auth_response.session.refresh_token,
                'user': {
                    'id': auth_response.user.id,
                    'email': auth_response.user.email,
                    'name': user_profile.get('name') if user_profile else email.split('@')[0],
                    'stripe_customer_id': user_profile.get('stripe_customer_id') if user_profile else None
                }
            }), 200

        except Exception as e:
            logger.error(f"Supabase auth error: {str(e)}")
            return jsonify({
                'error': 'Invalid email or password',
                'code': 'AUTH_FAILED',
                'details': str(e)
            }), 401

    except Exception as e:
        logger.error(f"Unexpected error in login: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR',
            'details': str(e)
        }), 500


@auth_bp.route('/signup', methods=['GET'])
def signup_page():
    """
    Render signup page
    """
    return render_template('signup.html')


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    Handle user signup with Supabase Auth and Stripe
    Creates user account, Stripe customer, and user profile

    Request JSON:
        - email: User email
        - password: User password
        - name: User full name

    Returns:
        JSON with access_token and user data
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'error': 'Request body is required',
                'code': 'NO_DATA'
            }), 400

        email = data.get('email')
        password = data.get('password')
        name = data.get('name')

        if not email or not password or not name:
            return jsonify({
                'error': 'Email, password, and name are required',
                'code': 'MISSING_FIELDS'
            }), 400

        logger.info(f"Processing signup for {email}")

        # Create user in Supabase Auth
        try:
            auth_response = supabase_client.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "name": name
                    }
                }
            })

            if not auth_response.user:
                return jsonify({
                    'error': 'Failed to create user account',
                    'code': 'SIGNUP_FAILED'
                }), 400

            user_id = auth_response.user.id
            logger.info(f"Created Supabase user {user_id} for {email}")

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Supabase signup error: {error_msg}")

            if 'already registered' in error_msg.lower() or 'already exists' in error_msg.lower():
                return jsonify({
                    'error': 'An account with this email already exists',
                    'code': 'EMAIL_EXISTS'
                }), 409

            return jsonify({
                'error': 'Failed to create account',
                'code': 'AUTH_ERROR',
                'details': error_msg
            }), 400

        # Create Stripe customer
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={
                    'supabase_user_id': user_id,
                    'product': 'redline'
                }
            )
            logger.info(f"Created Stripe customer {customer.id} for {email}")

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating customer: {str(e)}")
            # Continue without Stripe - user can still sign up
            customer = None

        # Create user profile in Supabase database
        try:
            user_profile = supabase_client.create_user_profile(
                user_id=user_id,
                email=email,
                stripe_customer_id=customer.id if customer else None,
                name=name
            )
            logger.info(f"Created user profile in Supabase for {email}")

        except Exception as e:
            logger.error(f"Error creating user profile: {str(e)}")
            # Profile creation is not critical - continue

        # Return auth data for automatic login
        return jsonify({
            'success': True,
            'access_token': auth_response.session.access_token if auth_response.session else None,
            'refresh_token': auth_response.session.refresh_token if auth_response.session else None,
            'user': {
                'id': user_id,
                'email': email,
                'name': name,
                'stripe_customer_id': customer.id if customer else None
            },
            'message': 'Account created successfully'
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
