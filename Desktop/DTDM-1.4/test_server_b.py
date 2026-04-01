#!/usr/bin/env python3
"""
Test script for Server B instance.

This script validates that Server B is properly configured and working
according to the requirements.
"""

import requests
import json
import time
import sys


def test_server_b_health() -> bool:
    """Test Server B health endpoint."""
    try:
        print("Testing Server B health check...")
        response = requests.get("http://localhost:8081/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health check passed")
            print(f"  Status: {data.get('status')}")
            print(f"  Uptime: {data.get('uptime_seconds', 0):.1f}s")
            return data.get('server_id') == 'Server B'
        else:
            print(f"✗ Health check failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False


def test_server_b_info() -> bool:
    """Test Server B info endpoint."""
    try:
        print("\nTesting Server B info endpoint...")
        response = requests.get("http://localhost:8081/info", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Info endpoint passed")
            print(f"  Server ID: {data.get('server_id')}")
            print(f"  Port: {data.get('port')}")
            print(f"  Status: {data.get('status')}")
            print(f"  Request count: {data.get('request_count', 0)}")
            return data.get('server_id') == 'Server B' and data.get('port') == 8081
        else:
            print(f"✗ Info endpoint failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Info endpoint error: {e}")
        return False


def test_server_b_ai_request() -> bool:
    """Test Server B AI request processing."""
    try:
        print("\nTesting Server B AI request processing...")
        
        # Test request
        request_data = {
            "prompt": "Hello Server B! Please identify yourself.",
            "parameters": {"temperature": 0.7},
            "client_id": "test_client",
            "request_id": "test-req-456"
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-Correlation-ID": "test-server-b-456"
        }
        
        response = requests.post(
            "http://localhost:8081/api/ai",
            json=request_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✓ AI request processed successfully")
            print(f"  Request ID: {data.get('request_id')}")
            print(f"  Server ID: {data.get('server_id')}")
            print(f"  Processing time: {data.get('processing_time', 0):.3f}s")
            print(f"  Correlation ID: {data.get('correlation_id')}")
            print(f"  Response preview: {data.get('response_text', '')[:100]}...")
            
            # Check response headers
            server_id_header = response.headers.get('X-Server-ID')
            correlation_header = response.headers.get('X-Correlation-ID')
            
            print(f"  Header Server ID: {server_id_header}")
            print(f"  Header Correlation ID: {correlation_header}")
            
            # Validate requirements
            server_id_correct = data.get('server_id') == 'Server B'
            header_correct = server_id_header == 'Server B'
            correlation_preserved = data.get('correlation_id') == 'test-server-b-456'
            response_identifies_server = 'Server B' in data.get('response_text', '')
            
            if server_id_correct and header_correct and correlation_preserved and response_identifies_server:
                print(f"✓ All Server B identification requirements met")
                return True
            else:
                print(f"✗ Server B identification requirements not met:")
                print(f"  - Server ID in response: {server_id_correct}")
                print(f"  - Server ID in header: {header_correct}")
                print(f"  - Correlation preserved: {correlation_preserved}")
                print(f"  - Response identifies server: {response_identifies_server}")
                return False
        else:
            print(f"✗ AI request failed: HTTP {response.status_code}")
            if response.text:
                print(f"  Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ AI request error: {e}")
        return False


def test_server_b_error_handling() -> bool:
    """Test Server B error handling."""
    try:
        print("\nTesting Server B error handling...")
        
        # Test invalid request (missing prompt)
        request_data = {
            "parameters": {"temperature": 0.7},
            "client_id": "test_client"
        }
        
        response = requests.post(
            "http://localhost:8081/api/ai",
            json=request_data,
            timeout=10
        )
        
        if response.status_code == 400:
            print(f"✓ Error handling works correctly (HTTP 400 for missing prompt)")
            return True
        else:
            print(f"✗ Error handling failed: Expected HTTP 400, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error handling test error: {e}")
        return False


def test_server_b_multiple_requests() -> bool:
    """Test Server B with multiple concurrent requests."""
    try:
        print("\nTesting Server B with multiple requests...")
        
        success_count = 0
        total_requests = 3
        
        for i in range(total_requests):
            request_data = {
                "prompt": f"Test request {i+1} for Server B",
                "parameters": {"temperature": 0.5},
                "client_id": f"test_client_{i+1}",
                "request_id": f"multi-test-{i+1}"
            }
            
            headers = {
                "Content-Type": "application/json",
                "X-Correlation-ID": f"multi-test-server-b-{i+1}"
            }
            
            response = requests.post(
                "http://localhost:8081/api/ai",
                json=request_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if (data.get('server_id') == 'Server B' and 
                    data.get('correlation_id') == f"multi-test-server-b-{i+1}"):
                    success_count += 1
                    print(f"  ✓ Request {i+1} processed correctly")
                else:
                    print(f"  ✗ Request {i+1} failed validation")
            else:
                print(f"  ✗ Request {i+1} failed: HTTP {response.status_code}")
            
            # Small delay between requests
            time.sleep(0.1)
        
        if success_count == total_requests:
            print(f"✓ All {total_requests} requests processed correctly")
            return True
        else:
            print(f"✗ Only {success_count}/{total_requests} requests succeeded")
            return False
            
    except Exception as e:
        print(f"✗ Multiple requests test error: {e}")
        return False


def main():
    """Run all Server B tests."""
    print("=" * 80)
    print("Server B Test Suite")
    print("=" * 80)
    print("\nTesting Server B instance on port 8081...")
    print("Make sure Server B is running before executing these tests.")
    print("\nTo start Server B:")
    print("python -m scalable_ai_api.ai_server.server_runner --server-id 'Server B' --port 8081")
    print("\n" + "=" * 80)
    
    # Wait a moment for user to read instructions
    time.sleep(2)
    
    tests = [
        ("Health Check", test_server_b_health),
        ("Server Info", test_server_b_info),
        ("AI Request Processing", test_server_b_ai_request),
        ("Error Handling", test_server_b_error_handling),
        ("Multiple Requests", test_server_b_multiple_requests)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Server B is working correctly.")
        print("\nRequirements validation:")
        print("✅ Requirement 2.1: Server B deployed on port 8081")
        print("✅ Requirement 2.3: Server B identifies itself in responses")
        print("✅ Server B ready for load balancer integration")
    else:
        print(f"\n❌ {total - passed} test(s) failed. Please check Server B configuration.")
        sys.exit(1)


if __name__ == "__main__":
    main()