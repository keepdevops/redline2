"""Supabase authentication service"""
import logging
from typing import Dict, Optional
from uuid import UUID
from datetime import datetime
from .supabase_config import supabase_client, supabase_admin

logger = logging.getLogger(__name__)


class SupabaseAuthService:
    """Service for managing Supabase authentication and user hours"""

    def register(self, email: str, password: str, name: str = None, company: str = None) -> Dict:
        """
        Register new user with Supabase Auth

        Args:
            email: User email address
            password: User password
            name: User's full name (optional)
            company: User's company (optional)

        Returns:
            Dict containing user_id, email, access_token, refresh_token
        """
        try:
            # Create auth user
            auth_response = supabase_client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {"name": name, "company": company}
                }
            })

            user_id = auth_response.user.id

            # Initialize hours in user_hours table
            supabase_admin.table('user_hours').insert({
                'user_id': str(user_id),
                'email': email,
                'hours_remaining': 0.0,  # Start with 0, buy hours via Stripe
                'total_hours_purchased': 0.0,
                'total_hours_used': 0.0
            }).execute()

            logger.info(f"User registered: {email} ({user_id})")

            return {
                'user_id': str(user_id),
                'email': email,
                'access_token': auth_response.session.access_token,
                'refresh_token': auth_response.session.refresh_token
            }
        except Exception as e:
            logger.error(f"Registration failed for {email}: {str(e)}")
            raise

    def login(self, email: str, password: str) -> Dict:
        """
        Login user, returns JWT tokens

        Args:
            email: User email
            password: User password

        Returns:
            Dict containing user_id, email, access_token, refresh_token
        """
        try:
            auth_response = supabase_client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            logger.info(f"User logged in: {email}")

            return {
                'user_id': str(auth_response.user.id),
                'email': auth_response.user.email,
                'access_token': auth_response.session.access_token,
                'refresh_token': auth_response.session.refresh_token
            }
        except Exception as e:
            logger.error(f"Login failed for {email}: {str(e)}")
            raise

    def validate_jwt(self, token: str) -> Dict:
        """
        Validate JWT token, returns user info

        Args:
            token: JWT access token

        Returns:
            Dict containing user_id and email
        """
        try:
            user_response = supabase_client.auth.get_user(token)
            return {
                'user_id': str(user_response.user.id),
                'email': user_response.user.email
            }
        except Exception as e:
            logger.error(f"JWT validation failed: {str(e)}")
            raise

    def get_user_hours(self, user_id: str) -> float:
        """
        Get remaining hours for user

        Args:
            user_id: User UUID

        Returns:
            Hours remaining as float
        """
        try:
            result = supabase_admin.table('user_hours').select('hours_remaining').eq('user_id', str(user_id)).single().execute()
            return result.data.get('hours_remaining', 0.0)
        except Exception as e:
            logger.error(f"Failed to get hours for user {user_id}: {str(e)}")
            return 0.0

    def deduct_hours(self, user_id: str, hours: float) -> bool:
        """
        Deduct hours from user balance

        Args:
            user_id: User UUID
            hours: Hours to deduct

        Returns:
            True if successful
        """
        try:
            # Get current hours
            current = supabase_admin.table('user_hours').select('*').eq('user_id', str(user_id)).single().execute()
            new_remaining = max(0, current.data['hours_remaining'] - hours)
            new_used = current.data['total_hours_used'] + hours

            # Update hours
            supabase_admin.table('user_hours').update({
                'hours_remaining': new_remaining,
                'total_hours_used': new_used,
                'last_deduction_at': datetime.now().isoformat()
            }).eq('user_id', str(user_id)).execute()

            logger.debug(f"Deducted {hours} hours from user {user_id}. Remaining: {new_remaining}")

            return True
        except Exception as e:
            logger.error(f"Failed to deduct hours for user {user_id}: {str(e)}")
            return False

    def add_hours(self, user_id: str, hours: float) -> bool:
        """
        Add purchased hours to user balance

        Args:
            user_id: User UUID
            hours: Hours to add

        Returns:
            True if successful
        """
        try:
            current = supabase_admin.table('user_hours').select('*').eq('user_id', str(user_id)).single().execute()

            supabase_admin.table('user_hours').update({
                'hours_remaining': current.data['hours_remaining'] + hours,
                'total_hours_purchased': current.data['total_hours_purchased'] + hours
            }).eq('user_id', str(user_id)).execute()

            logger.info(f"Added {hours} hours to user {user_id}")

            return True
        except Exception as e:
            logger.error(f"Failed to add hours for user {user_id}: {str(e)}")
            return False


# Singleton instance
supabase_auth = SupabaseAuthService()
