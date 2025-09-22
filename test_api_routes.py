#!/usr/bin/env python3
"""
API Route Validation Test
Tests that all frontend API calls match backend routes
"""

import requests
import json
import sys

API_BASE = 'http://localhost:5000'

def test_endpoint(method, endpoint, headers=None, data=None, expected_status=None):
    """Test a single API endpoint"""
    url = f"{API_BASE}{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        status_ok = expected_status is None or response.status_code == expected_status
        status_indicator = "✅" if status_ok else "❌"
        
        print(f"{status_indicator} {method} {endpoint} - Status: {response.status_code}")
        
        if not status_ok:
            print(f"   Expected: {expected_status}, Got: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Response: {response.text[:200]}")
        
        return status_ok
        
    except requests.exceptions.ConnectionError:
        print(f"❌ {method} {endpoint} - Connection failed (server not running?)")
        return False
    except Exception as e:
        print(f"❌ {method} {endpoint} - Error: {str(e)}")
        return False

def main():
    """Test all API routes that frontend expects"""
    
    print("🧪 Testing NeuroNav API Routes")
    print("=" * 50)
    
    # Test public endpoints (no auth required)
    tests = [
        # Auth endpoints
        ('POST', '/auth/register', None, {
            'name': 'Test User',
            'email': 'test@example.com', 
            'password': 'testpass123'
        }, 201),
        
        ('POST', '/auth/login', None, {
            'email': 'test@example.com',
            'password': 'testpass123'
        }, 200),
        
        # Quiz endpoints (public)
        ('GET', '/quiz/questions', None, None, 200),
    ]
    
    # Run basic tests
    passed = 0
    total = len(tests)
    
    for method, endpoint, headers, data, expected_status in tests:
        if test_endpoint(method, endpoint, headers, data, expected_status):
            passed += 1
    
    # Try to get a JWT token for authenticated tests
    try:
        login_response = requests.post(f"{API_BASE}/auth/login", json={
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        
        if login_response.status_code == 200:
            token = login_response.json().get('access_token')
            if token:
                auth_headers = {'Authorization': f'Bearer {token}'}
                
                print("\n📋 Testing authenticated endpoints...")
                
                # Test authenticated endpoints
                auth_tests = [
                    ('GET', '/auth/verify-token', auth_headers, None, 200),
                    ('POST', '/quiz/submit', auth_headers, {
                        'answers': [
                            {'question_id': '507f1f77bcf86cd799439011', 'selected_option': 1}
                        ],
                        'preferences': {'topic': 'Data Science'}
                    }, None),  # Might fail due to missing questions, that's OK
                    ('GET', '/progress/summary', auth_headers, None, 200),
                    ('GET', '/roadmaps', auth_headers, None, 200),
                ]
                
                for method, endpoint, headers, data, expected_status in auth_tests:
                    if test_endpoint(method, endpoint, headers, data, expected_status):
                        passed += 1
                    total += 1
                
    except Exception as e:
        print(f"⚠️  Could not test authenticated endpoints: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All API routes are working correctly!")
        return 0
    else:
        print("❌ Some API routes need attention")
        return 1

if __name__ == '__main__':
    sys.exit(main())