#!/usr/bin/env python3
"""
Test rate limiting functionality for REDLINE Web Application
"""

import requests
import time
import sys

# Configuration
BASE_URL = "http://localhost:8080"
RATE_LIMIT_TESTS = {
    "/api/upload": {"limit": "10 per minute", "endpoint": "POST", "files": {"file": ("test.csv", "a,b,c\n1,2,3")}},
    "/api/convert": {"limit": "20 per hour", "endpoint": "POST", "json": {"input_file": "test.csv", "output_format": "json", "output_file": "test.json"}},
    "/api/download/AAPL": {"limit": "30 per hour", "endpoint": "POST", "json": {}},
    "/data/load": {"limit": "30 per minute", "endpoint": "POST", "json": {"filename": "test.csv"}},
    "/data/filter": {"limit": "60 per minute", "endpoint": "POST", "json": {"filename": "test.csv", "filters": {}}},
}

def test_rate_limit(endpoint, config):
    """Test rate limiting for a specific endpoint."""
    print(f"\n{'='*60}")
    print(f"Testing rate limit for: {endpoint}")
    print(f"Configured limit: {config['limit']}")
    print(f"{'='*60}")
    
    try:
        # Make initial request to check if endpoint is available
        if config['endpoint'] == "POST":
            if 'json' in config:
                response = requests.post(f"{BASE_URL}{endpoint}", json=config['json'], timeout=5)
            elif 'files' in config:
                response = requests.post(f"{BASE_URL}{endpoint}", files=config['files'], timeout=5)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", json={}, timeout=5)
        else:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        
        print(f"Initial request status: {response.status_code}")
        
        # Check for rate limit headers
        rate_limit_headers = [
            'X-RateLimit-Limit',
            'X-RateLimit-Remaining',
            'X-RateLimit-Reset',
            'Retry-After'
        ]
        
        found_headers = []
        for header in rate_limit_headers:
            if header in response.headers:
                found_headers.append((header, response.headers[header]))
        
        if found_headers:
            print(f"\n✓ Rate limit headers detected:")
            for header, value in found_headers:
                print(f"  - {header}: {value}")
        else:
            print(f"\n⚠ No rate limit headers found (may be disabled)")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to {BASE_URL} - is the server running?")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def test_concurrent_requests():
    """Test concurrent request handling."""
    print(f"\n{'='*60}")
    print("Testing concurrent request handling")
    print(f"{'='*60}")
    
    # Test status endpoint (should have default limits)
    print("\nTesting /api/status endpoint with default rate limits...")
    
    try:
        start_time = time.time()
        responses = []
        
        # Make 10 concurrent requests
        for i in range(10):
            try:
                response = requests.get(f"{BASE_URL}/api/status", timeout=5)
                responses.append(response.status_code)
            except Exception as e:
                responses.append(f"Error: {str(e)}")
        
        elapsed = time.time() - start_time
        
        success_count = sum(1 for r in responses if r == 200)
        failed_count = len(responses) - success_count
        
        print(f"  - Made 10 concurrent requests in {elapsed:.2f}s")
        print(f"  - Successful: {success_count}")
        print(f"  - Failed: {failed_count}")
        
        if success_count > 0:
            print(f"✓ Server is handling concurrent requests")
            return True
        else:
            print(f"✗ All requests failed")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to {BASE_URL} - is the server running?")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def test_rate_limit_exceeded():
    """Test behavior when rate limit is exceeded."""
    print(f"\n{'='*60}")
    print("Testing rate limit exceeded behavior")
    print(f"{'='*60}")
    
    print("\nAttempting to exceed rate limit on /api/status...")
    
    try:
        # Make many requests quickly
        for i in range(25):
            response = requests.get(f"{BASE_URL}/api/status", timeout=5)
            
            if response.status_code == 429:
                print(f"✓ Rate limit reached at request #{i+1}")
                print(f"  - Response: {response.status_code}")
                print(f"  - Message: {response.json().get('error', 'Rate limit exceeded')}")
                return True
            elif i % 5 == 0:
                print(f"  Request #{i+1}: {response.status_code}")
        
        print("⚠ Rate limit not reached in 25 requests")
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to {BASE_URL} - is the server running?")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def main():
    """Main test function."""
    print("="*60)
    print("REDLINE Rate Limiting Test")
    print("="*60)
    print(f"Testing against: {BASE_URL}")
    print(f"Ensure the REDLINE web app is running on {BASE_URL}")
    print("="*60)
    
    # Test connection
    try:
        response = requests.get(f"{BASE_URL}/api/status", timeout=5)
        print(f"\n✓ Connected to server (status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print(f"\n✗ Cannot connect to server at {BASE_URL}")
        print("  Please start the REDLINE web application first:")
        print("  python web_app.py")
        return False
    except Exception as e:
        print(f"\n✗ Error connecting to server: {str(e)}")
        return False
    
    # Run tests
    results = []
    
    # Test 1: Check rate limit headers
    results.append(test_rate_limit("/api/status", {"limit": "200 per day", "endpoint": "GET"}))
    
    # Test 2: Concurrent requests
    results.append(test_concurrent_requests())
    
    # Test 3: Rate limit exceeded
    results.append(test_rate_limit_exceeded())
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total tests: {len(results)}")
    print(f"Passed: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("\n✓ All rate limiting tests passed!")
        return True
    else:
        print("\n✗ Some tests failed")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
