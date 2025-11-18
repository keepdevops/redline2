#!/usr/bin/env python3
"""
Payment routes registry for REDLINE Web GUI
Handles Stripe payment processing, checkout, and webhooks

This module now serves as a central registry for all payment blueprints.
Individual route modules are organized by functionality.
"""

from flask import Blueprint

# Import all payment blueprints
from .payments_checkout import payments_checkout_bp
from .payments_webhook import payments_webhook_bp
from .payments_balance import payments_balance_bp
from .payments_tab import payments_tab_bp

# Main payment blueprint - registers all sub-blueprints
payments_bp = Blueprint('payments', __name__)

# Add route aliases to maintain backward compatibility with templates
from flask import render_template

@payments_bp.route('/', endpoint='payment_tab')
def payment_tab():
    """Alias for payments_tab.payment_tab"""
    return render_template('payment_tab.html')

# Register all sub-blueprints with the main payment blueprint
# Use url_prefix to maintain route structure
payments_bp.register_blueprint(payments_checkout_bp, url_prefix='')
payments_bp.register_blueprint(payments_webhook_bp, url_prefix='')
payments_bp.register_blueprint(payments_balance_bp, url_prefix='')
payments_bp.register_blueprint(payments_tab_bp, url_prefix='')
