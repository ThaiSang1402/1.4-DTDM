#!/usr/bin/env python3
"""
Test script for Server A instance.

This script validates that Server A is properly configured and working
according to the requirements.
"""

import requests
import json
import time
import sys
from typing import Dict, Any


def test_server_a_health() -> bool:
    """Test Server A health endpoint."""
    try:
        print("Testing Server A health check...")
        response = requests.get("http://localhost:8080/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health check passed")
            print(f"  Server ID: {data.get('server_id')}")
            print(f"  Status: {data.get('status')}")
            print(f"  Uptime: {data.get('uptime_seconds', 0):.1f}s")
            return data.get('server_id') == 'Server A'
        else:
            print(f"✗ Health check failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False


def test_server_a_info() -> bool:
    """Test Server A info endpoint."""
    try:
        print("\nTesting Server A info endpoint...")
        response = requests.get("http://localhost:8080/info", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Info endpoint working")
            print(f"  Server ID: {data.get('server_id')}")
            print(f"  Port: {data.get('port')}")
            print(f"  Status: {data.get('status')}")
            print(f"  Request count: {data.get('request_count', 0)}")
            return data.get('server_id') == 'Server A' and data.get('port') == 8080
        else:
            print(f"✗ Info endpoint failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Info endpoint error: {e}")
        return False


def test_server_a_ai_request() -> bool:
    """Test Server A AI request processing."""
    try:
        print("\nTesting Server A AI request processing...")
        
        # Test request
        request_data = {
            "prompt": "Hello Server A! Please identify yourself.",
            "parameters": {"temperature": 0.7},
            "client_id": "test_client",
            "request_id": "test_request_001"
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-Correlation-ID": "test-server-a-123"
        }
        
        response = requests.post(
            "http://localhost:8080/api/ai",
            json=request_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            response_headers = dict(response.headers)
            
            print(f"✓ AI request processed successfully")
            print(f"  Server ID in response: {data.get('server_id')}")
            print(f"  Request ID: {data.get('request_id')}")
            print(f"  Correlation ID: {data.get('correlation_id')}")
            print(f"  Processing time: {data.get('processing_time', 0):.3f}s")
            print(f"  Response text: {data.get('response_text', '')[:100]}...")
            
            # Check response headers (case-insensitive)
            server_id_header = response_headers.get('X-Server-ID') or response_headers.get('x-server-id')
            correlation_header = response_headers.get('X-Correlation-ID') or response_headers.get('x-correlation-id')
            
            print(f"  X-Server-ID header: {server_id_header}")
            print(f"  X-Correlation-ID header: {correlation_header}")
            
            # Validate requirements
            server_id_correct = data.get('server_id') == 'Server A'
            header_correct = server_id_header == 'Server A'
            correlation_preserved = data.get('correlation_id') == 'test-server-a-123'
            response_identifies_server = 'Server A' in data.get('response_text', '')
            
            if server_id_correct and header_correct and correlation_preserved and response_identifies_server:
                print("✓ All Server A identification requirements met")
                return True
            else:
                print("✗ Server A identification requirements not fully met")
                print(f"  Server ID in response: {server_id_correct}")
                print(f"  Server ID in header: {header_correct}")
                print(f"  Correlation preserved: {correlation_preserved}")
                print(f"  Response identifies server: {response_identifies_server}")
                return False
        else:
            print(f"✗ AI request failed: HTTP {response.status_code}")
            if response.content:
                print(f"  Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ AI request error: {e}")
        return False


def test_multiple_requests() -> bool:
    """Test multiple requests to verify consistent Server A identification."""
    try:
        print("\nTesting multiple requests for consistency...")
        
        success_count = 0
        total_requests = 3
        
        for i in range(total_requests):
            request_data = {
                "prompt": f"Test request {i+1} to Server A",
                "parameters": {},
                "client_id": "test_client",
                "request_id": f"test_request_{i+1:03d}"
            }
            
            response = requests.post(
                "http://localhost:8080/api/ai",
                json=request_data,
                headers={"X-Correlation-ID": f"multi-test-{i+1}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('server_id') == 'Server A':
                    success_count += 1
                    print(f"  Request {i+1}: ✓ Server A identified correctly")
                else:
                    print(f"  Request {i+1}: ✗ Wrong server ID: {data.get('server_id')}")
            else:
                print(f"  Request {i+1}: ✗ Failed with HTTP {response.status_code}")
            
            time.sleep(0.1)  # Small delay between requests
        
        success_rate = success_count / total_requests
        print(f"Success rate: {success_count}/{total_requests} ({success_rate*100:.1f}%)")
        
        return success_rate == 1.0
        
    except Exception as e:
        print(f"✗ Multiple requests test error: {e}")
        return False


def main():
    """Main test function."""
    print("=" * 60)
    print("Server A Validation Test")
    print("=" * 60)
    print("\nThis test validates that Server A meets the requirements:")
    print("- Requirement 2.1: Server A is deployed and running on port 8080")
    print("- Requirement 2.2: Server A clearly identifies itself in responses")
    print()
    
    # Wait a moment for server to be ready
    print("Waiting for Server A to be ready...")
    time.sleep(2)
    
    # Run tests
    tests = [
        ("Health Check", test_server_a_health),
        ("Server Info", test_server_a_info),
        ("AI Request Processing", test_server_a_ai_request),
        ("Multiple Requests Consistency", test_multiple_requests)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 Server A is properly configured and meets all requirements!")
        print("\nServer A successfully:")
        print("✓ Runs on port 8080 as specified")
        print("✓ Identifies itself as 'Server A' in all responses")
        print("✓ Includes server identification in response headers")
        print("✓ Preserves request correlation IDs")
        print("✓ Provides health check and info endpoints")
        return True
    else:
        print(f"\n❌ Server A validation failed ({len(results)-passed} tests failed)")
        print("\nPlease check the server configuration and try again.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)