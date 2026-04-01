#!/usr/bin/env python3
"""
Quick validation script for Server B.

This script starts Server B, tests it briefly, and shuts it down.
"""

import subprocess
import sys
import time
import requests
import json
import signal
import os


def test_server_b_quick():
    """Quick test of Server B functionality."""
    print("Starting Server B for validation...")
    
    # Start Server B
    cmd = [
        sys.executable, "-m", "scalable_ai_api.ai_server.server_runner",
        "--server-id", "Server B",
        "--port", "8081",
        "--log-level", "INFO"
    ]
    
    server_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    try:
        # Wait for server to start
        print("Waiting for Server B to start...")
        time.sleep(3)
        
        # Test health check
        print("Testing health check...")
        health_response = requests.get("http://localhost:8081/health", timeout=5)
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✓ Health check passed")
            print(f"  Server ID: {health_data.get('server_id')}")
            print(f"  Status: {health_data.get('status')}")
            
            # Validate server identification
            if health_data.get('server_id') == 'Server B':
                print("✓ Server B correctly identifies itself")
            else:
                print("✗ Server B identification failed")
                return False
        else:
            print(f"✗ Health check failed: HTTP {health_response.status_code}")
            return False
        
        # Test AI request
        print("Testing AI request...")
        ai_request = {
            "prompt": "Hello Server B! Please identify yourself.",
            "parameters": {"temperature": 0.7},
            "client_id": "validation_client"
        }
        
        ai_response = requests.post(
            "http://localhost:8081/api/ai",
            json=ai_request,
            headers={"X-Correlation-ID": "validation-test-123"},
            timeout=10
        )
        
        if ai_response.status_code == 200:
            ai_data = ai_response.json()
            print(f"✓ AI request processed")
            print(f"  Server ID: {ai_data.get('server_id')}")
            print(f"  Response preview: {ai_data.get('response_text', '')[:100]}...")
            
            # Validate server identification in response
            server_id_correct = ai_data.get('server_id') == 'Server B'
            response_identifies_server = 'Server B' in ai_data.get('response_text', '')
            header_correct = ai_response.headers.get('X-Server-ID') == 'Server B'
            
            if server_id_correct and response_identifies_server and header_correct:
                print("✓ Server B correctly identifies itself in AI responses")
                print("✓ All validation tests passed!")
                return True
            else:
                print("✗ Server B identification in AI response failed")
                print(f"  - Server ID in response: {server_id_correct}")
                print(f"  - Response identifies server: {response_identifies_server}")
                print(f"  - Header correct: {header_correct}")
                return False
        else:
            print(f"✗ AI request failed: HTTP {ai_response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Validation error: {e}")
        return False
    finally:
        # Clean up server process
        print("Shutting down Server B...")
        server_process.terminate()
        time.sleep(1)
        if server_process.poll() is None:
            server_process.kill()
        print("Server B stopped.")


def main():
    """Run Server B validation."""
    print("=" * 60)
    print("Server B Validation")
    print("=" * 60)
    
    success = test_server_b_quick()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Server B validation PASSED!")
        print("\nServer B is ready for:")
        print("✓ Load balancer integration")
        print("✓ A/B testing with Server A")
        print("✓ Production deployment")
        print("\nRequirements satisfied:")
        print("✓ Requirement 2.1: Server B deployed on port 8081")
        print("✓ Requirement 2.3: Server B identifies itself in responses")
    else:
        print("❌ Server B validation FAILED!")
        print("Please check the server configuration and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()