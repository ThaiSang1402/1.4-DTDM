"""
Property-based tests for AI Server responses.

This module implements Property 5: Server Response Identification
using Hypothesis for property-based testing.

**Validates: Requirements 2.2, 2.3, 6.2**
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from hypothesis.stateful import RuleBasedStateMachine, rule, initialize, invariant
from fastapi.testclient import TestClient
import uuid
from typing import Dict, Any, List

from scalable_ai_api.ai_server import BaseAIServer
from scalable_ai_api.models import AIRequest, ServerStatus


# Hypothesis strategies for generating test data
@st.composite
def server_id_strategy(draw):
    """Generate valid server IDs (ASCII-safe for HTTP headers)."""
    server_types = ["Server A", "Server B", "Test Server", "Production Server"]
    # Use ASCII-safe characters only (for HTTP header compatibility)
    custom_id = draw(st.text(
        min_size=1, 
        max_size=50, 
        alphabet=st.characters(min_codepoint=32, max_codepoint=126)  # ASCII printable
    ).filter(lambda x: x.strip() and not x.startswith(' ') and not x.endswith(' ')))
    return draw(st.one_of(st.sampled_from(server_types), st.just(custom_id)))


@st.composite
def ai_request_strategy(draw):
    """Generate valid AI requests."""
    prompt = draw(st.text(min_size=1, max_size=1000))
    client_id = draw(st.text(min_size=0, max_size=100))
    request_id = draw(st.one_of(
        st.just(str(uuid.uuid4())),
        st.text(min_size=1, max_size=100)
    ))
    
    # Generate parameters dictionary
    param_keys = draw(st.lists(
        st.text(min_size=1, max_size=20, alphabet=st.characters(min_codepoint=97, max_codepoint=122)),
        min_size=0, max_size=5, unique=True
    ))
    param_values = draw(st.lists(
        st.one_of(
            st.floats(min_value=0.0, max_value=2.0, allow_nan=False, allow_infinity=False),
            st.integers(min_value=1, max_value=1000),
            st.text(min_size=0, max_size=50)
        ),
        min_size=len(param_keys), max_size=len(param_keys)
    ))
    parameters = dict(zip(param_keys, param_values))
    
    correlation_id = draw(st.one_of(
        st.none(),
        st.just(str(uuid.uuid4())),
        st.text(min_size=1, max_size=100)
    ))
    
    return AIRequest(
        request_id=request_id,
        client_id=client_id,
        prompt=prompt,
        parameters=parameters,
        correlation_id=correlation_id
    )


@st.composite
def http_request_strategy(draw):
    """Generate valid HTTP request payloads."""
    prompt = draw(st.text(min_size=1, max_size=1000))
    client_id = draw(st.text(min_size=0, max_size=100))
    request_id = draw(st.one_of(
        st.none(),
        st.text(min_size=1, max_size=100)
    ))
    
    # Generate parameters
    param_count = draw(st.integers(min_value=0, max_value=5))
    parameters = {}
    for _ in range(param_count):
        key = draw(st.text(min_size=1, max_size=20, alphabet=st.characters(min_codepoint=97, max_codepoint=122)))
        value = draw(st.one_of(
            st.floats(min_value=0.0, max_value=2.0, allow_nan=False, allow_infinity=False),
            st.integers(min_value=1, max_value=1000),
            st.text(min_size=0, max_size=50)
        ))
        parameters[key] = value
    
    request_data = {
        "prompt": prompt,
        "client_id": client_id,
        "parameters": parameters
    }
    
    if request_id is not None:
        request_data["request_id"] = request_id
    
    return request_data


class TestServerResponseIdentificationProperty:
    """
    Property-based tests for Server Response Identification.
    
    **Validates: Requirements 2.2, 2.3, 6.2**
    
    Property 5: Server Response Identification
    For any request processed by an AI_Server, the response should contain 
    clear identification of which server processed the request.
    """
    
    @given(server_id=server_id_strategy(), ai_request=ai_request_strategy())
    @settings(max_examples=50, deadline=5000)
    def test_property_server_response_identification_direct(self, server_id: str, ai_request: AIRequest):
        """
        **Validates: Requirements 2.2, 2.3, 6.2**
        
        Property: For any request processed by an AI_Server, the response should 
        contain clear identification of which server processed the request.
        
        This test validates the property through direct method calls.
        """
        # Arrange: Create server with generated server_id
        server = BaseAIServer(server_id=server_id, port=9000 + hash(server_id) % 1000)
        
        # Act: Process the AI request
        response = server.process_ai_request(ai_request)
        
        # Assert: Response must contain server identification
        assert response.server_id == server_id, (
            f"Response server_id '{response.server_id}' does not match "
            f"expected server_id '{server_id}'"
        )
        
        # Assert: Response text must contain server identification
        assert server_id in response.response_text, (
            f"Server ID '{server_id}' not found in response text: '{response.response_text}'"
        )
        
        # Assert: Response must preserve request correlation
        assert response.request_id == ai_request.request_id, (
            f"Response request_id '{response.request_id}' does not match "
            f"original request_id '{ai_request.request_id}'"
        )
        
        # Assert: Correlation ID preservation
        if ai_request.correlation_id is not None:
            assert response.correlation_id == ai_request.correlation_id, (
                f"Response correlation_id '{response.correlation_id}' does not match "
                f"original correlation_id '{ai_request.correlation_id}'"
            )
        
        # Assert: Response must have valid processing time
        assert response.processing_time >= 0, (
            f"Processing time must be non-negative, got: {response.processing_time}"
        )
        
        # Assert: Response must have timestamp
        assert response.timestamp is not None, "Response must have a timestamp"
    
    @given(server_id=server_id_strategy(), http_request=http_request_strategy())
    @settings(max_examples=50, deadline=10000)
    def test_property_server_response_identification_http(self, server_id: str, http_request: Dict[str, Any]):
        """
        **Validates: Requirements 2.2, 2.3, 6.2**
        
        Property: For any HTTP request processed by an AI_Server, the response should 
        contain clear identification of which server processed the request.
        
        This test validates the property through HTTP endpoints.
        """
        # Arrange: Create server and HTTP client
        server = BaseAIServer(server_id=server_id, port=9000 + hash(server_id) % 1000)
        client = TestClient(server.app)
        
        # Act: Send HTTP request
        response = client.post("/api/ai", json=http_request)
        
        # Assert: HTTP response must be successful
        assert response.status_code == 200, (
            f"Expected HTTP 200, got {response.status_code}: {response.text}"
        )
        
        # Assert: Response headers must contain server identification
        assert "X-Server-ID" in response.headers, "Response headers must contain X-Server-ID"
        assert response.headers["X-Server-ID"] == server_id, (
            f"Header X-Server-ID '{response.headers['X-Server-ID']}' does not match "
            f"expected server_id '{server_id}'"
        )
        
        # Assert: Response body must contain server identification
        response_data = response.json()
        assert "server_id" in response_data, "Response body must contain server_id field"
        assert response_data["server_id"] == server_id, (
            f"Response body server_id '{response_data['server_id']}' does not match "
            f"expected server_id '{server_id}'"
        )
        
        # Assert: Response text must contain server identification
        assert "response_text" in response_data, "Response body must contain response_text field"
        assert server_id in response_data["response_text"], (
            f"Server ID '{server_id}' not found in response text: '{response_data['response_text']}'"
        )
        
        # Assert: Correlation ID must be present in headers
        assert "X-Correlation-ID" in response.headers, "Response headers must contain X-Correlation-ID"
        
        # Assert: Correlation ID must be present in response body
        assert "correlation_id" in response_data, "Response body must contain correlation_id field"
        assert response_data["correlation_id"] == response.headers["X-Correlation-ID"], (
            "Correlation ID in body must match correlation ID in headers"
        )
    
    @given(
        server_ids=st.lists(server_id_strategy(), min_size=2, max_size=5, unique=True),
        ai_request=ai_request_strategy()
    )
    @settings(max_examples=30, deadline=10000)
    def test_property_server_identification_uniqueness(self, server_ids: List[str], ai_request: AIRequest):
        """
        **Validates: Requirements 2.2, 2.3, 6.2**
        
        Property: Different servers must produce responses with unique server identification.
        
        This test ensures that server identification is unique and consistent.
        """
        servers = []
        responses = []
        
        # Arrange: Create multiple servers with different IDs
        for i, server_id in enumerate(server_ids):
            server = BaseAIServer(server_id=server_id, port=9100 + i)
            servers.append(server)
        
        # Act: Process same request on all servers
        for server in servers:
            response = server.process_ai_request(ai_request)
            responses.append(response)
        
        # Assert: Each response must have unique server identification
        response_server_ids = [resp.server_id for resp in responses]
        assert len(set(response_server_ids)) == len(server_ids), (
            f"Server IDs in responses are not unique: {response_server_ids}"
        )
        
        # Assert: Each response must match its corresponding server
        for server, response in zip(servers, responses):
            assert response.server_id == server.server_id, (
                f"Response server_id '{response.server_id}' does not match "
                f"server's server_id '{server.server_id}'"
            )
            
            # Assert: Response text must contain the correct server ID
            assert server.server_id in response.response_text, (
                f"Server ID '{server.server_id}' not found in response text: '{response.response_text}'"
            )
        
        # Assert: Response texts must be different (contain different server IDs)
        response_texts = [resp.response_text for resp in responses]
        unique_texts = set(response_texts)
        assert len(unique_texts) == len(server_ids), (
            f"Response texts are not unique, indicating server identification failed"
        )
    
    @given(server_id=server_id_strategy())
    @settings(max_examples=20, deadline=5000)
    def test_property_server_info_consistency(self, server_id: str):
        """
        **Validates: Requirements 2.2, 2.3, 6.2**
        
        Property: Server information endpoints must consistently return the same server identification.
        """
        # Arrange: Create server
        server = BaseAIServer(server_id=server_id, port=9200 + hash(server_id) % 100)
        client = TestClient(server.app)
        
        # Act: Get server info through different methods
        direct_info = server.get_server_info()
        http_info_response = client.get("/info")
        health_response = client.get("/health")
        
        # Assert: HTTP responses must be successful
        assert http_info_response.status_code == 200
        assert health_response.status_code in [200, 503]  # Health check might fail in test environment
        
        # Assert: All methods must return consistent server identification
        http_info_data = http_info_response.json()
        health_data = health_response.json()
        
        assert direct_info["server_id"] == server_id
        assert http_info_data["server_id"] == server_id
        assert health_data["server_id"] == server_id
        
        # Assert: Headers must contain consistent server identification
        assert http_info_response.headers["X-Server-ID"] == server_id
        assert health_response.headers["X-Server-ID"] == server_id
    
    @given(
        server_id=server_id_strategy(),
        requests=st.lists(ai_request_strategy(), min_size=1, max_size=10)
    )
    @settings(max_examples=20, deadline=15000)
    def test_property_server_identification_persistence(self, server_id: str, requests: List[AIRequest]):
        """
        **Validates: Requirements 2.2, 2.3, 6.2**
        
        Property: Server identification must remain consistent across multiple requests.
        """
        # Arrange: Create server
        server = BaseAIServer(server_id=server_id, port=9300 + hash(server_id) % 100)
        
        # Act: Process multiple requests
        responses = []
        for request in requests:
            response = server.process_ai_request(request)
            responses.append(response)
        
        # Assert: All responses must have the same server identification
        for i, response in enumerate(responses):
            assert response.server_id == server_id, (
                f"Request {i}: Response server_id '{response.server_id}' does not match "
                f"expected server_id '{server_id}'"
            )
            
            assert server_id in response.response_text, (
                f"Request {i}: Server ID '{server_id}' not found in response text: '{response.response_text}'"
            )
        
        # Assert: Server identification must be consistent across all responses
        server_ids_in_responses = [resp.server_id for resp in responses]
        unique_server_ids = set(server_ids_in_responses)
        assert len(unique_server_ids) == 1, (
            f"Server identification is not consistent across requests: {unique_server_ids}"
        )
        assert list(unique_server_ids)[0] == server_id


class ServerResponseStateMachine(RuleBasedStateMachine):
    """
    Stateful property-based testing for server response identification.
    
    **Validates: Requirements 2.2, 2.3, 6.2**
    
    This state machine tests that server identification remains consistent
    throughout the server's lifecycle and various operations.
    """
    
    def __init__(self):
        super().__init__()
        self.servers: Dict[str, BaseAIServer] = {}
        self.clients: Dict[str, TestClient] = {}
        self.processed_requests: List[Dict[str, Any]] = []
    
    @initialize()
    def setup_servers(self):
        """Initialize test servers."""
        server_configs = [
            ("Server A", 9400),
            ("Server B", 9401),
            ("Test Server Alpha", 9402)
        ]
        
        for server_id, port in server_configs:
            server = BaseAIServer(server_id=server_id, port=port)
            client = TestClient(server.app)
            self.servers[server_id] = server
            self.clients[server_id] = client
    
    @rule(
        server_id=st.sampled_from(["Server A", "Server B", "Test Server Alpha"]),
        ai_request=ai_request_strategy()
    )
    def process_request_direct(self, server_id: str, ai_request: AIRequest):
        """Process request directly and verify server identification."""
        server = self.servers[server_id]
        response = server.process_ai_request(ai_request)
        
        # Record the request/response for invariant checking
        self.processed_requests.append({
            "server_id": server_id,
            "request_id": ai_request.request_id,
            "response_server_id": response.server_id,
            "method": "direct"
        })
        
        # Verify server identification
        assert response.server_id == server_id
        assert server_id in response.response_text
    
    @rule(
        server_id=st.sampled_from(["Server A", "Server B", "Test Server Alpha"]),
        http_request=http_request_strategy()
    )
    def process_request_http(self, server_id: str, http_request: Dict[str, Any]):
        """Process request via HTTP and verify server identification."""
        client = self.clients[server_id]
        response = client.post("/api/ai", json=http_request)
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Record the request/response for invariant checking
            self.processed_requests.append({
                "server_id": server_id,
                "request_id": http_request.get("request_id", "generated"),
                "response_server_id": response_data["server_id"],
                "method": "http"
            })
            
            # Verify server identification
            assert response_data["server_id"] == server_id
            assert response.headers["X-Server-ID"] == server_id
            assert server_id in response_data["response_text"]
    
    @rule(server_id=st.sampled_from(["Server A", "Server B", "Test Server Alpha"]))
    def check_server_info(self, server_id: str):
        """Check server info consistency."""
        server = self.servers[server_id]
        client = self.clients[server_id]
        
        # Get info through different methods
        direct_info = server.get_server_info()
        http_response = client.get("/info")
        
        if http_response.status_code == 200:
            http_info = http_response.json()
            
            # Verify consistency
            assert direct_info["server_id"] == server_id
            assert http_info["server_id"] == server_id
            assert http_response.headers["X-Server-ID"] == server_id
    
    @invariant()
    def server_identification_consistency(self):
        """
        Invariant: All responses from a server must have consistent server identification.
        """
        # Group requests by server
        by_server = {}
        for record in self.processed_requests:
            server_id = record["server_id"]
            if server_id not in by_server:
                by_server[server_id] = []
            by_server[server_id].append(record)
        
        # Check consistency within each server
        for server_id, records in by_server.items():
            response_server_ids = [r["response_server_id"] for r in records]
            unique_response_ids = set(response_server_ids)
            
            assert len(unique_response_ids) == 1, (
                f"Server {server_id} produced inconsistent server IDs in responses: {unique_response_ids}"
            )
            assert list(unique_response_ids)[0] == server_id, (
                f"Server {server_id} produced incorrect server ID in responses: {unique_response_ids}"
            )
    
    @invariant()
    def no_cross_server_contamination(self):
        """
        Invariant: Responses from different servers must have different server identification.
        """
        if len(self.processed_requests) < 2:
            return  # Need at least 2 requests to check
        
        # Check that different servers produce different identifications
        server_to_response_ids = {}
        for record in self.processed_requests:
            server_id = record["server_id"]
            response_server_id = record["response_server_id"]
            
            if server_id not in server_to_response_ids:
                server_to_response_ids[server_id] = set()
            server_to_response_ids[server_id].add(response_server_id)
        
        # Each server should only produce its own server ID
        for server_id, response_ids in server_to_response_ids.items():
            assert len(response_ids) == 1, (
                f"Server {server_id} produced multiple different server IDs: {response_ids}"
            )
            assert list(response_ids)[0] == server_id, (
                f"Server {server_id} produced wrong server ID: {response_ids}"
            )


# Create the stateful test
TestServerResponseStateMachine = ServerResponseStateMachine.TestCase


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])