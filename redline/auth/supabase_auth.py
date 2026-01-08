#!/usr/bin/env python3
"""
Supabase Authentication Manager for REDLINE
Handles JWT token validation and user authentication
"""

from functools import wraps
from flask import request, jsonify, g
from redline.database.supabase_client import supabase_client
import jwt
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class SupabaseAuthManager:
    """Authenticate users via Supabase Auth JWT tokens"""

    def __init__(self):
        self.jwt_secret = os.environ.get('SUPABASE_JWT_SECRET')
        self.supabase_url = os.environ.get('SUPABASE_URL')

        if not self.jwt_secret:
            logger.warning("SUPABASE_JWT_SECRET not configured. JWT validation will fail.")
        if not self.supabase_url:
            logger.warning("SUPABASE_URL not configured.")

    def is_available(self) -> bool:
        """Check if auth manager is properly configured"""
        return bool(self.jwt_secret and self.supabase_url and supabase_client.is_available())

    # ========================================================================
    # JWT TOKEN VALIDATION
    # ========================================================================

    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify Supabase JWT token

        Args:
            token: JWT token string

        Returns:
            Decoded token payload or None if invalid
        """
        if not self.jwt_secret:
            logger.error("Cannot verify JWT: SUPABASE_JWT_SECRET not set")
            return None

        # Validate token input
        if not token:
            logger.error("Cannot verify JWT: token is empty or None")
            return None

        if not isinstance(token, str):
            logger.error(f"Cannot verify JWT: token must be string, got {type(token)}")
            return None

        if len(token) < 20:
            logger.error(f"Cannot verify JWT: token too short ({len(token)} chars), appears invalid")
            return None

        # JWT tokens typically have 3 parts separated by dots
        token_parts = token.split('.')
        if len(token_parts) != 3:
            logger.error(f"Cannot verify JWT: invalid token format (expected 3 parts, got {len(token_parts)})")
            return None

        logger.debug("Attempting to decode JWT token")

        # Note: jwt.decode raises specific exceptions that we need to catch
        # This is a legitimate use of exception handling for library behavior
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=['HS256'],
                audience='authenticated'
            )
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidAudienceError:
            logger.warning("JWT token has invalid audience")
            return None
        except jwt.InvalidSignatureError:
            logger.warning("JWT token has invalid signature")
            return None
        except jwt.DecodeError as e:
            logger.warning(f"JWT token decode error: {str(e)}")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"JWT token is invalid: {str(e)}")
            return None

        # Validate decoded payload
        if not payload:
            logger.error("JWT decode returned empty payload")
            return None

        if not isinstance(payload, dict):
            logger.error(f"JWT decode returned unexpected type: {type(payload)}")
            return None

        user_id = payload.get('sub')
        if not user_id:
            logger.error("JWT token missing 'sub' claim (user ID)")
            return None

        logger.debug(f"JWT token verified successfully for user: {user_id}")
        return payload

    def get_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Get user info from JWT token and fetch full profile from Supabase

        Args:
            token: JWT token string

        Returns:
            User profile dict or None if token invalid or user not found
        """
        # Validate token input
        if not token:
            logger.error("Cannot get user from token: token is empty or None")
            return None

        # Verify token (includes validation and decoding)
        logger.debug("Verifying JWT token to extract user information")
        payload = self.verify_jwt_token(token)

        if not payload:
            logger.warning("Cannot get user from token: token verification failed")
            return None

        # Extract user ID from token
        user_id = payload.get('sub')  # Supabase user ID (UUID)
        email = payload.get('email')

        if not user_id:
            logger.error("No user ID (sub claim) found in JWT token payload")
            return None

        logger.debug(f"JWT token contains user_id: {user_id}, email: {email}")

        # Check if Supabase client is available
        if not supabase_client.is_available():
            logger.error("Cannot fetch user profile: Supabase client not available")
            return None

        # Get full user profile from Supabase database
        logger.debug(f"Fetching full user profile from Supabase for user_id: {user_id}")
        user = supabase_client.get_user_by_id(user_id)

        if not user:
            logger.warning(f"User {user_id} (email: {email}) not found in Supabase database")
            return None

        # Validate user data structure
        if not isinstance(user, dict):
            logger.error(f"User profile returned unexpected type: {type(user)}")
            return None

        if 'id' not in user:
            logger.error(f"User profile missing 'id' field for user {user_id}")
            return None

        logger.debug(f"Successfully retrieved user profile for {email} ({user_id})")
        return user

    # ========================================================================
    # TOKEN EXTRACTION
    # ========================================================================

    def extract_token_from_request(self, request) -> Optional[str]:
        """
        Extract JWT token from request headers or cookies

        Args:
            request: Flask request object

        Returns:
            JWT token string or None if not found
        """
        # Try Authorization header first (standard approach)
        auth_header = request.headers.get('Authorization')
        if auth_header:
            # Support both "Bearer <token>" and just "<token>"
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]  # Remove 'Bearer ' prefix
                logger.debug("Token found in Authorization header")
                return token
            else:
                logger.debug("Token found in Authorization header (no Bearer prefix)")
                return auth_header

        # Try cookie (Supabase Auth stores token here by default)
        token = request.cookies.get('sb-access-token')
        if token:
            logger.debug("Token found in sb-access-token cookie")
            return token

        # Try alternative cookie name
        token = request.cookies.get('supabase-auth-token')
        if token:
            logger.debug("Token found in supabase-auth-token cookie")
            return token

        # Try custom header
        token = request.headers.get('X-Supabase-Token')
        if token:
            logger.debug("Token found in X-Supabase-Token header")
            return token

        logger.debug("No token found in request")
        return None

    # ========================================================================
    # AUTHENTICATION DECORATORS
    # ========================================================================

    def require_auth(self, f):
        """
        Decorator to require authentication for a Flask route

        Usage:
            @app.route('/protected')
            @auth_manager.require_auth
            def protected_route():
                user_id = g.user_id
                return jsonify({'message': 'Authenticated!'})
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Extract token
            token = self.extract_token_from_request(request)

            if not token:
                return jsonify({
                    'error': 'Authentication required',
                    'code': 'NO_TOKEN',
                    'message': 'No authentication token provided'
                }), 401

            # Verify token and get user
            user = self.get_user_from_token(token)

            if not user:
                return jsonify({
                    'error': 'Invalid or expired token',
                    'code': 'INVALID_TOKEN',
                    'message': 'The provided authentication token is invalid or has expired'
                }), 401

            # Store user context in Flask g object
            g.user_id = user['id']
            g.email = user['email']
            g.stripe_customer_id = user.get('stripe_customer_id')
            g.subscription_status = user.get('subscription_status', 'inactive')
            g.user = user

            logger.debug(f"Authenticated user: {g.email} ({g.user_id})")

            # Call the actual route function
            return f(*args, **kwargs)

        return decorated_function

    def require_active_subscription(self, f):
        """
        Decorator to require active subscription for a Flask route

        Usage:
            @app.route('/premium')
            @auth_manager.require_active_subscription
            def premium_route():
                return jsonify({'message': 'Premium content!'})
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # First require authentication
            token = self.extract_token_from_request(request)

            if not token:
                return jsonify({
                    'error': 'Authentication required',
                    'code': 'NO_TOKEN'
                }), 401

            user = self.get_user_from_token(token)

            if not user:
                return jsonify({
                    'error': 'Invalid or expired token',
                    'code': 'INVALID_TOKEN'
                }), 401

            # Store user context
            g.user_id = user['id']
            g.email = user['email']
            g.stripe_customer_id = user.get('stripe_customer_id')
            g.subscription_status = user.get('subscription_status', 'inactive')
            g.user = user

            # Check subscription status
            subscription_status = user.get('subscription_status')

            if subscription_status not in ['active', 'trialing']:
                return jsonify({
                    'error': 'No active subscription',
                    'code': 'INACTIVE_SUBSCRIPTION',
                    'subscription_status': subscription_status,
                    'message': 'An active subscription is required to access this resource'
                }), 403

            logger.debug(f"Authenticated user with active subscription: {g.email}")

            # Call the actual route function
            return f(*args, **kwargs)

        return decorated_function

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Get current authenticated user from Flask g object

        Returns:
            User dict or None if not authenticated
        """
        return getattr(g, 'user', None)

    def get_current_user_id(self) -> Optional[str]:
        """
        Get current authenticated user ID from Flask g object

        Returns:
            User ID (UUID) or None if not authenticated
        """
        return getattr(g, 'user_id', None)

    def is_authenticated(self) -> bool:
        """
        Check if current request is authenticated

        Returns:
            True if authenticated, False otherwise
        """
        return hasattr(g, 'user_id') and g.user_id is not None


# Global instance
auth_manager = SupabaseAuthManager()
