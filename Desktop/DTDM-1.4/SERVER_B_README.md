# Server B Instance - Scalable AI API System

## Overview

Server B is one of the two AI server instances in the Scalable AI API System. It runs on port 8081 and clearly identifies itself as "Server B" in all responses, meeting Requirements 2.1 and 2.3.

## Features

- **Server Identification**: All responses clearly identify "Server B" as the processing server
- **Health Monitoring**: Provides health check endpoint at `/health`
- **Request Correlation**: Preserves and returns correlation IDs for request tracking
- **Error Handling**: Comprehensive error handling with descriptive messages
- **Metrics Collection**: Tracks request count, processing times, and system metrics

## Quick Start

### Starting Server B

```bash
# Method 1: Using the demo script
python demo_servers.py --mode auto

# Method 2: Using the server runner module
python -m scalable_ai_api.ai_server.server_runner --server-id "Server B" --port 8081
```

### Testing Server B

```bash
# Health check
curl http://localhost:8081/health

# Server info
curl http://localhost:8081/info

# AI request
curl -X POST http://localhost:8081/api/ai \
  -H "Content-Type: application/json" \
  -H "X-Correlation-ID: test-123" \
  -d '{"prompt": "Hello Server B!", "client_id": "test"}'
```

## API Endpoints

### Health Check: `GET /health`

Returns server health status and metrics:

```json
{
  "status": "healthy",
  "server_id": "Server B",
  "uptime_seconds": 123.45,
  "metrics": {
    "cpu_usage": 15.2,
    "memory_usage": 45.8,
    "request_count": 10
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

### Server Info: `GET /info`

Returns detailed server information:

```json
{
  "server_id": "Server B",
  "host": "0.0.0.0",
  "port": 8081,
  "status": "healthy",
  "start_time": "2024-01-01T11:00:00",
  "uptime_seconds": 3600.0,
  "request_count": 25,
  "average_processing_time": 0.125
}
```

### AI Processing: `POST /api/ai`

Processes AI requests and returns responses with server identification:

```json
{
  "request_id": "req-123",
  "server_id": "Server B",
  "response_text": "AI Response from Server B: Processed prompt 'Hello Server B!' with parameters {...}",
  "processing_time": 0.145,
  "correlation_id": "test-123",
  "timestamp": "2024-01-01T12:00:00"
}
```

All AI responses include:
- `server_id`: Always "Server B"
- `request_id`: Unique request identifier
- `correlation_id`: Preserved from request headers
- `response_text`: AI-generated response (includes "Server B" identification)
- `processing_time`: Time taken to process the request
- `timestamp`: Response generation timestamp

Response headers include:
- `X-Server-ID: Server B`
- `X-Correlation-ID: <correlation-id>`

## Requirements Compliance

### Requirement 2.1: Server Deployment
✅ **SATISFIED**: Server B is deployed and runs on port 8081 as specified

### Requirement 2.3: Server Identification
✅ **SATISFIED**: Server B clearly identifies itself in all responses:
- Response body contains `"server_id": "Server B"`
- Response text includes "Server B" identification
- Response headers include `X-Server-ID: Server B`

## Configuration

Server B uses the following default configuration:
- **Server ID**: "Server B"
- **Host**: 0.0.0.0 (all interfaces)
- **Port**: 8081
- **Log Level**: INFO
- **Health Check**: Enabled

## Monitoring

Server B provides comprehensive monitoring through:
- Health check endpoint with system metrics
- Request counting and timing
- CPU and memory usage tracking
- Error rate monitoring
- Response time analytics

## Integration

Server B is designed to work with:
- Load Balancer (Round Robin distribution)
- Health Monitoring System
- Auto Scaling Controller
- Metrics Collection System

## Logs

Server B logs to:
- **Console**: Real-time logging output
- **File**: `ai_server.log` for persistent logging

Log entries include:
- Request processing details
- Health check results
- Error conditions
- Performance metrics

## Testing

Use the provided test script to validate Server B:

```bash
python test_server_b.py
```

Tests include:
- Health endpoint validation
- Server identification verification
- Request/response correlation
- Error handling
- Multiple request consistency

All tests must pass to ensure Server B meets the requirements.

## A/B Testing

Server B works in conjunction with Server A to enable A/B testing:
- Both servers use identical APIs
- Server identification allows tracking which server processed each request
- Load balancer can distribute requests between Server A (port 8080) and Server B (port 8081)
- Responses clearly indicate the processing server for analysis

## Troubleshooting

### Common Issues

1. **Port 8081 already in use**
   - Check for existing processes: `lsof -i :8081`
   - Kill existing process or use different port

2. **Health check fails**
   - Verify server is running: `curl http://localhost:8081/health`
   - Check logs for error messages
   - Ensure sufficient system resources

3. **AI requests timeout**
   - Check server logs for processing errors
   - Verify request format matches API specification
   - Ensure correlation ID is properly formatted

### Performance Tuning

- Monitor CPU and memory usage through health endpoint
- Adjust processing delays based on system capacity
- Scale horizontally by adding more server instances
- Use load balancer to distribute traffic evenly

## Next Steps

After Server B is running:
1. Implement Load Balancer for Round Robin distribution
2. Set up Health Monitoring System
3. Configure Auto Scaling Controller
4. Deploy comprehensive monitoring and alerting