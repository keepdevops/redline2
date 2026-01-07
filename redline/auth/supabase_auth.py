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

        try:
            # Decode JWT token
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=['HS256'],
                audience='authenticated'
            )

            logger.debug(f"JWT token verified successfully for user: {payload.get('sub')}")
            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error verifying JWT token: {str(e)}")
            return None

    def get_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Get user info from JWT token and fetch full profile from Supabase

        Args:
            token: JWT token string

        Returns:
            User profile dict or None if token invalid or user not found
        """
        # Verify token
        payload = self.verify_jwt_token(token)
        if not payload:
            return None

        user_id = payload.get('sub')  # Supabase user ID (UUID)
        email = payload.get('email')

        if not user_id:
            logger.error("No user ID found in JWT token")
            return None

        # Get full user profile from Supabase
        try:
            user = supabase_client.get_user_by_id(user_id)

            if not user:
                logger.warning(f"User {user_id} not found in Supabase")
                return None

            logger.debug(f"Retrieved user profile for {email} ({user_id})")
            return user

        except Exception as e:
            logger.error(f"Error getting user from Supabase: {str(e)}")
            return None

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
