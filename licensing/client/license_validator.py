#!/usr/bin/env python3
"""
REDLINE License Client
Client-side license validation and management
"""

import os
import json
import hashlib
import platform
import uuid
import requests
from datetime import datetime
from pathlib import Path

class LicenseValidator:
    def __init__(self, license_server_url=None, cache_file=None):
        self.license_server_url = license_server_url or os.environ.get(
            'LICENSE_SERVER_URL', 
            'http://localhost:5001/api'
        )
        self.cache_file = cache_file or os.path.expanduser('~/.redline/license_cache.json')
        self.machine_id = self._get_machine_id()
        self.cached_license = None
        self._load_cached_license()
    
    def _get_machine_id(self):
        """Generate a unique machine ID"""
        try:
            # Try to get MAC address
            mac = uuid.getnode()
            if mac != uuid.getnode():
                return str(mac)
        except:
            pass
        
        # Fallback to hostname + platform info
        hostname = platform.node()
        system = platform.system()
        machine = platform.machine()
        return hashlib.md5(f"{hostname}:{system}:{machine}".encode()).hexdigest()
    
    def _get_system_info(self):
        """Get system information"""
        return {
            'platform': platform.platform(),
            'system': platform.system(),
            'release': platform.release(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version()
        }
    
    def _load_cached_license(self):
        """Load cached license information"""
        try:
            cache_path = Path(self.cache_file)
            if cache_path.exists():
                with open(cache_path, 'r') as f:
                    data = json.load(f)
                    
                # Check if cache is still valid (not expired)
                if 'expires' in data and datetime.now() < datetime.fromisoformat(data['expires']):
                    self.cached_license = data
        except (json.JSONDecodeError, IOError, ValueError):
            pass
    
    def _save_cached_license(self, license_data):
        """Save license information to cache"""
        try:
            cache_path = Path(self.cache_file)
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(cache_path, 'w') as f:
                json.dump(license_data, f, indent=2)
        except IOError:
            pass
    
    def validate_license(self, license_key, force_online=False):
        """Validate a license key"""
        # Try cached license first if not forcing online check
        if not force_online and self.cached_license:
            if self.cached_license.get('key') == license_key:
                return {
                    'valid': True,
                    'license': self.cached_license,
                    'cached': True
                }
        
        # Online validation
        try:
            response = requests.post(
                f"{self.license_server_url}/licenses/{license_key}/validate",
                json={
                    'machine_id': self.machine_id
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result['valid']:
                    # Cache the license
                    license_data = result['license']
                    license_data['cached_at'] = datetime.now().isoformat()
                    self._save_cached_license(license_data)
                    self.cached_license = license_data
                    
                    # Register this installation
                    self._register_install(license_key)
                    
                    return {
                        'valid': True,
                        'license': license_data,
                        'cached': False
                    }
                else:
                    return {
                        'valid': False,
                        'error': result.get('error', 'License validation failed')
                    }
            else:
                return {
                    'valid': False,
                    'error': f'Server error: {response.status_code}'
                }
                
        except requests.exceptions.RequestException as e:
            # Fallback to cached license if available
            if self.cached_license and self.cached_license.get('key') == license_key:
                return {
                    'valid': True,
                    'license': self.cached_license,
                    'cached': True,
                    'warning': f'Using cached license (offline): {str(e)}'
                }
            
            return {
                'valid': False,
                'error': f'Network error: {str(e)}'
            }
    
    def _register_install(self, license_key):
        """Register this installation with the license server"""
        try:
            requests.post(
                f"{self.license_server_url}/licenses/{license_key}/install",
                json={
                    'machine_id': self.machine_id,
                    'system_info': self._get_system_info()
                },
                timeout=5
            )
        except requests.exceptions.RequestException:
            # Ignore registration errors
            pass
    
    def check_feature_access(self, feature_name):
        """Check if a feature is available for the current license"""
        if not self.cached_license:
            return False
        
        features = self.cached_license.get('features', [])
        return feature_name in features
    
    def get_license_info(self):
        """Get current license information"""
        return self.cached_license
    
    def clear_cache(self):
        """Clear cached license information"""
        try:
            cache_path = Path(self.cache_file)
            if cache_path.exists():
                cache_path.unlink()
            self.cached_license = None
        except IOError:
            pass
    
    def check_updates(self):
        """Check for software updates"""
        try:
            current_version = "1.0.0"  # This would come from __version__.py
            
            response = requests.get(
                f"{self.license_server_url}/updates/check",
                params={'version': current_version},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'Server error: {response.status_code}'}
                
        except requests.exceptions.RequestException as e:
            return {'error': f'Network error: {str(e)}'}

# Convenience functions for easy integration
def validate_license_key(license_key, server_url=None):
    """Simple function to validate a license key"""
    validator = LicenseValidator(license_server_url=server_url)
    return validator.validate_license(license_key)

def check_feature(feature_name, server_url=None):
    """Simple function to check feature access"""
    validator = LicenseValidator(license_server_url=server_url)
    return validator.check_feature_access(feature_name)

def get_license_info(server_url=None):
    """Simple function to get license information"""
    validator = LicenseValidator(license_server_url=server_url)
    return validator.get_license_info()

if __name__ == '__main__':
    # Test the license validator
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python license_validator.py <license_key>")
        sys.exit(1)
    
    license_key = sys.argv[1]
    
    print(f"🔍 Validating license: {license_key}")
    print(f"🖥️  Machine ID: {LicenseValidator().machine_id}")
    
    result = validate_license_key(license_key)
    
    if result['valid']:
        print("✅ License is valid!")
        print(f"📋 License type: {result['license']['type']}")
        print(f"🎯 Features: {', '.join(result['license']['features'])}")
        print(f"📅 Expires: {result['license']['expires']}")
        if result.get('cached'):
            print("💾 Using cached license")
    else:
        print(f"❌ License validation failed: {result['error']}")