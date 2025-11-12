#!/usr/bin/env python3
"""
Create a test license for Stripe payment testing
"""

import sys
import requests
import json
from datetime import datetime, timedelta

def create_test_license(license_server_url="http://localhost:5001", hours=0, customer_name="Test User"):
    """Create a test license"""
    
    print("🔑 Creating Test License")
    print("=" * 50)
    print(f"License Server: {license_server_url}")
    print(f"Initial Hours: {hours}")
    print(f"Customer: {customer_name}")
    print()
    
    # Create license
    try:
        response = requests.post(
            f"{license_server_url}/api/licenses",
            json={
                'name': customer_name,
                'email': 'test@example.com',
                'company': 'Test Company',
                'type': 'trial',
                'duration_days': 365,
                'hours': hours
            },
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            license_info = data.get('license', {})
            license_key = license_info.get('key')  # License key is in license.key, not license_key
            
            print("✅ License created successfully!")
            print()
            print("License Details:")
            print(f"  License Key: {license_key}")
            print(f"  Hours Remaining: {license_info.get('hours_remaining', 0)}")
            print(f"  Status: {license_info.get('status', 'unknown')}")
            print()
            print("Use this license key for payment testing:")
            print(f"  {license_key}")
            print()
            print("Test payment flow:")
            print(f"  1. Create checkout: POST /payments/create-checkout")
            print(f"     {{'license_key': '{license_key}', 'hours': 10}}")
            print(f"  2. Complete payment with test card")
            print(f"  3. Check balance: GET /payments/balance?license_key={license_key}")
            print()
            
            return license_key
        else:
            print(f"❌ Failed to create license: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to license server")
        print(f"   Make sure license server is running: python3 licensing/server/license_server.py")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def check_license_balance(license_key, license_server_url="http://localhost:5001"):
    """Check license balance"""
    try:
        response = requests.get(
            f"{license_server_url}/api/licenses/{license_key}/hours",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('hours_remaining', 0)
        else:
            print(f"Failed to check balance: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error checking balance: {str(e)}")
        return None

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Create a test license for payment testing")
    parser.add_argument("--server", default="http://localhost:5001",
                       help="License server URL (default: http://localhost:5001)")
    parser.add_argument("--hours", type=int, default=0,
                       help="Initial hours (default: 0 - to test purchase flow)")
    parser.add_argument("--name", default="Test User",
                       help="Customer name (default: Test User)")
    parser.add_argument("--check", metavar="LICENSE_KEY",
                       help="Check balance for existing license key")
    
    args = parser.parse_args()
    
    if args.check:
        print(f"Checking balance for license: {args.check}")
        balance = check_license_balance(args.check, args.server)
        if balance is not None:
            print(f"Hours remaining: {balance}")
        sys.exit(0)
    
    license_key = create_test_license(args.server, args.hours, args.name)
    
    if license_key:
        print("💡 Tip: Save this license key for testing:")
        print(f"   export TEST_LICENSE_KEY={license_key}")
        sys.exit(0)
    else:
        sys.exit(1)

