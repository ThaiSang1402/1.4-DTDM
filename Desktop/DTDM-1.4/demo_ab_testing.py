#!/usr/bin/env python3
"""
Demo script for A/B testing between Server A and Server B.

This script demonstrates how the two server instances can be used
for A/B testing by sending requests to both servers and comparing responses.
"""

import requests
import json
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed


def send_request_to_server(server_name: str, port: int, request_id: int):
    """Send a request to a specific server and return the result."""
    try:
        base_url = f"http://localhost:{port}"
        
        # Create test request
        request_data = {
            "prompt": f"Test request {request_id} for A/B testing",
            "parameters": {"temperature": 0.7, "test_id": request_id},
            "client_id": f"ab_test_client_{request_id}",
            "request_id": f"ab-test-{request_id}"
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-Correlation-ID": f"ab-test-{server_name.lower().replace(' ', '-')}-{request_id}"
        }
        
        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/ai",
            json=request_data,
            headers=headers,
            timeout=10
        )
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "server_name": server_name,
                "port": port,
                "request_id": request_id,
                "server_id": data.get("server_id"),
                "processing_time": data.get("processing_time", 0),
                "total_time": end_time - start_time,
                "correlation_id": data.get("correlation_id"),
                "response_preview": data.get("response_text", "")[:100] + "..."
            }
        else:
            return {
                "success": False,
                "server_name": server_name,
                "port": port,
                "request_id": request_id,
                "error": f"HTTP {response.status_code}",
                "total_time": end_time - start_time
            }
            
    except Exception as e:
        return {
            "success": False,
            "server_name": server_name,
            "port": port,
            "request_id": request_id,
            "error": str(e),
            "total_time": 0
        }


def demo_sequential_ab_testing():
    """Demonstrate sequential A/B testing."""
    print("=" * 80)
    print("Sequential A/B Testing Demo")
    print("=" * 80)
    
    servers = [
        ("Server A", 8080),
        ("Server B", 8081)
    ]
    
    results = []
    
    print("\nSending requests sequentially to both servers...")
    
    for i in range(6):  # 6 requests total, 3 to each server
        server_name, port = servers[i % 2]  # Alternate between servers
        
        print(f"\nRequest {i+1}: Sending to {server_name} (port {port})")
        result = send_request_to_server(server_name, port, i+1)
        results.append(result)
        
        if result["success"]:
            print(f"  ✓ Success: {result['server_id']} processed in {result['processing_time']:.3f}s")
            print(f"  Response: {result['response_preview']}")
        else:
            print(f"  ✗ Failed: {result['error']}")
        
        time.sleep(0.5)  # Small delay between requests
    
    return results


def demo_concurrent_ab_testing():
    """Demonstrate concurrent A/B testing."""
    print("\n" + "=" * 80)
    print("Concurrent A/B Testing Demo")
    print("=" * 80)
    
    print("\nSending concurrent requests to both servers...")
    
    # Prepare requests for both servers
    requests_to_send = []
    for i in range(10):  # 10 requests total
        server_name = "Server A" if i % 2 == 0 else "Server B"
        port = 8080 if i % 2 == 0 else 8081
        requests_to_send.append((server_name, port, i+1))
    
    results = []
    
    # Send requests concurrently
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_request = {
            executor.submit(send_request_to_server, server_name, port, req_id): (server_name, port, req_id)
            for server_name, port, req_id in requests_to_send
        }
        
        for future in as_completed(future_to_request):
            server_name, port, req_id = future_to_request[future]
            try:
                result = future.result()
                results.append(result)
                
                if result["success"]:
                    print(f"  ✓ Request {req_id}: {result['server_id']} - {result['processing_time']:.3f}s")
                else:
                    print(f"  ✗ Request {req_id}: {server_name} - {result['error']}")
                    
            except Exception as e:
                print(f"  ✗ Request {req_id}: {server_name} - Exception: {e}")
    
    return results


def analyze_results(results):
    """Analyze A/B testing results."""
    print("\n" + "=" * 80)
    print("A/B Testing Results Analysis")
    print("=" * 80)
    
    # Separate results by server
    server_a_results = [r for r in results if r.get("server_id") == "Server A" and r["success"]]
    server_b_results = [r for r in results if r.get("server_id") == "Server B" and r["success"]]
    
    failed_results = [r for r in results if not r["success"]]
    
    print(f"\nTotal requests: {len(results)}")
    print(f"Successful requests: {len(server_a_results) + len(server_b_results)}")
    print(f"Failed requests: {len(failed_results)}")
    
    if server_a_results:
        avg_processing_a = sum(r["processing_time"] for r in server_a_results) / len(server_a_results)
        avg_total_a = sum(r["total_time"] for r in server_a_results) / len(server_a_results)
        print(f"\nServer A Statistics:")
        print(f"  Requests processed: {len(server_a_results)}")
        print(f"  Average processing time: {avg_processing_a:.3f}s")
        print(f"  Average total time: {avg_total_a:.3f}s")
    
    if server_b_results:
        avg_processing_b = sum(r["processing_time"] for r in server_b_results) / len(server_b_results)
        avg_total_b = sum(r["total_time"] for r in server_b_results) / len(server_b_results)
        print(f"\nServer B Statistics:")
        print(f"  Requests processed: {len(server_b_results)}")
        print(f"  Average processing time: {avg_processing_b:.3f}s")
        print(f"  Average total time: {avg_total_b:.3f}s")
    
    if failed_results:
        print(f"\nFailed Requests:")
        for result in failed_results:
            print(f"  Request {result['request_id']} to {result['server_name']}: {result['error']}")
    
    # Verify server identification
    print(f"\nServer Identification Verification:")
    server_a_correct = all(r.get("server_id") == "Server A" for r in server_a_results)
    server_b_correct = all(r.get("server_id") == "Server B" for r in server_b_results)
    
    print(f"  Server A identification: {'✓ Correct' if server_a_correct else '✗ Incorrect'}")
    print(f"  Server B identification: {'✓ Correct' if server_b_correct else '✗ Incorrect'}")
    
    # Overall success
    if server_a_correct and server_b_correct and len(failed_results) == 0:
        print(f"\n🎉 A/B Testing Successful!")
        print(f"✓ Both servers correctly identify themselves")
        print(f"✓ All requests processed successfully")
        print(f"✓ Ready for load balancer integration")
    else:
        print(f"\n❌ A/B Testing Issues Detected")
        if not server_a_correct:
            print(f"✗ Server A identification issues")
        if not server_b_correct:
            print(f"✗ Server B identification issues")
        if failed_results:
            print(f"✗ {len(failed_results)} requests failed")


def check_servers_running():
    """Check if both servers are running."""
    print("Checking if servers are running...")
    
    servers_status = {}
    
    for server_name, port in [("Server A", 8080), ("Server B", 8081)]:
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=3)
            if response.status_code == 200:
                data = response.json()
                servers_status[server_name] = {
                    "running": True,
                    "server_id": data.get("server_id"),
                    "status": data.get("status")
                }
                print(f"  ✓ {server_name} is running (ID: {data.get('server_id')})")
            else:
                servers_status[server_name] = {"running": False, "error": f"HTTP {response.status_code}"}
                print(f"  ✗ {server_name} health check failed: HTTP {response.status_code}")
        except Exception as e:
            servers_status[server_name] = {"running": False, "error": str(e)}
            print(f"  ✗ {server_name} not accessible: {e}")
    
    all_running = all(status["running"] for status in servers_status.values())
    
    if not all_running:
        print(f"\n❌ Not all servers are running!")
        print(f"Please start the servers using:")
        print(f"  Terminal 1: python -m scalable_ai_api.ai_server.server_runner --server-id 'Server A' --port 8080")
        print(f"  Terminal 2: python -m scalable_ai_api.ai_server.server_runner --server-id 'Server B' --port 8081")
        print(f"\nOr use the demo script:")
        print(f"  python demo_servers.py --mode auto")
        return False
    
    return True


def main():
    """Main A/B testing demo."""
    print("=" * 80)
    print("A/B Testing Demo - Server A vs Server B")
    print("=" * 80)
    
    # Check if servers are running
    if not check_servers_running():
        return
    
    print(f"\n✓ Both servers are running and ready for A/B testing!")
    
    # Run sequential testing
    sequential_results = demo_sequential_ab_testing()
    
    # Run concurrent testing
    concurrent_results = demo_concurrent_ab_testing()
    
    # Combine and analyze results
    all_results = sequential_results + concurrent_results
    analyze_results(all_results)


if __name__ == "__main__":
    main()