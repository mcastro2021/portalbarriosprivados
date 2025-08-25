#!/usr/bin/env python3
"""
Verification script to test deployment endpoints
"""

import requests
import json
import sys

def test_endpoint(url, endpoint, expected_status=200):
    """Test a specific endpoint"""
    try:
        full_url = f"{url}{endpoint}"
        print(f"🔍 Testing: {full_url}")
        
        response = requests.get(full_url, timeout=10)
        
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
        
        if response.headers.get('Content-Type', '').startswith('application/json'):
            try:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError:
                print(f"   Response: {response.text[:200]}...")
        else:
            print(f"   Response: {response.text[:200]}...")
        
        if response.status_code == expected_status:
            print("   ✅ PASS")
            return True
        else:
            print("   ❌ FAIL - Unexpected status code")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ FAIL - Request error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ FAIL - Unexpected error: {e}")
        return False

def main():
    """Main verification function"""
    base_url = "https://portalbarriosprivados.onrender.com"
    
    print("🚀 Starting deployment verification...")
    print(f"📍 Testing: {base_url}")
    print()
    
    # Test endpoints
    endpoints = [
        ("/", "Home page"),
        ("/health", "Health check"),
        ("/diagnostic", "Diagnostic info"),
        ("/auth/login", "Login endpoint (should return JSON error)"),
    ]
    
    results = []
    
    for endpoint, description in endpoints:
        print(f"📋 {description}")
        success = test_endpoint(base_url, endpoint)
        results.append((endpoint, success))
        print()
    
    # Summary
    print("📊 SUMMARY:")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for endpoint, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {endpoint}")
    
    print()
    print(f"Overall: {passed}/{total} endpoints working")
    
    if passed == total:
        print("🎉 All endpoints working correctly!")
        return True
    else:
        print("⚠️ Some endpoints failed - check the details above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
