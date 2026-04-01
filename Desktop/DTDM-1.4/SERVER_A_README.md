# Server A Instance - Scalable AI API System

## Overview

Server A is one of the two AI server instances in the Scalable AI API System. It runs on port 8080 and clearly identifies itself as "Server A" in all responses, meeting Requirements 2.1 and 2.2.

## Features

- **Server Identification**: All responses clearly identify "Server A" as the processing server
- **Health Monitoring**: Provides health check endpoint at `/health`
- **Request Correlation**: Preserves and returns correlation IDs for request tracking
- **Error Handling**: Comprehensive error handling with descriptive messages
- **Metrics Collection**: Tracks request count, processing times, and system metrics

## Quick Start

### Starting Server A

```bash
# Method 1: Using the dedicated script
python server_a.py

# Method 2: Using the server runner module
python -m scalable_ai_api.ai_server.server_runner --server-id "Server A" --port 8080
```

### Testing Server A

```bash
# Run validation tests
python test_server_a.py

# Manual health check
curl http://localhost:8080/health

# Manual server info
curl http://localhost:8080/info

# Manual AI request
curl -X POST http://localhost:8080/api/ai \
  -H "Content-Type: application/json" \
  -H "X-Correlation-ID: test-123" \
  -d '{"prompt": "Hello Server A!", "client_id": "test"}'
```

## API Endpoints

### Health Check
- **URL**: `GET /health`
- **Purpose**: Check server health status
- **Response**: Health metrics and server status

### Server Information
- **URL**: `GET /info`
- **Purpose**: Get server configuration and statistics
- **Response**: Server ID, port, uptime, request count

### AI Processing
- **URL**: `POST /api/ai`
- **Purpose**: Process AI requests
- **Headers**: 
  - `Content-Type: application/json`
  - `X-Correlation-ID: <optional-correlation-id>`
- **Body**: 
  ```json
  {
    "prompt": "Your AI prompt here",
    "parameters": {"temperature": 0.7},
    "client_id": "your_client_id",
    "request_id": "optional_request_id"
  }
  ```

## Response Format

All AI responses include:
- `server_id`: Always "Server A"
- `request_id`: Unique request identifier
- `correlation_id`: Preserved from request headers
- `response_text`: AI-generated response (includes "Server A" identification)
- `processing_time`: Time taken to process the request
- `timestamp`: Response generation timestamp

Response headers include:
- `X-Server-ID: Server A`
- `X-Correlation-ID: <correlation-id>`

## Requirements Compliance

### Requirement 2.1: Server Deployment
✅ **SATISFIED**: Server A is deployed and runs on port 8080 as specified

### Requirement 2.2: Server Identification
✅ **SATISFIED**: Server A clearly identifies itself in all responses:
- Response body contains `"server_id": "Server A"`
- Response text includes "Server A" identification
- Response headers include `X-Server-ID: Server A`

## Configuration

Server A uses the following default configuration:
- **Server ID**: "Server A"
- **Host**: 0.0.0.0 (all interfaces)
- **Port**: 8080
- **Log Level**: INFO
- **Log File**: server_a.log

## Monitoring

Server A provides comprehensive monitoring through:
- Health check endpoint with system metrics
- Request counting and timing
- CPU and memory usage tracking
- Uptime monitoring
- Error logging and tracking

## Integration

Server A is designed to work with:
- Load Balancer (Round Robin distribution)
- Health Monitoring System
- Auto Scaling Controller
- Metrics Collection System

## Logs

Server A logs to:
- **Console**: Real-time logging output
- **File**: `server_a.log` for persistent logging

Log entries include:
- Server startup and shutdown events
- Request processing with correlation IDs
- Health check results
- Error conditions and exceptions

## Validation

The `test_server_a.py` script validates:
- Health check functionality
- Server information accuracy
- AI request processing
- Server identification in responses
- Request correlation preservation
- Multiple request consistency

All tests must pass to ensure Server A meets the requirements.