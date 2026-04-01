#!/usr/bin/env python3
"""
Test script for Render deployment.

This script tests the deployed services on Render to ensure
they are working correctly.
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List


class RenderDeploymentTester:
    """Test deployed services on Render."""
    
    def __init__(self, base_urls: Dict[str, str]):
        """Initialize with service URLs.
        
        Args:
            base_urls: Dictionary mapping service names to their URLs
        """
        self.base_urls = base_urls
        self.session = requests.Session()
        self.session.timeout = 30
    
    def test_service_health(self, service_name: str) -> bool:
        """Test health endpoint of a service."""
        url = f"{self.base_urls[service_name]}/health"
        
        try:
            print(f"Testing {service_name} health: {url}")
            response = self.session.get(url)
            
            if response.status_code in [200, 503]:  # 503 is acceptable for health checks
                data = response.json()
                print(f"  ✓ Status: {data.get('status', 'unknown')}")
                print(f"  ✓ Message: {data.get('message', 'No message')}")
                return True
            else:
                print(f"  ✗ HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return False
    
    def test_ai_server(self, service_name: str, expected_server_id: str) -> bool:
        """Test AI server functionality."""
        url = f"{self.base_urls[service_name]}/api/ai"
        
        try:
            print(f"Testing {service_name} AI endpoint: {url}")
            
            request_data = {
                "prompt": f"Hello {expected_server_id}! Please identify yourself.",
                "parameters": {"temperature": 0.7},
                "client_id": "render_test_client",
                "request_id": f"render-test-{int(time.time())}"
            }
            
            headers = {
                "Content-Type": "application/json",
                "X-Correlation-ID": f"render-test-{service_name}-{int(time.time())}"
            }
            
            response = self.session.post(url, json=request_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                server_id = data.get("server_id", "")
                
                print(f"  ✓ Response received")
                print(f"  ✓ Server ID: {server_id}")
                print(f"  ✓ Processing time: {data.get('processing_time', 0):.3f}s")
                print(f"  ✓ Response preview: {data.get('response_text', '')[:100]}...")
                
                # Verify server identification
                if expected_server_id in server_id:
                    print(f"  ✓ Server identification correct")
                    return True
                else:
                    print(f"  ✗ Server identification incorrect: expected '{expected_server_id}', got '{server_id}'")
                    return False
            else:
                print(f"  ✗ HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return False
    
    def test_load_balancer_routing(self) -> bool:
        """Test load balancer Round Robin routing."""
        if "load_balancer" not in self.base_urls:
            print("Load balancer URL not provided, skipping routing test")
            return True
        
        url = f"{self.base_urls['load_balancer']}/api/ai"
        
        try:
            print(f"Testing Load Balancer Round Robin: {url}")
            
            server_responses = []
            
            # Send multiple requests to test Round Robin
            for i in range(6):  # 3 rounds of 2 servers
                request_data = {
                    "prompt": f"Round Robin test request {i+1}",
                    "parameters": {"test_round": i+1},
                    "client_id": "round_robin_test",
                    "request_id": f"rr-test-{i+1}"
                }
                
                headers = {
                    "Content-Type": "application/json",
                    "X-Correlation-ID": f"round-robin-test-{i+1}"
                }
                
                response = self.session.post(url, json=request_data, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    server_id = data.get("server_id", "unknown")
                    server_responses.append(server_id)
                    print(f"  Request {i+1}: Routed to {server_id}")
                else:
                    print(f"  Request {i+1}: Failed with HTTP {response.status_code}")
                    server_responses.append("ERROR")
                
                time.sleep(0.5)  # Small delay between requests
            
            # Analyze Round Robin pattern
            print(f"  Server routing pattern: {server_responses}")
            
            # Check if we got responses from both servers
            unique_servers = set(s for s in server_responses if s != "ERROR")
            if len(unique_servers) >= 2:
                print(f"  ✓ Round Robin working: {len(unique_servers)} different servers responded")
                return True
            else:
                print(f"  ✗ Round Robin not working: Only {len(unique_servers)} server(s) responded")
                return False
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return False
    
    def test_load_balancer_status(self) -> bool:
        """Test load balancer status endpoint."""
        if "load_balancer" not in self.base_urls:
            print("Load balancer URL not provided, skipping status test")
            return True
        
        url = f"{self.base_urls['load_balancer']}/status"
        
        try:
            print(f"Testing Load Balancer status: {url}")
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"  ✓ Load Balancer status: {data.get('load_balancer', {}).get('status', 'unknown')}")
                print(f"  ✓ Server count: {data.get('load_balancer', {}).get('server_count', 0)}")
                print(f"  ✓ Healthy servers: {data.get('load_balancer', {}).get('healthy_servers', 0)}")
                
                metrics = data.get('metrics', {})
                print(f"  ✓ Total requests: {metrics.get('total_requests', 0)}")
                print(f"  ✓ Error rate: {metrics.get('error_rate', 0):.2%}")
                
                servers = data.get('servers', [])
                for server in servers:
                    print(f"    - {server.get('id', 'unknown')}: {server.get('status', 'unknown')} ({server.get('request_count', 0)} requests)")
                
                return True
            else:
                print(f"  ✗ HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all deployment tests."""
        print("=" * 80)
        print("Render Deployment Test Suite")
        print("=" * 80)
        
        results = []
        
        # Test individual services
        for service_name, url in self.base_urls.items():
            print(f"\n{'='*20} Testing {service_name.upper()} {'='*20}")
            
            # Health check
            health_result = self.test_service_health(service_name)
            results.append((f"{service_name} health", health_result))
            
            # AI server specific tests
            if service_name in ["server_a", "server_b"]:
                expected_server_id = "Server A" if service_name == "server_a" else "Server B"
                ai_result = self.test_ai_server(service_name, expected_server_id)
                results.append((f"{service_name} AI", ai_result))
        
        # Load balancer specific tests
        if "load_balancer" in self.base_urls:
            print(f"\n{'='*20} Testing LOAD BALANCER ROUTING {'='*20}")
            
            routing_result = self.test_load_balancer_routing()
            results.append(("Load Balancer routing", routing_result))
            
            status_result = self.test_load_balancer_status()
            results.append(("Load Balancer status", status_result))
        
        # Summary
        print(f"\n{'='*80}")
        print("TEST RESULTS SUMMARY")
        print("=" * 80)
        
        passed = 0
        for test_name, result in results:
            status = "PASS" if result else "FAIL"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\nOverall: {passed}/{len(results)} tests passed")
        
        if passed == len(results):
            print("\n🎉 All tests passed! Render deployment is working correctly.")
            return True
        else:
            print(f"\n❌ {len(results) - passed} test(s) failed. Please check the deployment.")
            return False


def main():
    """Main test function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Render deployment")
    parser.add_argument("--load-balancer", help="Load Balancer URL")
    parser.add_argument("--server-a", help="Server A URL")
    parser.add_argument("--server-b", help="Server B URL")
    parser.add_argument("--config", help="JSON config file with URLs")
    
    args = parser.parse_args()
    
    # Get URLs from arguments or config file
    base_urls = {}
    
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
                base_urls = config.get("services", {})
        except Exception as e:
            print(f"Error reading config file: {e}")
            sys.exit(1)
    else:
        if args.load_balancer:
            base_urls["load_balancer"] = args.load_balancer.rstrip('/')
        if args.server_a:
            base_urls["server_a"] = args.server_a.rstrip('/')
        if args.server_b:
            base_urls["server_b"] = args.server_b.rstrip('/')
    
    if not base_urls:
        print("No service URLs provided. Use --load-balancer, --server-a, --server-b or --config")
        print("\nExample usage:")
        print("python test_render_deployment.py \\")
        print("  --load-balancer https://scalable-ai-api-load-balancer.onrender.com \\")
        print("  --server-a https://scalable-ai-api-server-a.onrender.com \\")
        print("  --server-b https://scalable-ai-api-server-b.onrender.com")
        sys.exit(1)
    
    print("Testing Render deployment with URLs:")
    for service, url in base_urls.items():
        print(f"  {service}: {url}")
    
    # Run tests
    tester = RenderDeploymentTester(base_urls)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()