#!/usr/bin/env python3
"""
Supabase Authentication Manager for REDLINE
Handles JWT token validation and user authentication
Supports both HS256 (legacy) and ES256 (ECC P-256) algorithms
"""

from functools import wraps
from flask import request, jsonify, g
from redline.database.supabase_client import supabase_client
import jwt
import os
import logging
import time
import json
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Try to import PyJWKClient for ECC P-256 (ES256) support
try:
    from jwt import PyJWKClient
    JWKS_AVAILABLE = True
    logger.debug("PyJWKClient imported successfully for ECC P-256 (ES256) support")
except ImportError as e:
    JWKS_AVAILABLE = False
    PyJWKClient = None
    logger.warning(f"PyJWKClient not available: {str(e)}. Install cryptography>=43.0.0 for ECC P-256 support.")
except Exception as e:
    JWKS_AVAILABLE = False
    PyJWKClient = None
    logger.error(f"Unexpected error importing PyJWKClient: {str(e)}. ECC P-256 support will be limited.")


class SupabaseAuthManager:
    """Authenticate users via Supabase Auth JWT tokens"""

    def __init__(self):
        logger.debug("Initializing SupabaseAuthManager")
        
        # Load configuration from environment
        self.jwt_secret = os.environ.get('SUPABASE_JWT_SECRET')
        self.supabase_url = os.environ.get('SUPABASE_URL')
        self.jwks_client = None
        self.jwks_url = None
        self._jwks_cache_time = 0
        self._jwks_cache_ttl = 3600  # Cache JWKS for 1 hour

        # Validate and configure SUPABASE_URL
        if not self.supabase_url:
            logger.warning("SUPABASE_URL not configured. JWT verification may be limited.")
        else:
            # Validate URL format
            if not isinstance(self.supabase_url, str):
                logger.error(f"SUPABASE_URL must be a string, got {type(self.supabase_url)}")
                self.supabase_url = None
            elif not self.supabase_url.startswith(('http://', 'https://')):
                logger.error(f"SUPABASE_URL must start with http:// or https://, got: {self.supabase_url[:20]}...")
                self.supabase_url = None
            else:
                logger.debug(f"SUPABASE_URL configured: {self.supabase_url}")
                
                # Set up JWKS client for ECC P-256 (ES256) verification
                # Supabase uses: https://<project-id>.supabase.co/auth/v1/.well-known/jwks.json
                if self.supabase_url.endswith('/'):
                    self.jwks_url = f"{self.supabase_url}auth/v1/.well-known/jwks.json"
                    logger.debug(f"JWKS URL constructed (trailing slash): {self.jwks_url}")
                else:
                    self.jwks_url = f"{self.supabase_url}/auth/v1/.well-known/jwks.json"
                    logger.debug(f"JWKS URL constructed (no trailing slash): {self.jwks_url}")
                
                # Initialize JWKS client if available
                if JWKS_AVAILABLE:
                    try:
                        if not self.jwks_url:
                            raise ValueError("JWKS URL is not set")
                        self.jwks_client = PyJWKClient(self.jwks_url)
                        logger.info(f"JWKS client initialized successfully for ECC P-256 (ES256) verification: {self.jwks_url}")
                    except ValueError as e:
                        logger.error(f"Invalid JWKS URL configuration: {str(e)}")
                    except Exception as e:
                        logger.warning(f"Failed to initialize JWKS client: {str(e)}. Will try to fetch keys manually.")
                        logger.debug(f"JWKS client initialization error type: {type(e).__name__}")
                else:
                    logger.warning("PyJWKClient not available. Install cryptography>=43.0.0 for ECC P-256 support.")
                    logger.debug("Will attempt manual JWKS fetching if needed")

        # Validate and configure SUPABASE_JWT_SECRET (legacy HS256 support)
        if not self.jwt_secret:
            logger.info("SUPABASE_JWT_SECRET not configured. Using JWKS for ECC P-256 (ES256) verification.")
        else:
            # Validate secret format
            if not isinstance(self.jwt_secret, str):
                logger.error(f"SUPABASE_JWT_SECRET must be a string, got {type(self.jwt_secret)}")
                self.jwt_secret = None
            elif len(self.jwt_secret) < 10:
                logger.warning(f"SUPABASE_JWT_SECRET appears too short ({len(self.jwt_secret)} chars). May be invalid.")
            else:
                logger.info("SUPABASE_JWT_SECRET configured. Will support both HS256 (legacy) and ES256 (ECC P-256).")
                logger.debug(f"JWT secret length: {len(self.jwt_secret)} characters")

    def is_available(self) -> bool:
        """Check if auth manager is properly configured"""
        logger.debug("Checking if SupabaseAuthManager is available")
        
        # Check JWKS availability (for ES256)
        has_jwks = self.jwks_client is not None or self.jwks_url is not None
        if has_jwks:
            logger.debug("JWKS available for ECC P-256 (ES256) verification")
        else:
            logger.debug("JWKS not available")
        
        # Check JWT secret availability (for HS256 legacy)
        has_secret = bool(self.jwt_secret)
        if has_secret:
            logger.debug("JWT secret available for HS256 (legacy) verification")
        else:
            logger.debug("JWT secret not available")
        
        # Check Supabase URL
        has_url = bool(self.supabase_url)
        if has_url:
            logger.debug(f"Supabase URL configured: {self.supabase_url}")
        else:
            logger.debug("Supabase URL not configured")
        
        # Check Supabase client availability
        client_available = supabase_client.is_available()
        if client_available:
            logger.debug("Supabase client is available")
        else:
            logger.debug("Supabase client is not available")
        
        # Determine overall availability
        is_available = (has_jwks or has_secret) and has_url and client_available
        
        if is_available:
            logger.debug("SupabaseAuthManager is fully available")
        else:
            logger.warning("SupabaseAuthManager is not fully available - some features may be limited")
            if not has_jwks and not has_secret:
                logger.warning("Neither JWKS nor JWT secret is configured - JWT verification will fail")
            if not has_url:
                logger.warning("Supabase URL not configured")
            if not client_available:
                logger.warning("Supabase client not available")
        
        return is_available

    # ========================================================================
    # JWT TOKEN VALIDATION
    # ========================================================================

    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify Supabase JWT token
        Supports both ES256 (ECC P-256) via JWKS and HS256 (legacy) via JWT_SECRET

        Args:
            token: JWT token string

        Returns:
            Decoded token payload or None if invalid
        """
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

        # Decode header to determine algorithm
        try:
            header = jwt.get_unverified_header(token)
            if not isinstance(header, dict):
                logger.error(f"JWT header is not a dictionary, got {type(header)}")
                algorithm = 'HS256'  # Default fallback
            else:
                algorithm = header.get('alg', 'HS256')
                logger.debug(f"JWT header decoded successfully, algorithm: {algorithm}")
                if 'kid' in header:
                    logger.debug(f"JWT header contains key ID (kid): {header.get('kid')}")
        except jwt.DecodeError as e:
            logger.error(f"Failed to decode JWT header (DecodeError): {str(e)}")
            algorithm = 'HS256'  # Default fallback
        except Exception as e:
            logger.error(f"Failed to decode JWT header (unexpected error): {str(e)}, type: {type(e).__name__}")
            algorithm = 'HS256'  # Default fallback

        logger.debug(f"Attempting to verify JWT token with algorithm: {algorithm}")

        # Try ES256 (ECC P-256) first if JWKS is available
        if algorithm in ['ES256', 'ES384', 'ES512']:
            if self.jwks_client or self.jwks_url:
                logger.debug(f"Using JWKS for {algorithm} verification")
                result = self._verify_jwt_with_jwks(token, algorithm)
                if result:
                    logger.debug(f"Successfully verified JWT with {algorithm} via JWKS")
                else:
                    logger.warning(f"Failed to verify JWT with {algorithm} via JWKS")
                return result
            else:
                logger.error(f"Algorithm {algorithm} requires JWKS endpoint but none configured")
                logger.error("ES256/ES384/ES512 requires SUPABASE_URL to be set (for JWKS endpoint)")
                return None

        # Fallback to HS256 (legacy) if JWT_SECRET is provided
        if algorithm == 'HS256':
            if self.jwt_secret:
                logger.debug("Using JWT secret for HS256 verification")
                result = self._verify_jwt_with_secret(token)
                if result:
                    logger.debug("Successfully verified JWT with HS256 via secret")
                else:
                    logger.warning("Failed to verify JWT with HS256 via secret")
                return result
            else:
                logger.error("Algorithm HS256 requires SUPABASE_JWT_SECRET environment variable")
                return None

        # If algorithm doesn't match available methods
        logger.error(f"Cannot verify JWT: algorithm {algorithm} is not supported")
        logger.error(f"Supported algorithms: ES256/ES384/ES512 (via JWKS) or HS256 (via JWT_SECRET)")
        return None

    def _verify_jwt_with_jwks(self, token: str, algorithm: str = 'ES256') -> Optional[Dict[str, Any]]:
        """
        Verify JWT token using JWKS (for ECC P-256 / ES256)

        Args:
            token: JWT token string
            algorithm: Algorithm to use (ES256, ES384, ES512)

        Returns:
            Decoded token payload or None if invalid
        """
        try:
            # Use PyJWKClient if available
            if self.jwks_client:
                logger.debug("Using PyJWKClient for JWKS key retrieval")
                try:
                    signing_key = self.jwks_client.get_signing_key_from_jwt(token)
                    if not signing_key:
                        logger.error("PyJWKClient returned None signing key")
                        return None
                    logger.debug(f"Retrieved signing key from JWKS, key type: {type(signing_key.key)}")
                    
                    payload = jwt.decode(
                        token,
                        signing_key.key,
                        algorithms=[algorithm],
                        audience='authenticated',
                        options={"verify_signature": True, "verify_exp": True, "verify_aud": True}
                    )
                    logger.debug("JWT decoded successfully using PyJWKClient")
                except Exception as e:
                    logger.error(f"Error using PyJWKClient: {str(e)}, type: {type(e).__name__}")
                    raise
            else:
                # Fallback: fetch JWKS manually using PyJWT's ECAlgorithm
                logger.debug("PyJWKClient not available, fetching JWKS manually")
                try:
                    import requests
                except ImportError as e:
                    logger.error(f"requests library required for manual JWKS fetching: {str(e)}")
                    return None
                
                if not self.jwks_url:
                    logger.error("JWKS URL is not configured, cannot fetch keys manually")
                    return None
                
                logger.debug(f"Fetching JWKS from: {self.jwks_url}")
                try:
                    response = requests.get(self.jwks_url, timeout=5)
                    response.raise_for_status()
                    logger.debug(f"JWKS fetched successfully, status: {response.status_code}")
                except requests.exceptions.Timeout:
                    logger.error(f"Timeout fetching JWKS from {self.jwks_url}")
                    return None
                except requests.exceptions.RequestException as e:
                    logger.error(f"Error fetching JWKS: {str(e)}, type: {type(e).__name__}")
                    return None
                
                try:
                    jwks = response.json()
                    if not isinstance(jwks, dict):
                        logger.error(f"JWKS response is not a dictionary, got {type(jwks)}")
                        return None
                    logger.debug(f"JWKS parsed successfully, contains {len(jwks.get('keys', []))} keys")
                except ValueError as e:
                    logger.error(f"Failed to parse JWKS JSON: {str(e)}")
                    return None
                
                # Extract key ID from token header
                try:
                    header = jwt.get_unverified_header(token)
                    if not isinstance(header, dict):
                        logger.error(f"JWT header is not a dictionary, got {type(header)}")
                        return None
                    kid = header.get('kid')
                    if not kid:
                        logger.error("JWT header missing 'kid' (key ID) field")
                        return None
                    logger.debug(f"Extracted key ID from token header: {kid}")
                except Exception as e:
                    logger.error(f"Failed to extract key ID from token header: {str(e)}")
                    return None
                
                # Find matching key and convert JWK to ECC public key
                key = None
                keys_found = jwks.get('keys', [])
                if not keys_found:
                    logger.error("JWKS contains no keys")
                    return None
                
                logger.debug(f"Searching {len(keys_found)} keys for kid={kid}")
                for idx, jwk in enumerate(keys_found):
                    if not isinstance(jwk, dict):
                        logger.warning(f"JWK at index {idx} is not a dictionary, skipping")
                        continue
                    
                    jwk_kid = jwk.get('kid')
                    jwk_kty = jwk.get('kty')
                    
                    if jwk_kid == kid and jwk_kty == 'EC':
                        logger.debug(f"Found matching EC key at index {idx} with kid={kid}")
                        try:
                            # Use PyJWT's built-in JWK to key conversion
                            key = jwt.algorithms.ECAlgorithm.from_jwk(json.dumps(jwk))
                            logger.debug("Successfully converted JWK to ECC public key")
                            break
                        except ValueError as e:
                            logger.warning(f"Failed to convert JWK to key (ValueError): {str(e)}")
                            continue
                        except Exception as e:
                            logger.warning(f"Failed to convert JWK to key (unexpected error): {str(e)}, type: {type(e).__name__}")
                            continue
                
                if not key:
                    logger.error(f"JWK with kid={kid} not found in JWKS or failed to convert")
                    logger.debug(f"Searched {len(keys_found)} keys, none matched kid={kid} with kty=EC")
                    return None
                
                logger.debug("Decoding JWT with manually fetched key")
                payload = jwt.decode(
                    token,
                    key,
                    algorithms=[algorithm],
                    audience='authenticated',
                    options={"verify_signature": True, "verify_exp": True, "verify_aud": True}
                )
                logger.debug("JWT decoded successfully using manually fetched key")

            # Validate decoded payload
            if not payload:
                logger.error("JWT decode returned None payload")
                return None
            
            if not isinstance(payload, dict):
                logger.error(f"JWT decode returned invalid payload type: {type(payload)}, expected dict")
                return None
            
            logger.debug(f"JWT payload decoded successfully, contains {len(payload)} claims")

            # Validate required claims
            user_id = payload.get('sub')
            if not user_id:
                logger.error("JWT token missing 'sub' claim (user ID)")
                logger.debug(f"Available claims in payload: {list(payload.keys())}")
                return None
            
            if not isinstance(user_id, str):
                logger.error(f"JWT token 'sub' claim is not a string, got {type(user_id)}")
                return None
            
            logger.debug(f"JWT token verified successfully with {algorithm} for user: {user_id}")
            return payload

        except jwt.ExpiredSignatureError as e:
            logger.warning(f"JWT token has expired: {str(e)}")
            return None
        except jwt.InvalidAudienceError as e:
            logger.warning(f"JWT token has invalid audience: {str(e)}")
            logger.debug("Expected audience: 'authenticated'")
            return None
        except jwt.InvalidSignatureError as e:
            logger.warning(f"JWT token has invalid signature: {str(e)}")
            return None
        except jwt.DecodeError as e:
            logger.warning(f"JWT token decode error: {str(e)}")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"JWT token is invalid: {str(e)}")
            return None
        except KeyError as e:
            logger.error(f"Missing required key in JWT processing: {str(e)}")
            return None
        except ValueError as e:
            logger.error(f"Invalid value in JWT processing: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error verifying JWT with JWKS: {str(e)}, type: {type(e).__name__}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return None

    def _verify_jwt_with_secret(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token using symmetric secret (HS256 - legacy)

        Args:
            token: JWT token string

        Returns:
            Decoded token payload or None if invalid
        """
        if not self.jwt_secret:
            logger.error("Cannot verify JWT: SUPABASE_JWT_SECRET not set")
            return None
        
        if not isinstance(self.jwt_secret, str):
            logger.error(f"JWT secret must be a string, got {type(self.jwt_secret)}")
            return None
        
        if len(self.jwt_secret) < 10:
            logger.error(f"JWT secret appears too short ({len(self.jwt_secret)} chars)")
            return None

        logger.debug("Decoding JWT token with HS256 algorithm using secret")
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=['HS256'],
                audience='authenticated'
            )
            logger.debug("JWT decoded successfully with HS256")

            # Validate decoded payload
            if not payload:
                logger.error("JWT decode returned None payload")
                return None
            
            if not isinstance(payload, dict):
                logger.error(f"JWT decode returned invalid payload type: {type(payload)}, expected dict")
                return None
            
            logger.debug(f"JWT payload decoded successfully, contains {len(payload)} claims")

            # Validate required claims
            user_id = payload.get('sub')
            if not user_id:
                logger.error("JWT token missing 'sub' claim (user ID)")
                logger.debug(f"Available claims in payload: {list(payload.keys())}")
                return None
            
            if not isinstance(user_id, str):
                logger.error(f"JWT token 'sub' claim is not a string, got {type(user_id)}")
                return None

            logger.debug(f"JWT token verified successfully with HS256 for user: {user_id}")
            return payload

        except jwt.ExpiredSignatureError as e:
            logger.warning(f"JWT token has expired: {str(e)}")
            return None
        except jwt.InvalidAudienceError as e:
            logger.warning(f"JWT token has invalid audience: {str(e)}")
            logger.debug("Expected audience: 'authenticated'")
            return None
        except jwt.InvalidSignatureError as e:
            logger.warning(f"JWT token has invalid signature: {str(e)}")
            return None
        except jwt.DecodeError as e:
            logger.warning(f"JWT token decode error: {str(e)}")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"JWT token is invalid: {str(e)}")
            return None
        except KeyError as e:
            logger.error(f"Missing required key in JWT processing: {str(e)}")
            return None
        except ValueError as e:
            logger.error(f"Invalid value in JWT processing: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error verifying JWT with secret: {str(e)}, type: {type(e).__name__}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return None

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
            logger.debug(f"Available claims in payload: {list(payload.keys())}")
            return None
        
        if not isinstance(user_id, str):
            logger.error(f"User ID (sub claim) is not a string, got {type(user_id)}")
            return None

        logger.debug(f"JWT token contains user_id: {user_id}, email: {email or 'not provided'}")

        # Check if Supabase client is available
        if not supabase_client.is_available():
            logger.error("Cannot fetch user profile: Supabase client not available")
            return None
        
        if not hasattr(supabase_client, 'get_user_by_id'):
            logger.error("Supabase client missing get_user_by_id method")
            return None

        # Get full user profile from Supabase database
        logger.debug(f"Fetching full user profile from Supabase for user_id: {user_id}")
        try:
            user = supabase_client.get_user_by_id(user_id)
        except Exception as e:
            logger.error(f"Error fetching user from Supabase: {str(e)}, type: {type(e).__name__}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return None

        if not user:
            logger.warning(f"User {user_id} (email: {email or 'unknown'}) not found in Supabase database")
            return None

        # Validate user data structure
        if not isinstance(user, dict):
            logger.error(f"User profile returned unexpected type: {type(user)}, expected dict")
            return None

        if 'id' not in user:
            logger.error(f"User profile missing 'id' field for user {user_id}")
            logger.debug(f"Available fields in user profile: {list(user.keys())}")
            return None
        
        if user.get('id') != user_id:
            logger.warning(f"User profile ID mismatch: expected {user_id}, got {user.get('id')}")

        logger.debug(f"Successfully retrieved user profile for {email or 'unknown'} ({user_id})")
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
        if not request:
            logger.error("Cannot extract token: request object is None")
            return None
        
        logger.debug("Extracting JWT token from request")
        
        # Try Authorization header first (standard approach)
        try:
            auth_header = request.headers.get('Authorization')
            if auth_header:
                if not isinstance(auth_header, str):
                    logger.warning(f"Authorization header is not a string, got {type(auth_header)}")
                else:
                    # Support both "Bearer <token>" and just "<token>"
                    if auth_header.startswith('Bearer '):
                        token = auth_header[7:]  # Remove 'Bearer ' prefix
                        if token:
                            logger.debug("Token found in Authorization header (Bearer format)")
                            logger.debug(f"Token length: {len(token)} characters")
                            return token
                        else:
                            logger.warning("Authorization header has 'Bearer ' prefix but no token")
                    else:
                        logger.debug("Token found in Authorization header (no Bearer prefix)")
                        logger.debug(f"Token length: {len(auth_header)} characters")
                        return auth_header
        except AttributeError as e:
            logger.error(f"Request object missing headers attribute: {str(e)}")
        except Exception as e:
            logger.warning(f"Error reading Authorization header: {str(e)}")

        # Try cookie (Supabase Auth stores token here by default)
        try:
            token = request.cookies.get('sb-access-token')
            if token:
                if not isinstance(token, str):
                    logger.warning(f"Cookie token is not a string, got {type(token)}")
                else:
                    logger.debug("Token found in sb-access-token cookie")
                    logger.debug(f"Token length: {len(token)} characters")
                    return token
        except AttributeError as e:
            logger.error(f"Request object missing cookies attribute: {str(e)}")
        except Exception as e:
            logger.warning(f"Error reading sb-access-token cookie: {str(e)}")

        # Try alternative cookie name
        try:
            token = request.cookies.get('supabase-auth-token')
            if token:
                if not isinstance(token, str):
                    logger.warning(f"Cookie token is not a string, got {type(token)}")
                else:
                    logger.debug("Token found in supabase-auth-token cookie")
                    logger.debug(f"Token length: {len(token)} characters")
                    return token
        except Exception as e:
            logger.warning(f"Error reading supabase-auth-token cookie: {str(e)}")

        # Try custom header
        try:
            token = request.headers.get('X-Supabase-Token')
            if token:
                if not isinstance(token, str):
                    logger.warning(f"Header token is not a string, got {type(token)}")
                else:
                    logger.debug("Token found in X-Supabase-Token header")
                    logger.debug(f"Token length: {len(token)} characters")
                    return token
        except Exception as e:
            logger.warning(f"Error reading X-Supabase-Token header: {str(e)}")

        logger.debug("No token found in request (checked Authorization header, cookies, and X-Supabase-Token header)")
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
            logger.debug(f"require_auth decorator called for route: {f.__name__}")
            
            # Extract token
            try:
                token = self.extract_token_from_request(request)
            except Exception as e:
                logger.error(f"Error extracting token from request: {str(e)}, type: {type(e).__name__}")
                return jsonify({
                    'error': 'Authentication error',
                    'code': 'TOKEN_EXTRACTION_ERROR',
                    'message': 'Failed to extract authentication token from request'
                }), 500

            if not token:
                logger.warning("Authentication required but no token provided")
                return jsonify({
                    'error': 'Authentication required',
                    'code': 'NO_TOKEN',
                    'message': 'No authentication token provided'
                }), 401

            # Verify token and get user
            try:
                user = self.get_user_from_token(token)
            except Exception as e:
                logger.error(f"Error getting user from token: {str(e)}, type: {type(e).__name__}")
                import traceback
                logger.debug(f"Traceback: {traceback.format_exc()}")
                return jsonify({
                    'error': 'Authentication error',
                    'code': 'TOKEN_VERIFICATION_ERROR',
                    'message': 'Failed to verify authentication token'
                }), 500

            if not user:
                logger.warning("Token verification failed or user not found")
                return jsonify({
                    'error': 'Invalid or expired token',
                    'code': 'INVALID_TOKEN',
                    'message': 'The provided authentication token is invalid or has expired'
                }), 401

            # Validate user structure before storing
            if not isinstance(user, dict):
                logger.error(f"User object is not a dictionary, got {type(user)}")
                return jsonify({
                    'error': 'Authentication error',
                    'code': 'INVALID_USER_DATA',
                    'message': 'Invalid user data structure'
                }), 500

            if 'id' not in user:
                logger.error("User object missing 'id' field")
                return jsonify({
                    'error': 'Authentication error',
                    'code': 'INVALID_USER_DATA',
                    'message': 'User data missing required fields'
                }), 500

            if 'email' not in user:
                logger.warning("User object missing 'email' field")

            # Store user context in Flask g object
            try:
                g.user_id = user['id']
                g.email = user.get('email', 'unknown')
                g.stripe_customer_id = user.get('stripe_customer_id')
                g.subscription_status = user.get('subscription_status', 'inactive')
                g.user = user
            except Exception as e:
                logger.error(f"Error storing user context: {str(e)}, type: {type(e).__name__}")
                return jsonify({
                    'error': 'Authentication error',
                    'code': 'CONTEXT_STORAGE_ERROR',
                    'message': 'Failed to store user context'
                }), 500

            logger.debug(f"Authenticated user: {g.email} ({g.user_id})")

            # Call the actual route function
            try:
                return f(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in authenticated route {f.__name__}: {str(e)}, type: {type(e).__name__}")
                import traceback
                logger.debug(f"Traceback: {traceback.format_exc()}")
                raise

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
            logger.debug(f"require_active_subscription decorator called for route: {f.__name__}")
            
            # First require authentication
            try:
                token = self.extract_token_from_request(request)
            except Exception as e:
                logger.error(f"Error extracting token from request: {str(e)}, type: {type(e).__name__}")
                return jsonify({
                    'error': 'Authentication error',
                    'code': 'TOKEN_EXTRACTION_ERROR',
                    'message': 'Failed to extract authentication token from request'
                }), 500

            if not token:
                logger.warning("Active subscription required but no token provided")
                return jsonify({
                    'error': 'Authentication required',
                    'code': 'NO_TOKEN',
                    'message': 'No authentication token provided'
                }), 401

            try:
                user = self.get_user_from_token(token)
            except Exception as e:
                logger.error(f"Error getting user from token: {str(e)}, type: {type(e).__name__}")
                import traceback
                logger.debug(f"Traceback: {traceback.format_exc()}")
                return jsonify({
                    'error': 'Authentication error',
                    'code': 'TOKEN_VERIFICATION_ERROR',
                    'message': 'Failed to verify authentication token'
                }), 500

            if not user:
                logger.warning("Token verification failed or user not found")
                return jsonify({
                    'error': 'Invalid or expired token',
                    'code': 'INVALID_TOKEN',
                    'message': 'The provided authentication token is invalid or has expired'
                }), 401

            # Validate user structure
            if not isinstance(user, dict):
                logger.error(f"User object is not a dictionary, got {type(user)}")
                return jsonify({
                    'error': 'Authentication error',
                    'code': 'INVALID_USER_DATA',
                    'message': 'Invalid user data structure'
                }), 500

            if 'id' not in user:
                logger.error("User object missing 'id' field")
                return jsonify({
                    'error': 'Authentication error',
                    'code': 'INVALID_USER_DATA',
                    'message': 'User data missing required fields'
                }), 500

            # Store user context
            try:
                g.user_id = user['id']
                g.email = user.get('email', 'unknown')
                g.stripe_customer_id = user.get('stripe_customer_id')
                g.subscription_status = user.get('subscription_status', 'inactive')
                g.user = user
            except Exception as e:
                logger.error(f"Error storing user context: {str(e)}, type: {type(e).__name__}")
                return jsonify({
                    'error': 'Authentication error',
                    'code': 'CONTEXT_STORAGE_ERROR',
                    'message': 'Failed to store user context'
                }), 500

            # Check subscription status
            subscription_status = user.get('subscription_status')
            
            if not subscription_status:
                logger.warning(f"User {user.get('id')} has no subscription_status field")
                subscription_status = 'inactive'

            logger.debug(f"Checking subscription status for user {g.email}: {subscription_status}")

            if subscription_status not in ['active', 'trialing']:
                logger.warning(f"User {g.email} ({g.user_id}) attempted to access premium resource but subscription is {subscription_status}")
                return jsonify({
                    'error': 'No active subscription',
                    'code': 'INACTIVE_SUBSCRIPTION',
                    'subscription_status': subscription_status,
                    'message': 'An active subscription is required to access this resource'
                }), 403

            logger.debug(f"Authenticated user with active subscription: {g.email} (status: {subscription_status})")

            # Call the actual route function
            try:
                return f(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in subscription-protected route {f.__name__}: {str(e)}, type: {type(e).__name__}")
                import traceback
                logger.debug(f"Traceback: {traceback.format_exc()}")
                raise

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
        try:
            user = getattr(g, 'user', None)
            if user is None:
                logger.debug("No user found in Flask g object")
            elif not isinstance(user, dict):
                logger.warning(f"User in Flask g object is not a dictionary, got {type(user)}")
                return None
            else:
                logger.debug(f"Retrieved current user: {user.get('email', 'unknown')} ({user.get('id', 'unknown')})")
            return user
        except Exception as e:
            logger.error(f"Error getting current user from Flask g object: {str(e)}, type: {type(e).__name__}")
            return None

    def get_current_user_id(self) -> Optional[str]:
        """
        Get current authenticated user ID from Flask g object

        Returns:
            User ID (UUID) or None if not authenticated
        """
        try:
            user_id = getattr(g, 'user_id', None)
            if user_id is None:
                logger.debug("No user_id found in Flask g object")
            elif not isinstance(user_id, str):
                logger.warning(f"user_id in Flask g object is not a string, got {type(user_id)}")
                return None
            else:
                logger.debug(f"Retrieved current user_id: {user_id}")
            return user_id
        except Exception as e:
            logger.error(f"Error getting current user_id from Flask g object: {str(e)}, type: {type(e).__name__}")
            return None

    def is_authenticated(self) -> bool:
        """
        Check if current request is authenticated

        Returns:
            True if authenticated, False otherwise
        """
        try:
            has_user_id = hasattr(g, 'user_id')
            if has_user_id:
                user_id = g.user_id
                if user_id is None:
                    logger.debug("user_id exists in Flask g object but is None")
                    return False
                elif not isinstance(user_id, str):
                    logger.warning(f"user_id in Flask g object is not a string, got {type(user_id)}")
                    return False
                else:
                    logger.debug(f"User is authenticated: {user_id}")
                    return True
            else:
                logger.debug("user_id not found in Flask g object")
                return False
        except Exception as e:
            logger.error(f"Error checking authentication status: {str(e)}, type: {type(e).__name__}")
            return False


# Global instance
auth_manager = SupabaseAuthManager()
