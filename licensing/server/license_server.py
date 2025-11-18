#!/usr/bin/env python3
"""
REDLINE License Server
Flask-based license validation and activation server
"""

import os
import json
import hashlib
import hmac
import time
import secrets
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration
SECRET_KEY = os.environ.get('LICENSE_SECRET_KEY') or secrets.token_hex(32)
# Use hidden directory for license storage
try:
    from redline.utils.config_paths import get_licenses_file, ensure_config_dir
    LICENSE_DB_FILE = str(get_licenses_file())
    ensure_config_dir()
except ImportError:
    # Fallback if config_paths not available
    LICENSE_DB_FILE = os.path.expanduser('~/.redline/licenses.json')
    os.makedirs(os.path.dirname(LICENSE_DB_FILE), mode=0o700, exist_ok=True)

class LicenseManager:
    def __init__(self):
        self.licenses = self.load_licenses()
    
    def load_licenses(self):
        """Load licenses from file"""
        if os.path.exists(LICENSE_DB_FILE):
            try:
                with open(LICENSE_DB_FILE, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}
    
    def save_licenses(self):
        """Save licenses to file"""
        with open(LICENSE_DB_FILE, 'w') as f:
            json.dump(self.licenses, f, indent=2)
    
    def generate_license_key(self, customer_info):
        """Generate a license key for customer"""
        data = f"{customer_info['email']}:{customer_info['company']}:{int(time.time())}"
        signature = hmac.new(SECRET_KEY.encode(), data.encode(), hashlib.sha256).hexdigest()
        return f"RL-{signature[:8].upper()}-{signature[8:16].upper()}-{signature[16:24].upper()}"
    
    def create_license(self, customer_info, license_type='standard', duration_days=365, hours=None):
        """Create a new license"""
        license_key = self.generate_license_key(customer_info)
        
        license_data = {
            'key': license_key,
            'customer': customer_info,
            'type': license_type,
            'created': datetime.now().isoformat(),
            'expires': (datetime.now() + timedelta(days=duration_days)).isoformat(),
            'status': 'active',
            'features': self.get_features_for_type(license_type),
            'max_installs': self.get_max_installs_for_type(license_type),
            'installs': [],
            # Hours-based access fields
            'hours_remaining': hours if hours is not None else 0.0,
            'purchased_hours': hours if hours is not None else 0.0,
            'used_hours': 0.0,
            'last_usage_check': None
        }
        
        self.licenses[license_key] = license_data
        self.save_licenses()
        
        return license_data
    
    def get_features_for_type(self, license_type):
        """Get features for license type"""
        features = {
            'trial': ['basic_analysis', 'data_import'],
            'standard': ['basic_analysis', 'data_import', 'advanced_analysis', 'export'],
            'professional': ['basic_analysis', 'data_import', 'advanced_analysis', 'export', 'api_access', 'priority_support'],
            'enterprise': ['basic_analysis', 'data_import', 'advanced_analysis', 'export', 'api_access', 'priority_support', 'custom_integrations', 'unlimited_users']
        }
        return features.get(license_type, features['standard'])
    
    def get_max_installs_for_type(self, license_type):
        """Get max installs for license type"""
        limits = {
            'trial': 1,
            'standard': 3,
            'professional': 10,
            'enterprise': -1  # Unlimited
        }
        return limits.get(license_type, 3)
    
    def validate_license(self, license_key, machine_id=None):
        """Validate a license key"""
        if license_key not in self.licenses:
            return {'valid': False, 'error': 'Invalid license key'}
        
        license_data = self.licenses[license_key]
        
        # Check if license is active
        if license_data['status'] != 'active':
            return {'valid': False, 'error': 'License inactive'}
        
        # Check hours-based access (if hours_remaining field exists)
        if 'hours_remaining' in license_data:
            hours_remaining = license_data.get('hours_remaining', 0.0)
            if hours_remaining <= 0:
                return {'valid': False, 'error': 'No hours remaining'}
        
        # Check install limits
        if machine_id:
            max_installs = license_data['max_installs']
            if max_installs != -1 and len(license_data['installs']) >= max_installs:
                if machine_id not in [install['machine_id'] for install in license_data['installs']]:
                    return {'valid': False, 'error': 'Maximum installs exceeded'}
        
        result = {
            'valid': True,
            'license': {
                'key': license_key,
                'type': license_data['type'],
                'features': license_data['features'],
                'expires': license_data['expires'],
                'customer': license_data['customer']
            }
        }
        
        # Include hours information if available
        if 'hours_remaining' in license_data:
            result['license']['hours_remaining'] = license_data.get('hours_remaining', 0.0)
            result['license']['purchased_hours'] = license_data.get('purchased_hours', 0.0)
            result['license']['used_hours'] = license_data.get('used_hours', 0.0)
        
        return result
    
    def register_install(self, license_key, machine_id, system_info):
        """Register a new installation"""
        if license_key not in self.licenses:
            return {'success': False, 'error': 'Invalid license key'}
        
        license_data = self.licenses[license_key]
        
        # Check if already registered
        for install in license_data['installs']:
            if install['machine_id'] == machine_id:
                install['last_seen'] = datetime.now().isoformat()
                install['system_info'] = system_info
                self.save_licenses()
                return {'success': True, 'message': 'Installation updated'}
        
        # Add new installation
        install_data = {
            'machine_id': machine_id,
            'system_info': system_info,
            'installed': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat()
        }
        
        license_data['installs'].append(install_data)
        self.save_licenses()
        
        return {'success': True, 'message': 'Installation registered'}
    
    def add_hours(self, license_key, hours):
        """Add hours to a license (for purchasing time)"""
        if license_key not in self.licenses:
            return {'success': False, 'error': 'Invalid license key'}
        
        license_data = self.licenses[license_key]
        
        # Initialize hours fields if they don't exist
        if 'hours_remaining' not in license_data:
            license_data['hours_remaining'] = 0.0
            license_data['purchased_hours'] = 0.0
            license_data['used_hours'] = 0.0
        
        # Add hours
        license_data['hours_remaining'] = license_data.get('hours_remaining', 0.0) + hours
        license_data['purchased_hours'] = license_data.get('purchased_hours', 0.0) + hours
        
        self.save_licenses()
        
        return {
            'success': True,
            'hours_added': hours,
            'hours_remaining': license_data['hours_remaining'],
            'purchased_hours': license_data['purchased_hours']
        }
    
    def deduct_hours(self, license_key, hours):
        """Deduct hours from a license (for usage tracking)"""
        if license_key not in self.licenses:
            return {'success': False, 'error': 'Invalid license key'}
        
        license_data = self.licenses[license_key]
        
        # Initialize hours fields if they don't exist
        if 'hours_remaining' not in license_data:
            license_data['hours_remaining'] = 0.0
            license_data['purchased_hours'] = 0.0
            license_data['used_hours'] = 0.0
        
        current_hours = license_data.get('hours_remaining', 0.0)
        
        # Cap deduction at remaining hours to allow zeroing out
        # If trying to deduct more than available, deduct only what's available
        hours_to_deduct = min(hours, current_hours)
        
        if hours_to_deduct <= 0:
            # No hours to deduct (already at zero or negative)
            return {
                'success': True,
                'hours_deducted': 0.0,
                'hours_remaining': max(0.0, current_hours),  # Ensure non-negative
                'used_hours': license_data.get('used_hours', 0.0)
            }
        
        # Deduct hours (cap at remaining hours to allow zeroing out)
        license_data['hours_remaining'] = max(0.0, current_hours - hours_to_deduct)  # Ensure non-negative
        license_data['used_hours'] = license_data.get('used_hours', 0.0) + hours_to_deduct
        license_data['last_usage_check'] = datetime.now().isoformat()
        
        self.save_licenses()
        
        return {
            'success': True,
            'hours_deducted': hours_to_deduct,
            'hours_remaining': license_data['hours_remaining'],
            'used_hours': license_data['used_hours']
        }
    
    def get_hours_remaining(self, license_key):
        """Get remaining hours for a license"""
        if license_key not in self.licenses:
            return {'success': False, 'error': 'Invalid license key'}
        
        license_data = self.licenses[license_key]
        
        return {
            'success': True,
            'hours_remaining': license_data.get('hours_remaining', 0.0),
            'purchased_hours': license_data.get('purchased_hours', 0.0),
            'used_hours': license_data.get('used_hours', 0.0)
        }

# Initialize license manager
license_manager = LicenseManager()

@app.route('/api/licenses', methods=['POST'])
def create_license():
    """Create a new license"""
    try:
        data = request.get_json()
        
        required_fields = ['email', 'company', 'name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        license_data = license_manager.create_license(
            customer_info=data,
            license_type=data.get('type', 'standard'),
            duration_days=data.get('duration_days', 365)
        )
        
        return jsonify({
            'success': True,
            'license': license_data
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/licenses/<license_key>/validate', methods=['POST'])
def validate_license(license_key):
    """Validate a license key"""
    try:
        data = request.get_json() or {}
        machine_id = data.get('machine_id')
        
        result = license_manager.validate_license(license_key, machine_id)
        
        if result['valid']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/licenses/<license_key>/install', methods=['POST'])
def register_install(license_key):
    """Register a new installation"""
    try:
        data = request.get_json()
        
        if not data or 'machine_id' not in data:
            return jsonify({'error': 'Missing machine_id'}), 400
        
        result = license_manager.register_install(
            license_key,
            data['machine_id'],
            data.get('system_info', {})
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/licenses/<license_key>', methods=['GET'])
def get_license_info(license_key):
    """Get license information"""
    try:
        if license_key not in license_manager.licenses:
            return jsonify({'error': 'License not found'}), 404
        
        license_data = license_manager.licenses[license_key]
        
        # Remove sensitive information
        safe_data = {
            'key': license_data['key'],
            'type': license_data['type'],
            'status': license_data['status'],
            'expires': license_data['expires'],
            'features': license_data['features'],
            'max_installs': license_data['max_installs'],
            'install_count': len(license_data['installs'])
        }
        
        # Include hours information if available
        if 'hours_remaining' in license_data:
            safe_data['hours_remaining'] = license_data.get('hours_remaining', 0.0)
            safe_data['purchased_hours'] = license_data.get('purchased_hours', 0.0)
            safe_data['used_hours'] = license_data.get('used_hours', 0.0)
        
        return jsonify({'license': safe_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/licenses/<license_key>/hours', methods=['GET', 'POST'])
def manage_hours(license_key):
    """Get or add hours to a license"""
    try:
        if request.method == 'GET':
            result = license_manager.get_hours_remaining(license_key)
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 400
        
        elif request.method == 'POST':
            data = request.get_json() or {}
            hours = data.get('hours', 0)
            
            if hours <= 0:
                return jsonify({'error': 'Hours must be greater than 0'}), 400
            
            result = license_manager.add_hours(license_key, hours)
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/licenses/<license_key>/usage', methods=['POST'])
def track_usage(license_key):
    """Track usage and deduct hours"""
    try:
        data = request.get_json() or {}
        hours = data.get('hours', 0)
        
        if hours <= 0:
            return jsonify({'error': 'Hours must be greater than 0'}), 400
        
        result = license_manager.deduct_hours(license_key, hours)
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'licenses_count': len(license_manager.licenses)
    }), 200

@app.route('/api/updates/check', methods=['GET'])
def check_updates():
    """Check for software updates"""
    try:
        current_version = request.args.get('version', '1.0.0')
        
        # In a real implementation, this would check against a release API
        latest_version = "1.0.0"  # This would come from GitHub releases API
        
        update_available = current_version != latest_version
        
        return jsonify({
            'current_version': current_version,
            'latest_version': latest_version,
            'update_available': update_available,
            'download_url': f"https://github.com/keepdevops/redline2/releases/tag/v{latest_version}" if update_available else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting REDLINE License Server...")
    print(f"📊 Loaded {len(license_manager.licenses)} licenses")
    
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('LICENSE_SERVER_PORT', 5001)),
        debug=os.environ.get('DEBUG', 'false').lower() == 'true'
    )