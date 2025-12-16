#!/usr/bin/env python3
"""
Cloudflare DNS Setup Script for Render + redfindat.com
Adds DNS records programmatically using Cloudflare API
"""

import os
import sys
import json
from typing import Optional, Dict, Any

try:
    import requests
except ImportError:
    print("❌ Error: requests library is required")
    print("   Install with: pip install requests")
    sys.exit(1)

# Cloudflare API endpoints
CF_API_BASE = "https://api.cloudflare.com/client/v4"

class CloudflareDNS:
    def __init__(self, email: str, api_key: str, zone_id: Optional[str] = None):
        self.email = email
        self.api_key = api_key
        self.zone_id = zone_id
        self.headers = {
            "X-Auth-Email": email,
            "X-Auth-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def get_zone_id(self, domain: str) -> Optional[str]:
        """Get Zone ID for a domain"""
        url = f"{CF_API_BASE}/zones?name={domain}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("result"):
                zone_id = data["result"][0]["id"]
                print(f"✅ Found Zone ID for {domain}: {zone_id}")
                return zone_id
        
        print(f"❌ Could not find Zone ID for {domain}")
        return None
    
    def get_existing_record(self, name: str, record_type: str = "CNAME") -> Optional[Dict[str, Any]]:
        """Check if DNS record already exists"""
        if not self.zone_id:
            return None
        
        url = f"{CF_API_BASE}/zones/{self.zone_id}/dns_records"
        params = {"type": record_type, "name": name}
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("result") and len(data["result"]) > 0:
                return data["result"][0]
        
        return None
    
    def add_dns_record(
        self,
        name: str,
        target: str,
        record_type: str = "CNAME",
        proxied: bool = True,
        update_existing: bool = True
    ) -> bool:
        """Add or update DNS record"""
        if not self.zone_id:
            print("❌ Zone ID not set")
            return False
        
        # Check if record exists
        existing = self.get_existing_record(name, record_type)
        
        if existing:
            print(f"⚠️  Record {name} already exists")
            if not update_existing:
                print("   Skipping (use --update to force update)")
                return False
            
            # Update existing record
            record_id = existing["id"]
            url = f"{CF_API_BASE}/zones/{self.zone_id}/dns_records/{record_id}"
            data = {
                "type": record_type,
                "name": name,
                "content": target,
                "ttl": 1,  # Auto
                "proxied": proxied
            }
            response = requests.put(url, headers=self.headers, json=data)
        else:
            # Create new record
            url = f"{CF_API_BASE}/zones/{self.zone_id}/dns_records"
            data = {
                "type": record_type,
                "name": name,
                "content": target,
                "ttl": 1,  # Auto
                "proxied": proxied
            }
            response = requests.post(url, headers=self.headers, json=data)
        
        if response.status_code in [200, 201]:
            result = response.json()
            if result.get("success"):
                print(f"✅ Successfully {'updated' if existing else 'added'} {name}")
                return True
            else:
                errors = result.get("errors", [])
                for error in errors:
                    print(f"❌ Error: {error.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False


def main():
    """Main function"""
    print("☁️  Cloudflare DNS Setup for Render + redfindat.com")
    print("=" * 50)
    print()
    
    # Get credentials
    email = os.environ.get("CF_API_EMAIL")
    api_key = os.environ.get("CF_API_KEY")
    zone_id = os.environ.get("CF_ZONE_ID")
    
    if not email:
        email = input("Enter your Cloudflare email: ").strip()
    
    if not api_key:
        import getpass
        api_key = getpass.getpass("Enter your Cloudflare API key: ").strip()
    
    domain = "redfindat.com"
    
    # Initialize Cloudflare client
    cf = CloudflareDNS(email, api_key, zone_id)
    
    # Get Zone ID if not provided
    if not cf.zone_id:
        cf.zone_id = cf.get_zone_id(domain)
        if not cf.zone_id:
            print(f"\nPlease add {domain} to Cloudflare first or provide Zone ID manually")
            sys.exit(1)
    
    # Get Render URL
    render_url = input("Enter your Render service URL (e.g., redline-xxxx.onrender.com): ").strip()
    if not render_url:
        print("❌ Render URL is required!")
        sys.exit(1)
    
    # Remove protocol if present
    render_url = render_url.replace("https://", "").replace("http://", "").rstrip("/")
    
    print()
    print("✅ Configuration:")
    print(f"   Domain: {domain}")
    print(f"   Render URL: {render_url}")
    print(f"   Zone ID: {cf.zone_id}")
    print()
    
    # Add DNS records
    print("🚀 Adding DNS records...")
    print()
    
    records = [
        ("app", render_url, "CNAME", True),      # app.redfindat.com → Render
        ("@", render_url, "CNAME", True),        # redfindat.com → Render
        ("www", domain, "CNAME", True),          # www.redfindat.com → redfindat.com
    ]
    
    success_count = 0
    for name, target, record_type, proxied in records:
        if cf.add_dns_record(name, target, record_type, proxied):
            success_count += 1
        print()
    
    # Summary
    print("=" * 50)
    if success_count == len(records):
        print("✅ All DNS records added successfully!")
    else:
        print(f"⚠️  {success_count}/{len(records)} records added")
    
    print()
    print("Next steps:")
    print("  1. Wait 5-15 minutes for DNS propagation")
    print("  2. Configure SSL/TLS in Cloudflare Dashboard:")
    print(f"     https://dash.cloudflare.com → {domain} → SSL/TLS → Overview")
    print("     Set to: Full (strict)")
    print("  3. Test your setup:")
    print(f"     curl -I https://app.{domain}/health")
    print()
    print("Cloudflare Dashboard: https://dash.cloudflare.com")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

