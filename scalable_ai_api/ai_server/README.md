# AI Server Module

This module implements the base AI Server functionality using FastAPI as specified in Task 2.1.

## Features Implemented

### ✅ FastAPI Application with Health Check Endpoint
- **Health Check Endpoint** (`/health`): Returns server health status with metrics
- **Server Info Endpoint** (`/info`): Provides server information and statistics
- **AI Processing Endpoint** (`/api/ai`): Processes AI requests with server identification

### ✅ Server Identification in Responses
- Each server instance has a unique `server_id`
- All responses include the `server_id` that processed the request
- Response headers include `X-Server-ID` for easy identification
- AI responses clearly identify which server processed the request

### ✅ Request/Response Correlation Tracking
- **Correlation ID Support**: Accepts `X-Correlation-ID` header from clients
- **Auto-Generation**: Generates correlation IDs when not provided
- **Preservation**: Maintains correlation IDs throughout request processing
- **Response Headers**: Returns correlation ID in `X-Correlation-ID` header
- **Logging**: Includes correlation IDs in all log messages

### ✅ Basic Error Handling and Logging
- **Input Validation**: Validates all incoming requests
- **Error Responses**: Returns appropriate HTTP status codes with descriptive messages
- **Structured Logging**: Comprehensive logging with correlation tracking
- **Exception Handling**: Graceful handling of processing errors
- **Health Monitoring**: Tracks server health metrics (CPU, memory, disk usage)

## Usage

### Starting a Server Instance

```bash
# Start Server A on port 8080
python -m scalable_ai_api.ai_server.server_runner --server-id "Server A" --port 8080

# Start Server B on port 8081
python -m scalable_ai_api.ai_server.server_runner --server-id "Server B" --port 8081
```

### API Endpoints

#### Health Check
```bash
curl http://localhost:8080/health
```

Response:
```json
{
  "status": "healthy",
  "server_id": "Server A",
  "uptime_seconds": 123.45,
  "metrics": {
    "cpu_usage": 25.0,
    "memory_usage": 45.2,
    "request_count": 10.0,
    "average_response_time": 0.15
  },
  "timestamp": "2026-04-01T09:00:00.000000"
}
```

#### Server Information
```bash
curl http://localhost:8080/info
```

#### AI Request Processing
```bash
curl -X POST http://localhost:8080/api/ai \
  -H "Content-Type: application/json" \
  -H "X-Correlation-ID: my-request-123" \
  -d '{
    "prompt": "Hello, AI!",
    "parameters": {"temperature": 0.7},
    "client_id": "my_client"
  }'
```

Response:
```json
{
  "request_id": "uuid-generated-id",
  "server_id": "Server A",
  "response_text": "AI Response from Server A: Processed prompt 'Hello, AI!' with parameters {'temperature': 0.7}",
  "processing_time": 0.025,
  "correlation_id": "my-request-123",
  "timestamp": "2026-04-01T09:00:00.000000"
}
```

## Requirements Satisfied

This implementation satisfies the following requirements:

- **Requirement 6.1**: ✅ Process valid AI requests and return responses within 10 seconds
- **Requirement 6.2**: ✅ Include server identification in responses for A/B testing
- **Requirement 6.3**: ✅ Maintain request/response correlation IDs
- **Requirement 6.4**: ✅ Return appropriate error codes with descriptive messages for failed requests

## Architecture

The AI Server is built using:

- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI applications
- **psutil**: System monitoring for health metrics
- **Correlation Middleware**: Custom middleware for request tracking
- **Structured Logging**: Comprehensive logging with correlation support

## Testing

Comprehensive unit tests are available in `tests/test_ai_server.py`:

```bash
# Run all AI Server tests
python -m pytest tests/test_ai_server.py -v

# Run specific test class
python -m pytest tests/test_ai_server.py::TestBaseAIServer -v
```

## Demo

Use the demo script to test the servers:

```bash
# Show manual testing commands
python demo_servers.py --mode manual

# Run automated testing (starts servers and tests them)
python demo_servers.py --mode auto
```

## Next Steps

This base AI Server implementation is ready for integration with:

1. **Load Balancer** (Task 3.x) - Will route requests between Server A and Server B
2. **Health Monitoring** (Task 5.x) - Will use the `/health` endpoint
3. **Auto Scaling** (Task 7.x) - Will create/destroy server instances
4. **Performance Monitoring** (Task 6.x) - Will collect metrics from servers

The server identification and correlation tracking features are specifically designed to support A/B testing and distributed request tracing in the complete system.