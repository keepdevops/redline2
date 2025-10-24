#!/usr/bin/env python3
"""
REDLINE Security Configuration Validator
Validates environment variables and security settings
"""

import os
import sys
import secrets
import logging
from typing import Dict, List, Optional

class SecurityValidator:
    """Validates security configuration for REDLINE application."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.errors = []
        self.warnings = []
    
    def validate_secret_key(self) -> bool:
        """Validate Flask SECRET_KEY configuration."""
        secret_key = os.environ.get('SECRET_KEY')
        
        if not secret_key:
            self.errors.append("SECRET_KEY environment variable is not set")
            return False
        
        if len(secret_key) < 32:
            self.warnings.append("SECRET_KEY should be at least 32 characters long")
        
        if secret_key in ['redline-secret-key-2024', 'test-secret-key', 'default-secret']:
            self.errors.append("SECRET_KEY is using a default/insecure value")
            return False
        
        return True
    
    def validate_cors_origins(self) -> bool:
        """Validate CORS origins configuration."""
        cors_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:8080,http://127.0.0.1:8080')
        origins = [origin.strip() for origin in cors_origins.split(',')]
        
        for origin in origins:
            if origin == '*':
                self.errors.append("CORS_ORIGINS contains wildcard '*' which is insecure")
                return False
            
            if not origin.startswith(('http://', 'https://')):
                self.errors.append(f"Invalid CORS origin format: {origin}")
                return False
        
        return True
    
    def validate_vnc_password(self) -> bool:
        """Validate VNC password configuration."""
        vnc_password = os.environ.get('VNC_PASSWORD')
        
        if not vnc_password:
            self.warnings.append("VNC_PASSWORD not set, will generate random password")
            return True
        
        if vnc_password == 'redline123':
            self.errors.append("VNC_PASSWORD is using default insecure value")
            return False
        
        if len(vnc_password) < 8:
            self.warnings.append("VNC_PASSWORD should be at least 8 characters long")
        
        return True
    
    def validate_api_keys(self) -> bool:
        """Validate API key configurations."""
        api_keys = {
            'ALPHA_VANTAGE_API_KEY': os.environ.get('ALPHA_VANTAGE_API_KEY'),
            'FINNHUB_API_KEY': os.environ.get('FINNHUB_API_KEY'),
            'IEX_CLOUD_API_KEY': os.environ.get('IEX_CLOUD_API_KEY')
        }
        
        valid_keys = 0
        for key_name, key_value in api_keys.items():
            if key_value:
                valid_keys += 1
                if len(key_value) < 10:
                    self.warnings.append(f"{key_name} appears to be too short")
            else:
                self.warnings.append(f"{key_name} not set - some data sources will be unavailable")
        
        if valid_keys == 0:
            self.warnings.append("No API keys configured - limited functionality available")
        
        return True
    
    def validate_file_permissions(self) -> bool:
        """Validate file permissions for sensitive files."""
        sensitive_files = [
            'data/api_keys.json',
            'data_config.ini',
            '.env'
        ]
        
        for file_path in sensitive_files:
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                mode = stat.st_mode
                
                # Check if file is readable by others
                if mode & 0o004:  # Other read permission
                    self.warnings.append(f"File {file_path} is readable by others")
                
                # Check if file is writable by others
                if mode & 0o002:  # Other write permission
                    self.errors.append(f"File {file_path} is writable by others")
        
        return True
    
    def validate_environment(self) -> bool:
        """Validate overall environment configuration."""
        flask_env = os.environ.get('FLASK_ENV', 'production')
        debug = os.environ.get('DEBUG', 'false').lower() == 'true'
        
        if flask_env == 'development' or debug:
            self.warnings.append("Running in development mode - not recommended for production")
        
        return True
    
    def generate_secure_config(self) -> Dict[str, str]:
        """Generate secure configuration values."""
        return {
            'SECRET_KEY': secrets.token_hex(32),
            'VNC_PASSWORD': secrets.token_urlsafe(32),
            'LICENSE_SECRET_KEY': secrets.token_hex(32),
            'CORS_ORIGINS': 'http://localhost:8080,http://127.0.0.1:8080'
        }
    
    def validate_all(self) -> bool:
        """Run all validation checks."""
        self.errors.clear()
        self.warnings.clear()
        
        checks = [
            self.validate_secret_key,
            self.validate_cors_origins,
            self.validate_vnc_password,
            self.validate_api_keys,
            self.validate_file_permissions,
            self.validate_environment
        ]
        
        all_passed = True
        for check in checks:
            if not check():
                all_passed = False
        
        return all_passed
    
    def print_report(self):
        """Print validation report."""
        print("🔒 REDLINE Security Configuration Report")
        print("=" * 50)
        
        if self.errors:
            print("\n❌ ERRORS (Must Fix):")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS (Recommended to Fix):")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ All security checks passed!")
        
        print("\n" + "=" * 50)
    
    def suggest_fixes(self):
        """Suggest fixes for security issues."""
        if self.errors or self.warnings:
            print("\n🔧 Suggested Fixes:")
            print("=" * 30)
            
            secure_config = self.generate_secure_config()
            
            print("\n1. Set secure environment variables:")
            print("   export SECRET_KEY='" + secure_config['SECRET_KEY'] + "'")
            print("   export VNC_PASSWORD='" + secure_config['VNC_PASSWORD'] + "'")
            print("   export CORS_ORIGINS='" + secure_config['CORS_ORIGINS'] + "'")
            
            print("\n2. Create .env file with secure values:")
            print("   cp env.template .env")
            print("   # Edit .env with secure values")
            
            print("\n3. Set proper file permissions:")
            print("   chmod 600 .env data/api_keys.json data_config.ini")
            
            print("\n4. For production deployment:")
            print("   export FLASK_ENV=production")
            print("   export DEBUG=false")

def main():
    """Main function for command-line usage."""
    validator = SecurityValidator()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--generate':
        # Generate secure configuration
        secure_config = validator.generate_secure_config()
        print("🔐 Generated Secure Configuration:")
        print("=" * 40)
        for key, value in secure_config.items():
            print(f"export {key}='{value}'")
        return
    
    # Run validation
    validator.validate_all()
    validator.print_report()
    validator.suggest_fixes()
    
    # Exit with error code if there are critical issues
    if validator.errors:
        sys.exit(1)

if __name__ == '__main__':
    main()
