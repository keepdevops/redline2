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


@auth_bp.route('/reset-password', methods=['GET'])
def reset_password_page():
    """
    Render password reset page
    """
    return render_template('reset_password.html')


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Send password reset email via Supabase Auth

    Request JSON:
        - email: User email address

    Returns:
        JSON with success status
    """
    # Get request data
    data = request.get_json()

    if not data:
        logger.warning("Password reset request with empty body")
        return jsonify({
            'error': 'Request body is required',
            'code': 'NO_DATA'
        }), 400

    if not isinstance(data, dict):
        logger.error(f"Password reset request with invalid data type: {type(data)}")
        return jsonify({
            'error': 'Request body must be JSON object',
            'code': 'INVALID_DATA_TYPE'
        }), 400

    # Validate email
    email = data.get('email')

    if not email:
        logger.warning("Password reset request missing email field")
        return jsonify({
            'error': 'Email address is required',
            'code': 'MISSING_EMAIL'
        }), 400

    if not isinstance(email, str):
        logger.error(f"Password reset email field has invalid type: {type(email)}")
        return jsonify({
            'error': 'Email must be a string',
            'code': 'INVALID_EMAIL_TYPE'
        }), 400

    if '@' not in email or len(email) < 3:
        logger.warning(f"Password reset request with invalid email format: {email}")
        return jsonify({
            'error': 'Invalid email format',
            'code': 'INVALID_EMAIL_FORMAT'
        }), 400

    logger.info(f"Processing password reset request for {email}")

    # Check if Supabase is available
    if not supabase_client.is_available():
        logger.error("Password reset failed: Supabase client not available")
        return jsonify({
            'error': 'Authentication service is not configured',
            'code': 'SERVICE_UNAVAILABLE'
        }), 503

    if not supabase_client.client:
        logger.error("Password reset failed: Supabase client is None")
        return jsonify({
            'error': 'Authentication service is not configured',
            'code': 'SERVICE_UNAVAILABLE'
        }), 503

    # Send password reset email via Supabase
    logger.debug(f"Calling Supabase Auth API to send reset email to {email}")

    # Note: For security, always return success message regardless of whether email exists
    # This prevents email enumeration attacks
    supabase_client.client.auth.reset_password_email(email)

    logger.info(f"Password reset email request processed for {email}")

    return jsonify({
        'success': True,
        'message': 'If an account exists with that email, a password reset link has been sent.'
    }), 200


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
    # Get request data
    data = request.get_json()

    if not data:
        logger.warning("Login request with empty body")
        return jsonify({
            'error': 'Request body is required',
            'code': 'NO_DATA'
        }), 400

    if not isinstance(data, dict):
        logger.error(f"Login request with invalid data type: {type(data)}")
        return jsonify({
            'error': 'Request body must be JSON object',
            'code': 'INVALID_DATA_TYPE'
        }), 400

    # Validate credentials
    email = data.get('email')
    password = data.get('password')

    if not email:
        logger.warning("Login request missing email field")
        return jsonify({
            'error': 'Email is required',
            'code': 'MISSING_EMAIL'
        }), 400

    if not password:
        logger.warning(f"Login request missing password field for email: {email}")
        return jsonify({
            'error': 'Password is required',
            'code': 'MISSING_PASSWORD'
        }), 400

    if not isinstance(email, str) or not isinstance(password, str):
        logger.error(f"Login credentials have invalid types - email: {type(email)}, password: {type(password)}")
        return jsonify({
            'error': 'Email and password must be strings',
            'code': 'INVALID_CREDENTIAL_TYPE'
        }), 400

    if '@' not in email:
        logger.warning(f"Login attempt with invalid email format: {email}")
        return jsonify({
            'error': 'Invalid email format',
            'code': 'INVALID_EMAIL_FORMAT'
        }), 400

    if len(password) < 6:
        logger.warning(f"Login attempt with password too short for email: {email}")
        return jsonify({
            'error': 'Invalid email or password',
            'code': 'INVALID_CREDENTIALS'
        }), 401

    logger.info(f"Processing login attempt for {email}")

    # Check if Supabase is available
    if not supabase_client.is_available():
        logger.error("Login failed: Supabase client not available")
        return jsonify({
            'error': 'Authentication service is not configured',
            'code': 'SERVICE_UNAVAILABLE'
        }), 503

    if not supabase_client.client:
        logger.error("Login failed: Supabase client is None")
        return jsonify({
            'error': 'Authentication service is not configured',
            'code': 'SERVICE_UNAVAILABLE'
        }), 503

    # Authenticate with Supabase
    logger.debug(f"Calling Supabase Auth API for email: {email}")
    auth_response = supabase_client.client.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

    # Validate auth response
    if not auth_response:
        logger.error(f"Supabase auth returned no response for email: {email}")
        return jsonify({
            'error': 'Authentication failed',
            'code': 'AUTH_FAILED'
        }), 401

    if not hasattr(auth_response, 'user') or not auth_response.user:
        logger.warning(f"Invalid credentials for email: {email}")
        return jsonify({
            'error': 'Invalid email or password',
            'code': 'INVALID_CREDENTIALS'
        }), 401

    if not hasattr(auth_response, 'session') or not auth_response.session:
        logger.error(f"Supabase auth succeeded but no session for email: {email}")
        return jsonify({
            'error': 'Authentication succeeded but session creation failed',
            'code': 'NO_SESSION'
        }), 500

    user_id = auth_response.user.id
    logger.debug(f"User authenticated successfully: {user_id}")

    # Get user profile from database
    user_profile = supabase_client.get_user_by_id(user_id)

    if not user_profile:
        logger.warning(f"User {user_id} authenticated but profile not found in database")

    logger.info(f"User {email} logged in successfully (user_id: {user_id})")

    return jsonify({
        'success': True,
        'access_token': auth_response.session.access_token,
        'refresh_token': auth_response.session.refresh_token,
        'user': {
            'id': user_id,
            'email': auth_response.user.email,
            'name': user_profile.get('name') if user_profile else email.split('@')[0],
            'stripe_customer_id': user_profile.get('stripe_customer_id') if user_profile else None
        }
    }), 200


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
    # Get request data
    data = request.get_json()

    if not data:
        logger.warning("Signup request with empty body")
        return jsonify({
            'error': 'Request body is required',
            'code': 'NO_DATA'
        }), 400

    if not isinstance(data, dict):
        logger.error(f"Signup request with invalid data type: {type(data)}")
        return jsonify({
            'error': 'Request body must be JSON object',
            'code': 'INVALID_DATA_TYPE'
        }), 400

    # Validate required fields
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if not email:
        logger.warning("Signup request missing email field")
        return jsonify({
            'error': 'Email is required',
            'code': 'MISSING_EMAIL'
        }), 400

    if not password:
        logger.warning(f"Signup request missing password for email: {email}")
        return jsonify({
            'error': 'Password is required',
            'code': 'MISSING_PASSWORD'
        }), 400

    if not name:
        logger.warning(f"Signup request missing name for email: {email}")
        return jsonify({
            'error': 'Name is required',
            'code': 'MISSING_NAME'
        }), 400

    # Validate field types
    if not isinstance(email, str) or not isinstance(password, str) or not isinstance(name, str):
        logger.error(f"Signup fields have invalid types - email: {type(email)}, password: {type(password)}, name: {type(name)}")
        return jsonify({
            'error': 'Email, password, and name must be strings',
            'code': 'INVALID_FIELD_TYPE'
        }), 400

    # Validate email format
    if '@' not in email or len(email) < 3:
        logger.warning(f"Signup attempt with invalid email format: {email}")
        return jsonify({
            'error': 'Invalid email format',
            'code': 'INVALID_EMAIL_FORMAT'
        }), 400

    # Validate password strength
    if len(password) < 6:
        logger.warning(f"Signup attempt with weak password for email: {email}")
        return jsonify({
            'error': 'Password must be at least 6 characters',
            'code': 'WEAK_PASSWORD'
        }), 400

    # Validate name length
    if len(name) < 2:
        logger.warning(f"Signup attempt with invalid name length for email: {email}")
        return jsonify({
            'error': 'Name must be at least 2 characters',
            'code': 'INVALID_NAME'
        }), 400

    logger.info(f"Processing signup for {email}")

    # Check if Supabase is available
    if not supabase_client.is_available():
        logger.error("Signup failed: Supabase client not available")
        return jsonify({
            'error': 'Authentication service is not configured',
            'code': 'SERVICE_UNAVAILABLE'
        }), 503

    if not supabase_client.client:
        logger.error("Signup failed: Supabase client is None")
        return jsonify({
            'error': 'Authentication service is not configured',
            'code': 'SERVICE_UNAVAILABLE'
        }), 503

    # Step 1: Create user in Supabase Auth
    logger.debug(f"Creating Supabase Auth user for email: {email}")
    auth_response = supabase_client.client.auth.sign_up({
        "email": email,
        "password": password,
        "options": {
            "data": {
                "name": name
            }
        }
    })

    if not auth_response:
        logger.error(f"Supabase signup returned no response for email: {email}")
        return jsonify({
            'error': 'Failed to create user account',
            'code': 'SIGNUP_FAILED'
        }), 400

    if not hasattr(auth_response, 'user') or not auth_response.user:
        logger.error(f"Supabase signup succeeded but no user for email: {email}")
        return jsonify({
            'error': 'Failed to create user account',
            'code': 'SIGNUP_FAILED'
        }), 400

    user_id = auth_response.user.id
    logger.info(f"Created Supabase Auth user {user_id} for {email}")

    # Step 2: Create Stripe customer
    logger.debug(f"Creating Stripe customer for email: {email}")
    customer = None

    if not stripe.api_key:
        logger.warning(f"Stripe API key not configured, skipping customer creation for {email}")
    else:
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={
                    'supabase_user_id': user_id,
                    'product': 'redline'
                }
            )

            if customer and hasattr(customer, 'id'):
                logger.info(f"Created Stripe customer {customer.id} for {email}")
            else:
                logger.warning(f"Stripe customer creation returned unexpected result for {email}")
                customer = None

        except stripe.error.InvalidRequestError as e:
            logger.error(f"Stripe invalid request creating customer for {email}: {str(e)}")
            customer = None
        except stripe.error.AuthenticationError as e:
            logger.error(f"Stripe authentication error creating customer for {email}: {str(e)}")
            customer = None
        except stripe.error.APIConnectionError as e:
            logger.error(f"Stripe API connection error creating customer for {email}: {str(e)}")
            customer = None
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating customer for {email}: {str(e)}")
            customer = None

    # Step 3: Create user profile in database
    logger.debug(f"Creating database user profile for email: {email}")
    user_profile = supabase_client.create_user_profile(
        user_id=user_id,
        email=email,
        stripe_customer_id=customer.id if customer else None,
        name=name
    )

    if user_profile:
        logger.info(f"Created user profile in Supabase database for {email}")
    else:
        logger.warning(f"Failed to create user profile in database for {email} (user_id: {user_id})")
        # Not critical - user can still log in

    # Return auth data for automatic login
    logger.info(f"Signup completed successfully for {email} (user_id: {user_id})")

    return jsonify({
        'success': True,
        'access_token': auth_response.session.access_token if hasattr(auth_response, 'session') and auth_response.session else None,
        'refresh_token': auth_response.session.refresh_token if hasattr(auth_response, 'session') and auth_response.session else None,
        'user': {
            'id': user_id,
            'email': email,
            'name': name,
            'stripe_customer_id': customer.id if customer else None
        },
        'message': 'Account created successfully'
    }), 201


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

    # Pre-validation with if-else
    if not supabase_client or not supabase_client.is_available():
        logger.error("Supabase client not available for get_current_user")
        return jsonify({
            'error': 'Authentication service unavailable',
            'code': 'SERVICE_UNAVAILABLE'
        }), 503

    try:
        user = supabase_client.get_user_by_id(user_id)

        if not user:
            logger.warning(f"User not found in database: {user_id}")
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

    except KeyError as e:
        logger.error(f"Missing required user field for {user_id}: {str(e)}")
        return jsonify({
            'error': 'Invalid user data structure',
            'code': 'INVALID_USER_DATA',
            'details': str(e)
        }), 500
    except Exception as e:
        logger.error(f"Unexpected error getting user {user_id}: {type(e).__name__}: {str(e)}")
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

    # Pre-validation with if-else
    if not supabase_client or not supabase_client.is_available():
        logger.error("Supabase client not available for get_user_usage")
        return jsonify({
            'error': 'Database service unavailable',
            'code': 'SERVICE_UNAVAILABLE'
        }), 503

    try:
        limit = int(request.args.get('limit', 100))

        if limit < 1 or limit > 1000:
            logger.warning(f"Invalid limit value requested: {limit}")
            return jsonify({
                'error': 'Limit must be between 1 and 1000',
                'code': 'INVALID_LIMIT'
            }), 400

        usage_records = supabase_client.get_user_usage(user_id, limit=limit)

        return jsonify({
            'usage_history': usage_records,
            'count': len(usage_records)
        })

    except ValueError as e:
        logger.error(f"Invalid limit parameter for user {user_id}: {str(e)}")
        return jsonify({
            'error': 'Invalid limit parameter',
            'code': 'INVALID_PARAMETER',
            'details': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Unexpected error getting usage for {user_id}: {type(e).__name__}: {str(e)}")
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

    # Pre-validation with if-else
    if not supabase_client or not supabase_client.is_available():
        logger.error("Supabase client not available for get_user_payments")
        return jsonify({
            'error': 'Database service unavailable',
            'code': 'SERVICE_UNAVAILABLE'
        }), 503

    try:
        limit = int(request.args.get('limit', 50))

        if limit < 1 or limit > 500:
            logger.warning(f"Invalid payment limit requested: {limit}")
            return jsonify({
                'error': 'Limit must be between 1 and 500',
                'code': 'INVALID_LIMIT'
            }), 400

        payment_records = supabase_client.get_user_payments(user_id, limit=limit)

        return jsonify({
            'payment_history': payment_records,
            'count': len(payment_records)
        })

    except ValueError as e:
        logger.error(f"Invalid limit parameter for payments {user_id}: {str(e)}")
        return jsonify({
            'error': 'Invalid limit parameter',
            'code': 'INVALID_PARAMETER',
            'details': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Unexpected error getting payments for {user_id}: {type(e).__name__}: {str(e)}")
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
        logger.warning("User requested subscription without Stripe customer ID")
        return jsonify({
            'error': 'No Stripe customer ID',
            'code': 'NO_STRIPE_CUSTOMER'
        }), 400

    try:
        from redline.payment.metered_billing import metered_billing_manager

        # Pre-validation with if-else
        if not metered_billing_manager or not metered_billing_manager.is_available():
            logger.error("Metered billing manager not available for subscription info")
            return jsonify({
                'error': 'Billing service unavailable',
                'code': 'SERVICE_UNAVAILABLE'
            }), 503

        subscription_info = metered_billing_manager.get_subscription_info(stripe_customer_id)

        if not subscription_info:
            logger.info(f"No active subscription found for customer: {stripe_customer_id}")
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

    except ImportError as e:
        logger.error(f"Import error getting subscription: {str(e)}")
        return jsonify({
            'error': 'Billing module not available',
            'code': 'MODULE_ERROR',
            'details': str(e)
        }), 503
    except Exception as e:
        logger.error(f"Unexpected error getting subscription for {stripe_customer_id}: {type(e).__name__}: {str(e)}")
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

    except RuntimeError as e:
        # Session-related errors
        logger.warning(f"Runtime error during logout (session clear failed): {str(e)}")
        return jsonify({
            'success': True,  # Still return success even if session clear fails
            'message': 'Logged out (session clear failed)'
        })
    except Exception as e:
        logger.error(f"Unexpected error during logout: {type(e).__name__}: {str(e)}")
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
