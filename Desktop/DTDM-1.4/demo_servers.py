#!/usr/bin/env python3
"""
Demo script for running AI Server instances.

This script demonstrates how to run Server A and Server B instances
as specified in the requirements.
"""

import subprocess
import sys
import time
import requests
import json
from concurrent.futures import ThreadPoolExecutor


def start_server(server_id: str, port: int):
    """Start a server instance."""
    cmd = [
        sys.executable, "-m", "scalable_ai_api.ai_server.server_runner",
        "--server-id", server_id,
        "--port", str(port),
        "--log-level", "INFO"
    ]
    
    print(f"Starting {server_id} on port {port}...")
    print(f"Command: {' '.join(cmd)}")
    
    return subprocess.Popen(cmd)


def test_server(server_id: str, port: int):
    """Test a server instance."""
    base_url = f"http://localhost:{port}"
    
    try:
        # Test health check
        print(f"\n--- Testing {server_id} on port {port} ---")
        
        health_response = requests.get(f"{base_url}/health", timeout=5)
        print(f"Health check: {health_response.status_code}")
        print(f"Health data: {json.dumps(health_response.json(), indent=2)}")
        
        # Test server info
        info_response = requests.get(f"{base_url}/info", timeout=5)
        print(f"Server info: {json.dumps(info_response.json(), indent=2)}")
        
        # Test AI request
        ai_request = {
            "prompt": f"Hello from client! Please identify yourself.",
            "parameters": {"temperature": 0.7},
            "client_id": "demo_client"
        }
        
        ai_response = requests.post(
            f"{base_url}/api/ai", 
            json=ai_request,
            headers={"X-Correlation-ID": f"demo-{server_id.lower().replace(' ', '-')}-123"},
            timeout=10
        )
        
        print(f"AI Response: {json.dumps(ai_response.json(), indent=2)}")
        print(f"Response Headers: {dict(ai_response.headers)}")
        
        return True
        
    except Exception as e:
        print(f"Error testing {server_id}: {e}")
        return False


def demo_manual_testing():
    """Demonstrate manual testing of servers."""
    print("=" * 80)
    print("AI Server Demo - Manual Testing")
    print("=" * 80)
    
    print("\nThis demo shows how to:")
    print("1. Start Server A on port 8080")
    print("2. Start Server B on port 8081") 
    print("3. Test both servers independently")
    print("\nTo run the servers manually, use these commands:")
    print("\n# Terminal 1 - Start Server A:")
    print("python -m scalable_ai_api.ai_server.server_runner --server-id 'Server A' --port 8080")
    print("\n# Terminal 2 - Start Server B:")
    print("python -m scalable_ai_api.ai_server.server_runner --server-id 'Server B' --port 8081")
    
    print("\n# Test commands:")
    print("curl http://localhost:8080/health")
    print("curl http://localhost:8081/health")
    print("curl http://localhost:8080/info")
    print("curl http://localhost:8081/info")
    
    print('\ncurl -X POST http://localhost:8080/api/ai \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -H "X-Correlation-ID: test-123" \\')
    print('  -d \'{"prompt": "Hello Server A!", "client_id": "test"}\'')
    
    print('\ncurl -X POST http://localhost:8081/api/ai \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -H "X-Correlation-ID: test-456" \\')
    print('  -d \'{"prompt": "Hello Server B!", "client_id": "test"}\'')


def demo_automated_testing():
    """Demonstrate automated testing by starting servers and testing them."""
    print("\n" + "=" * 80)
    print("AI Server Demo - Automated Testing")
    print("=" * 80)
    
    print("\nStarting servers for automated testing...")
    
    # Start servers
    server_a = start_server("Server A", 8080)
    server_b = start_server("Server B", 8081)
    
    try:
        # Wait for servers to start
        print("Waiting for servers to start...")
        time.sleep(3)
        
        # Test both servers
        success_a = test_server("Server A", 8080)
        success_b = test_server("Server B", 8081)
        
        if success_a and success_b:
            print("\n🎉 Both servers are working correctly!")
            print("\nKey features demonstrated:")
            print("✓ Server identification in responses")
            print("✓ Health check endpoints")
            print("✓ Request/response correlation tracking")
            print("✓ Error handling and logging")
            print("✓ Server-specific responses")
        else:
            print("\n❌ Some servers failed testing")
            
    except KeyboardInterrupt:
        print("\nShutdown requested...")
    finally:
        # Clean up
        print("\nStopping servers...")
        server_a.terminate()
        server_b.terminate()
        
        # Wait for cleanup
        time.sleep(1)
        server_a.kill()
        server_b.kill()


def main():
    """Main demo function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Server Demo")
    parser.add_argument(
        "--mode",
        choices=["manual", "auto"],
        default="manual",
        help="Demo mode: manual (show commands) or auto (run servers)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "manual":
        demo_manual_testing()
    else:
        demo_automated_testing()


if __name__ == "__main__":
    main()