"""
Unit tests for Load Balancer core functionality.

Tests the Round Robin algorithm, server pool management, health tracking,
and request forwarding capabilities.
"""

import pytest
import time
import threading
import requests
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from scalable_ai_api.load_balancer.core import LoadBalancerCore
from scalable_ai_api.models import (
    ServerInstance, AIRequest, AIResponse, ServerStatus, RequestPriority
)


class TestLoadBalancerCore:
    """Test cases for LoadBalancerCore class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.load_balancer = LoadBalancerCore(request_timeout=5, max_retries=2)
        
        # Create test servers
        self.server_a = ServerInstance(
            id="server_a",
            ip_address="127.0.0.1",
            port=8080,
            status=ServerStatus.HEALTHY
        )
        
        self.server_b = ServerInstance(
            id="server_b", 
            ip_address="127.0.0.1",
            port=8081,
            status=ServerStatus.HEALTHY
        )
        
        self.server_c = ServerInstance(
            id="server_c",
            ip_address="127.0.0.1", 
            port=8082,
            status=ServerStatus.UNHEALTHY
        )
    
    def test_initialization(self):
        """Test load balancer initialization."""
        lb = LoadBalancerCore(request_timeout=10, max_retries=5)
        
        assert lb.request_timeout == 10
        assert lb.max_retries == 5
        assert lb.server_pool == []
        assert lb.last_server_index == -1
        assert lb.metrics.total_requests == 0
        assert lb.session is not None
    
    def test_add_server_success(self):
        """Test successful server addition."""
        result = self.load_balancer.add_server(self.server_a)
        
        assert result is True
        assert len(self.load_balancer.server_pool) == 1
        assert self.load_balancer.server_pool[0] == self.server_a
        assert "server_a" in self.load_balancer.metrics.server_distribution
    
    def test_add_duplicate_server(self):
        """Test adding duplicate server."""
        self.load_balancer.add_server(self.server_a)
        result = self.load_balancer.add_server(self.server_a)
        
        assert result is False
        assert len(self.load_balancer.server_pool) == 1
    
    def test_remove_server_success(self):
        """Test successful server removal."""
        self.load_balancer.add_server(self.server_a)
        self.load_balancer.add_server(self.server_b)
        
        result = self.load_balancer.remove_server("server_a")
        
        assert result is True
        assert len(self.load_balancer.server_pool) == 1
        assert self.load_balancer.server_pool[0] == self.server_b
        assert "server_a" not in self.load_balancer.metrics.server_distribution
    
    def test_remove_nonexistent_server(self):
        """Test removing non-existent server."""
        result = self.load_balancer.remove_server("nonexistent")
        
        assert result is False
        assert len(self.load_balancer.server_pool) == 0
    
    def test_get_current_server_pool(self):
        """Test getting current server pool."""
        self.load_balancer.add_server(self.server_a)
        self.load_balancer.add_server(self.server_b)
        
        pool = self.load_balancer.get_current_server_pool()
        
        assert len(pool) == 2
        assert pool[0] == self.server_a
        assert pool[1] == self.server_b
        
        # Verify it's a copy (modifying shouldn't affect original)
        pool.clear()
        assert len(self.load_balancer.server_pool) == 2
    
    def test_round_robin_selection_two_servers(self):
        """Test Round Robin selection with two servers."""
        self.load_balancer.add_server(self.server_a)
        self.load_balancer.add_server(self.server_b)
        
        healthy_servers = [self.server_a, self.server_b]
        
        # First selection should be server_a (index 0)
        server1 = self.load_balancer._select_next_server(healthy_servers)
        assert server1 == self.server_a
        assert self.load_balancer.last_server_index == 0
        
        # Second selection should be server_b (index 1)
        server2 = self.load_balancer._select_next_server(healthy_servers)
        assert server2 == self.server_b
        assert self.load_balancer.last_server_index == 1
        
        # Third selection should wrap around to server_a
        server3 = self.load_balancer._select_next_server(healthy_servers)
        assert server3 == self.server_a
        assert self.load_balancer.last_server_index == 0
    
    def test_round_robin_selection_single_server(self):
        """Test Round Robin selection with single server."""
        self.load_balancer.add_server(self.server_a)
        
        healthy_servers = [self.server_a]
        
        # Should always select the same server
        server1 = self.load_balancer._select_next_server(healthy_servers)
        server2 = self.load_balancer._select_next_server(healthy_servers)
        
        assert server1 == self.server_a
        assert server2 == self.server_a
    
    def test_round_robin_selection_no_servers(self):
        """Test Round Robin selection with no servers."""
        with pytest.raises(Exception, match="No healthy servers available"):
            self.load_balancer._select_next_server([])
    
    def test_health_status_no_servers(self):
        """Test health status with no servers."""
        status = self.load_balancer.get_health_status()
        
        assert status.status == ServerStatus.UNHEALTHY
        assert "No servers in pool" in status.message
        assert status.details["total_servers"] == 0
        assert status.details["healthy_servers"] == 0
    
    def test_health_status_all_healthy(self):
        """Test health status with all healthy servers."""
        self.load_balancer.add_server(self.server_a)
        self.load_balancer.add_server(self.server_b)
        
        status = self.load_balancer.get_health_status()
        
        assert status.status == ServerStatus.HEALTHY
        assert "All servers healthy (2/2)" in status.message
        assert status.details["total_servers"] == 2
        assert status.details["healthy_servers"] == 2
    
    def test_health_status_partially_healthy(self):
        """Test health status with some unhealthy servers."""
        self.load_balancer.add_server(self.server_a)
        self.load_balancer.add_server(self.server_c)  # unhealthy
        
        status = self.load_balancer.get_health_status()
        
        assert status.status == ServerStatus.HEALTHY
        assert "Partially healthy (1/2 servers)" in status.message
        assert status.details["total_servers"] == 2
        assert status.details["healthy_servers"] == 1
    
    def test_health_status_all_unhealthy(self):
        """Test health status with all unhealthy servers."""
        self.server_a.status = ServerStatus.UNHEALTHY
        self.load_balancer.add_server(self.server_a)
        self.load_balancer.add_server(self.server_c)
        
        status = self.load_balancer.get_health_status()
        
        assert status.status == ServerStatus.UNHEALTHY
        assert "No healthy servers (0/2)" in status.message
        assert status.details["total_servers"] == 2
        assert status.details["healthy_servers"] == 0
    
    @patch('scalable_ai_api.load_balancer.core.requests.Session.post')
    def test_forward_request_success(self, mock_post):
        """Test successful request forwarding."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "request_id": "test_req_123",
            "server_id": "server_a",
            "response_text": "AI Response from server_a",
            "processing_time": 0.5,
            "correlation_id": "corr_123"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Create test request
        request = AIRequest(
            request_id="test_req_123",
            client_id="client_1",
            prompt="Test prompt",
            correlation_id="corr_123"
        )
        
        # Forward request
        response = self.load_balancer._forward_request(self.server_a, request)
        
        # Verify response
        assert response.request_id == "test_req_123"
        assert response.server_id == "server_a"
        assert response.response_text == "AI Response from server_a"
        assert response.processing_time == 0.5
        assert response.correlation_id == "corr_123"
        
        # Verify server metrics updated
        assert self.server_a.request_count == 1
        assert self.server_a.response_time == 0.5
        
        # Verify HTTP call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]['timeout'] == 5  # request_timeout
        assert "X-Correlation-ID" in call_args[1]['headers']
    
    @patch('scalable_ai_api.load_balancer.core.requests.Session.post')
    def test_forward_request_timeout(self, mock_post):
        """Test request forwarding timeout."""
        mock_post.side_effect = requests.exceptions.Timeout()
        
        request = AIRequest(
            request_id="test_req_123",
            prompt="Test prompt"
        )
        
        with pytest.raises(Exception, match="Request timeout"):
            self.load_balancer._forward_request(self.server_a, request)
    
    @patch('scalable_ai_api.load_balancer.core.requests.Session.post')
    def test_forward_request_connection_error(self, mock_post):
        """Test request forwarding connection error."""
        mock_post.side_effect = requests.exceptions.ConnectionError()
        
        request = AIRequest(
            request_id="test_req_123",
            prompt="Test prompt"
        )
        
        with pytest.raises(Exception, match="Connection failed"):
            self.load_balancer._forward_request(self.server_a, request)
    
    @patch('scalable_ai_api.load_balancer.core.LoadBalancerCore._forward_request')
    def test_route_request_success(self, mock_forward):
        """Test successful request routing."""
        # Setup
        self.load_balancer.add_server(self.server_a)
        self.load_balancer.add_server(self.server_b)
        
        mock_response = AIResponse(
            request_id="test_req_123",
            server_id="server_a",
            response_text="Test response",
            processing_time=0.3
        )
        mock_forward.return_value = mock_response
        
        request = AIRequest(
            request_id="test_req_123",
            prompt="Test prompt"
        )
        
        # Route request
        response = self.load_balancer.route_request(request)
        
        # Verify
        assert response == mock_response
        assert self.load_balancer.metrics.total_requests == 1
        assert self.load_balancer.metrics.server_distribution["server_a"] == 1
        mock_forward.assert_called_once_with(self.server_a, request)
    
    def test_route_request_no_healthy_servers(self):
        """Test routing request with no healthy servers."""
        # Add only unhealthy servers
        self.load_balancer.add_server(self.server_c)
        
        request = AIRequest(
            request_id="test_req_123",
            prompt="Test prompt"
        )
        
        response = self.load_balancer.route_request(request)
        
        # Should return error response
        assert response.server_id == "load_balancer"
        assert response.error_message is not None
        assert "No healthy servers available" in response.error_message
        assert self.load_balancer.metrics.total_requests == 1
        assert self.load_balancer.metrics.error_rate == 1.0
    
    @patch('scalable_ai_api.load_balancer.core.LoadBalancerCore._forward_request')
    def test_route_request_server_error(self, mock_forward):
        """Test routing request when server returns error."""
        self.load_balancer.add_server(self.server_a)
        
        mock_forward.side_effect = Exception("Server error")
        
        request = AIRequest(
            request_id="test_req_123",
            prompt="Test prompt"
        )
        
        response = self.load_balancer.route_request(request)
        
        # Should return error response
        assert response.server_id == "load_balancer"
        assert response.error_message is not None
        assert "Request routing failed" in response.error_message
        assert self.load_balancer.metrics.total_requests == 1
        assert self.load_balancer.metrics.error_rate == 1.0
    
    def test_metrics_tracking(self):
        """Test metrics tracking functionality."""
        # Test successful request metrics
        self.load_balancer._update_metrics_success("server_a", 0.5)
        
        metrics = self.load_balancer.get_metrics()
        assert metrics.total_requests == 1
        assert metrics.average_response_time == 0.5
        assert metrics.error_rate == 0.0
        assert metrics.server_distribution["server_a"] == 1
        
        # Test error metrics
        self.load_balancer._update_metrics_error()
        
        metrics = self.load_balancer.get_metrics()
        assert metrics.total_requests == 2
        assert metrics.error_rate == 0.5  # 1 error out of 2 requests
    
    def test_thread_safety(self):
        """Test thread safety of server pool operations."""
        def add_servers():
            for i in range(10):
                server = ServerInstance(
                    id=f"server_{i}",
                    ip_address="127.0.0.1",
                    port=8080 + i,
                    status=ServerStatus.HEALTHY
                )
                self.load_balancer.add_server(server)
        
        def remove_servers():
            time.sleep(0.01)  # Small delay to interleave operations
            for i in range(5):
                self.load_balancer.remove_server(f"server_{i}")
        
        # Run operations concurrently
        thread1 = threading.Thread(target=add_servers)
        thread2 = threading.Thread(target=remove_servers)
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # Verify final state is consistent
        pool = self.load_balancer.get_current_server_pool()
        assert len(pool) == 5  # 10 added - 5 removed
        
        # Verify all remaining servers have unique IDs
        server_ids = [s.id for s in pool]
        assert len(server_ids) == len(set(server_ids))
    
    def test_shutdown(self):
        """Test load balancer shutdown."""
        # Should not raise any exceptions
        self.load_balancer.shutdown()
        
        # Session should be closed
        # Note: We can't easily test if session is closed without accessing private attributes


class TestLoadBalancerRoundRobinDistribution:
    """Test Round Robin distribution fairness."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.load_balancer = LoadBalancerCore()
        
        # Add multiple servers
        for i in range(3):
            server = ServerInstance(
                id=f"server_{i}",
                ip_address="127.0.0.1",
                port=8080 + i,
                status=ServerStatus.HEALTHY
            )
            self.load_balancer.add_server(server)
    
    def test_round_robin_fairness_multiple_selections(self):
        """Test that Round Robin distributes requests fairly over multiple selections."""
        healthy_servers = [s for s in self.load_balancer.server_pool if s.status == ServerStatus.HEALTHY]
        selections = []
        
        # Make 9 selections (3 full rounds)
        for _ in range(9):
            server = self.load_balancer._select_next_server(healthy_servers)
            selections.append(server.id)
        
        # Verify distribution pattern
        expected_pattern = ["server_0", "server_1", "server_2"] * 3
        assert selections == expected_pattern
    
    def test_round_robin_with_server_removal(self):
        """Test Round Robin behavior when servers are removed."""
        healthy_servers = [s for s in self.load_balancer.server_pool if s.status == ServerStatus.HEALTHY]
        
        # Select first server
        server1 = self.load_balancer._select_next_server(healthy_servers)
        assert server1.id == "server_0"
        
        # Remove server_1
        self.load_balancer.remove_server("server_1")
        
        # Update healthy servers list
        healthy_servers = [s for s in self.load_balancer.server_pool if s.status == ServerStatus.HEALTHY]
        
        # Next selection should be server_2 (skipping removed server_1)
        server2 = self.load_balancer._select_next_server(healthy_servers)
        assert server2.id == "server_2"
        
        # Next selection should wrap to server_0
        server3 = self.load_balancer._select_next_server(healthy_servers)
        assert server3.id == "server_0"


if __name__ == "__main__":
    pytest.main([__file__])