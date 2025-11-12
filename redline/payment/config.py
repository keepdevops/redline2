#!/usr/bin/env python3
"""
REDLINE Payment Configuration
Stripe payment processing configuration and pricing
"""

import os
import logging

logger = logging.getLogger(__name__)

class PaymentConfig:
    """Payment configuration and pricing settings"""
    
    # Stripe Configuration
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', '')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')
    
    # Pricing Configuration (hours per dollar)
    # Default: 1 hour = $5, so 0.2 hours per dollar
    HOURS_PER_DOLLAR = float(os.environ.get('HOURS_PER_DOLLAR', '0.2'))
    
    # Predefined hour packages
    HOUR_PACKAGES = {
        'small': {'hours': 5, 'price': 25, 'name': '5 Hours Pack'},
        'medium': {'hours': 10, 'price': 45, 'name': '10 Hours Pack'},
        'large': {'hours': 20, 'price': 80, 'name': '20 Hours Pack'},
        'xlarge': {'hours': 50, 'price': 180, 'name': '50 Hours Pack'},
    }
    
    # Currency
    CURRENCY = os.environ.get('PAYMENT_CURRENCY', 'usd')
    
    # License server URL (for adding hours after payment)
    LICENSE_SERVER_URL = os.environ.get('LICENSE_SERVER_URL', 'http://localhost:5001')
    
    @classmethod
    def validate(cls):
        """Validate payment configuration"""
        errors = []
        
        if not cls.STRIPE_SECRET_KEY:
            errors.append("STRIPE_SECRET_KEY is not set")
        
        if not cls.STRIPE_PUBLISHABLE_KEY:
            errors.append("STRIPE_PUBLISHABLE_KEY is not set")
        
        if cls.HOURS_PER_DOLLAR <= 0:
            errors.append("HOURS_PER_DOLLAR must be greater than 0")
        
        if errors:
            logger.warning(f"Payment configuration issues: {', '.join(errors)}")
            return False
        
        return True
    
    @classmethod
    def calculate_hours_from_price(cls, price_dollars):
        """Calculate hours from price in dollars"""
        return price_dollars * cls.HOURS_PER_DOLLAR
    
    @classmethod
    def calculate_price_from_hours(cls, hours):
        """Calculate price in dollars from hours"""
        return hours / cls.HOURS_PER_DOLLAR
    
    @classmethod
    def get_package_info(cls, package_id):
        """Get information about a predefined package"""
        return cls.HOUR_PACKAGES.get(package_id)

