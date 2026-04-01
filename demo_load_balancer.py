#!/usr/bin/env python3
"""
Demo script for Load Balancer functionality.

This script demonstrates the Load Balancer core class working with
the existing AI servers, showing Round Robin distribution and
health-aware routing.
"""

import time
import threading
from datetime import datetime

from scalable_ai_api.load_balancer.core import LoadBalancerCore
from scalable_ai_api.models import ServerInstance, AIRequest, ServerStatus


def demo_load_balancer():
    """Demonstrate Load Balancer functionality."""
    print("=== Load Balancer Demo ===\n")
    
    # Initialize Load Balancer
    print("1. Initializing Load Balancer...")
    lb = LoadBalancerCore(request_timeout=10, max_retries=2)
    print(f"   Load Balancer initialized with timeout={lb.request_timeout}s")
    
    # Create server instances (simulating existing AI servers)
    print("\n2. Creating server instances...")
    server_a = ServerInstance(
        id="server_a",
        ip_address="127.0.0.1",
        port=8080,
        status=ServerStatus.HEALTHY
    )
    
    server_b = ServerInstance(
        id="server_b", 
        ip_address="127.0.0.1",
        port=8081,
        status=ServerStatus.HEALTHY
    )
    
    server_c = ServerInstance(
        id="server_c",
        ip_address="127.0.0.1",
        port=8082,
        status=ServerStatus.UNHEALTHY  # Simulate unhealthy server
    )
    
    print(f"   Created servers: {server_a.id}, {server_b.id}, {server_c.id}")
    
    # Add servers to load balancer
    print("\n3. Adding servers to Load Balancer...")
    lb.add_server(server_a)
    lb.add_server(server_b)
    lb.add_server(server_c)
    
    pool = lb.get_current_server_pool()
    print(f"   Server pool size: {len(pool)}")
    for server in pool:
        print(f"   - {server.id}: {server.status.value} ({server.ip_address}:{server.port})")
    
    # Check health status
    print("\n4. Checking Load Balancer health status...")
    health = lb.get_health_status()
    print(f"   Status: {health.status.value}")
    print(f"   Message: {health.message}")
    print(f"   Details: {health.details}")
    
    # Demonstrate Round Robin selection
    print("\n5. Demonstrating Round Robin selection...")
    healthy_servers = [s for s in pool if s.status == ServerStatus.HEALTHY]
    print(f"   Healthy servers: {[s.id for s in healthy_servers]}")
    
    selections = []
    for i in range(6):  # 3 full rounds
        try:
            server = lb._select_next_server(healthy_servers)
            selections.append(server.id)
            print(f"   Selection {i+1}: {server.id}")
        except Exception as e:
            print(f"   Selection {i+1}: Error - {e}")
    
    print(f"   Selection pattern: {selections}")
    
    # Test request routing (will fail since servers aren't actually running)
    print("\n6. Testing request routing...")
    test_requests = [
        AIRequest(request_id="req_1", prompt="Hello from request 1"),
        AIRequest(request_id="req_2", prompt="Hello from request 2"),
        AIRequest(request_id="req_3", prompt="Hello from request 3"),
    ]
    
    for request in test_requests:
        print(f"   Routing request {request.request_id}...")
        try:
            response = lb.route_request(request)
            if response.error_message:
                print(f"     Error: {response.error_message}")
            else:
                print(f"     Success: Routed to {response.server_id}")
        except Exception as e:
            print(f"     Exception: {e}")
    
    # Show metrics
    print("\n7. Load Balancer metrics...")
    metrics = lb.get_metrics()
    print(f"   Total requests: {metrics.total_requests}")
    print(f"   Error rate: {metrics.error_rate:.2%}")
    print(f"   Average response time: {metrics.average_response_time:.3f}s")
    print(f"   Server distribution: {metrics.server_distribution}")
    
    # Test server removal
    print("\n8. Testing server removal...")
    print(f"   Removing {server_c.id}...")
    removed = lb.remove_server(server_c.id)
    print(f"   Removal successful: {removed}")
    
    pool = lb.get_current_server_pool()
    print(f"   Updated pool size: {len(pool)}")
    print(f"   Remaining servers: {[s.id for s in pool]}")
    
    # Test with no healthy servers
    print("\n9. Testing with no healthy servers...")
    server_a.status = ServerStatus.UNHEALTHY
    server_b.status = ServerStatus.UNHEALTHY
    
    health = lb.get_health_status()
    print(f"   Health status: {health.status.value}")
    print(f"   Message: {health.message}")
    
    test_request = AIRequest(request_id="req_no_servers", prompt="Test with no healthy servers")
    response = lb.route_request(test_request)
    print(f"   Response: {response.error_message}")
    
    # Cleanup
    print("\n10. Shutting down Load Balancer...")
    lb.shutdown()
    print("    Shutdown complete")
    
    print("\n=== Demo Complete ===")


def demo_concurrent_requests():
    """Demonstrate concurrent request handling."""
    print("\n=== Concurrent Request Demo ===\n")
    
    lb = LoadBalancerCore()
    
    # Add healthy servers
    for i in range(3):
        server = ServerInstance(
            id=f"server_{i}",
            ip_address="127.0.0.1",
            port=8080 + i,
            status=ServerStatus.HEALTHY
        )
        lb.add_server(server)
    
    print(f"Added {len(lb.get_current_server_pool())} servers")
    
    # Function to simulate concurrent requests
    def make_requests(thread_id, num_requests):
        selections = []
        for i in range(num_requests):
            healthy_servers = [s for s in lb.get_current_server_pool() if s.status == ServerStatus.HEALTHY]
            if healthy_servers:
                try:
                    server = lb._select_next_server(healthy_servers)
                    selections.append(server.id)
                except Exception as e:
                    selections.append(f"Error: {e}")
            time.sleep(0.01)  # Small delay to simulate processing
        
        print(f"Thread {thread_id} selections: {selections}")
        return selections
    
    # Run concurrent requests
    print("Running concurrent requests from 3 threads...")
    threads = []
    results = []
    
    def thread_wrapper(thread_id, num_requests):
        result = make_requests(thread_id, num_requests)
        results.append((thread_id, result))
    
    for i in range(3):
        thread = threading.Thread(target=thread_wrapper, args=(i, 5))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    # Analyze results
    print("\nConcurrency test results:")
    all_selections = []
    for thread_id, selections in results:
        all_selections.extend(selections)
        print(f"  Thread {thread_id}: {selections}")
    
    # Count distribution
    from collections import Counter
    distribution = Counter(all_selections)
    print(f"\nOverall distribution: {dict(distribution)}")
    
    lb.shutdown()
    print("Concurrent demo complete")


if __name__ == "__main__":
    demo_load_balancer()
    demo_concurrent_requests()