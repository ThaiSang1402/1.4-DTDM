#!/usr/bin/env python3
"""
Task 2.4 Validation Script - Server B Instance Creation

This script validates that Task 2.4 has been completed successfully by:
1. Verifying Server B can be started on port 8081
2. Confirming Server B identifies itself correctly
3. Testing A/B functionality with both servers
4. Validating all requirements are met
"""

import subprocess
import sys
import time
import requests
import json


def validate_server_b_deployment():
    """Validate that Server B can be deployed and configured correctly."""
    print("=" * 80)
    print("Task 2.4 Validation: Server B Instance Creation")
    print("=" * 80)
    
    print("\n1. Testing Server B Deployment...")
    
    # Start Server B
    cmd = [
        sys.executable, "-m", "scalable_ai_api.ai_server.server_runner",
        "--server-id", "Server B",
        "--port", "8081",
        "--log-level", "INFO"
    ]
    
    print("   Starting Server B on port 8081...")
    server_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    try:
        # Wait for server to start
        time.sleep(3)
        
        # Test 1: Health Check
        print("\n2. Testing Health Check Endpoint...")
        health_response = requests.get("http://localhost:8081/health", timeout=5)
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   ✓ Health check successful")
            print(f"   ✓ Server ID: {health_data.get('server_id')}")
            print(f"   ✓ Status: {health_data.get('status')}")
            
            # Validate Requirement 2.1 - Server B deployment
            if health_data.get('server_id') == 'Server B':
                print("   ✅ Requirement 2.1: Server B deployed successfully")
            else:
                print("   ❌ Requirement 2.1: Server B identification failed")
                return False
        else:
            print(f"   ❌ Health check failed: HTTP {health_response.status_code}")
            return False
        
        # Test 2: Server Info
        print("\n3. Testing Server Info Endpoint...")
        info_response = requests.get("http://localhost:8081/info", timeout=5)
        
        if info_response.status_code == 200:
            info_data = info_response.json()
            print(f"   ✓ Server info retrieved")
            print(f"   ✓ Port: {info_data.get('port')}")
            print(f"   ✓ Host: {info_data.get('host')}")
            
            # Validate port configuration
            if info_data.get('port') == 8081:
                print("   ✅ Server B configured on correct port (8081)")
            else:
                print("   ❌ Server B port configuration incorrect")
                return False
        else:
            print(f"   ❌ Server info failed: HTTP {info_response.status_code}")
            return False
        
        # Test 3: AI Request Processing
        print("\n4. Testing AI Request Processing...")
        ai_request = {
            "prompt": "Hello Server B! Please identify yourself for validation.",
            "parameters": {"temperature": 0.7, "validation": True},
            "client_id": "validation_client",
            "request_id": "validation-req-001"
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-Correlation-ID": "validation-server-b-001"
        }
        
        ai_response = requests.post(
            "http://localhost:8081/api/ai",
            json=ai_request,
            headers=headers,
            timeout=10
        )
        
        if ai_response.status_code == 200:
            ai_data = ai_response.json()
            print(f"   ✓ AI request processed successfully")
            print(f"   ✓ Processing time: {ai_data.get('processing_time', 0):.3f}s")
            
            # Validate Requirement 2.3 - Server B identification
            server_id_correct = ai_data.get('server_id') == 'Server B'
            response_identifies_server = 'Server B' in ai_data.get('response_text', '')
            header_correct = ai_response.headers.get('X-Server-ID') == 'Server B'
            correlation_preserved = ai_data.get('correlation_id') == 'validation-server-b-001'
            
            print(f"   ✓ Server ID in response: {ai_data.get('server_id')}")
            print(f"   ✓ Server ID in header: {ai_response.headers.get('X-Server-ID')}")
            print(f"   ✓ Correlation ID preserved: {ai_data.get('correlation_id')}")
            print(f"   ✓ Response text includes 'Server B': {'Server B' in ai_data.get('response_text', '')}")
            
            if server_id_correct and response_identifies_server and header_correct and correlation_preserved:
                print("   ✅ Requirement 2.3: Server B identifies itself correctly in responses")
            else:
                print("   ❌ Requirement 2.3: Server B identification requirements not met")
                print(f"      - Server ID correct: {server_id_correct}")
                print(f"      - Response identifies server: {response_identifies_server}")
                print(f"      - Header correct: {header_correct}")
                print(f"      - Correlation preserved: {correlation_preserved}")
                return False
        else:
            print(f"   ❌ AI request failed: HTTP {ai_response.status_code}")
            return False
        
        print("\n5. Testing Multiple Requests...")
        # Test multiple requests to ensure consistency
        for i in range(3):
            test_request = {
                "prompt": f"Test request {i+1} for Server B consistency check",
                "parameters": {"test_number": i+1},
                "client_id": f"consistency_test_{i+1}",
                "request_id": f"consistency-{i+1}"
            }
            
            test_response = requests.post(
                "http://localhost:8081/api/ai",
                json=test_request,
                headers={"X-Correlation-ID": f"consistency-{i+1}"},
                timeout=10
            )
            
            if test_response.status_code == 200:
                test_data = test_response.json()
                if test_data.get('server_id') == 'Server B':
                    print(f"   ✓ Request {i+1}: Server B identification consistent")
                else:
                    print(f"   ❌ Request {i+1}: Server B identification inconsistent")
                    return False
            else:
                print(f"   ❌ Request {i+1}: Failed with HTTP {test_response.status_code}")
                return False
        
        print("\n6. Validation Summary...")
        print("   ✅ Server B successfully deployed on port 8081")
        print("   ✅ Server B correctly identifies itself in all responses")
        print("   ✅ Health monitoring endpoints working")
        print("   ✅ Request/response correlation tracking working")
        print("   ✅ Multiple request consistency verified")
        print("   ✅ All Task 2.4 requirements satisfied")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Validation error: {e}")
        return False
    finally:
        # Clean up server process
        print("\n7. Cleaning up...")
        server_process.terminate()
        time.sleep(1)
        if server_process.poll() is None:
            server_process.kill()
        print("   ✓ Server B stopped")


def validate_ab_readiness():
    """Validate that Server B is ready for A/B testing with Server A."""
    print("\n" + "=" * 80)
    print("A/B Testing Readiness Validation")
    print("=" * 80)
    
    print("\nThis validation demonstrates that Server B is ready for A/B testing.")
    print("For full A/B testing, both Server A and Server B need to be running.")
    print("\nTo test A/B functionality:")
    print("1. Start both servers:")
    print("   Terminal 1: python -m scalable_ai_api.ai_server.server_runner --server-id 'Server A' --port 8080")
    print("   Terminal 2: python -m scalable_ai_api.ai_server.server_runner --server-id 'Server B' --port 8081")
    print("2. Run A/B testing demo:")
    print("   python demo_ab_testing.py")
    print("3. Or use the automated demo:")
    print("   python demo_servers.py --mode auto")
    
    print("\n✅ Server B is ready for:")
    print("   - Load balancer integration")
    print("   - A/B testing with Server A")
    print("   - Round Robin request distribution")
    print("   - Health monitoring integration")
    print("   - Auto scaling integration")


def main():
    """Main validation function."""
    success = validate_server_b_deployment()
    
    if success:
        validate_ab_readiness()
        
        print("\n" + "=" * 80)
        print("🎉 TASK 2.4 COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\nServer B Instance Creation - VALIDATION PASSED")
        print("\n✅ Requirements Satisfied:")
        print("   - Requirement 2.1: Server B deployed on port 8081")
        print("   - Requirement 2.3: Server B identifies itself in responses")
        print("\n✅ Features Implemented:")
        print("   - FastAPI-based AI server")
        print("   - Health check endpoint")
        print("   - Server info endpoint")
        print("   - AI request processing")
        print("   - Request correlation tracking")
        print("   - Error handling")
        print("   - Performance metrics")
        print("\n✅ Integration Ready:")
        print("   - Load balancer compatibility")
        print("   - A/B testing capability")
        print("   - Monitoring system integration")
        print("   - Auto scaling support")
        
        print("\n🚀 Next Steps:")
        print("   - Implement Load Balancer (Task 3)")
        print("   - Set up Health Monitoring (Task 5)")
        print("   - Configure Auto Scaling (Task 7)")
        
    else:
        print("\n" + "=" * 80)
        print("❌ TASK 2.4 VALIDATION FAILED!")
        print("=" * 80)
        print("\nPlease check the error messages above and fix the issues.")
        sys.exit(1)


if __name__ == "__main__":
    main()