# Scalable AI API System

A scalable AI API system with load balancing, health monitoring, auto scaling, and comprehensive metrics collection.

## 🚀 Quick Deploy to Render

### Option 1: One-Click Deploy (Recommended)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Option 2: Manual Deploy
1. Fork this repository
2. Connect to Render via GitHub
3. Create Blueprint from `render.yaml`
4. Deploy all services automatically

**Live Demo URLs** (after deployment):
- **Load Balancer**: `https://scalable-ai-api-load-balancer.onrender.com`
- **Server A**: `https://scalable-ai-api-server-a.onrender.com`
- **Server B**: `https://scalable-ai-api-server-b.onrender.com`

### Test Deployment
```bash
# Test the deployed system
python test_render_deployment.py --config render_config.json

# Or test individual services
curl https://scalable-ai-api-load-balancer.onrender.com/health
```

📖 **[Complete Deployment Guide](RENDER_DEPLOYMENT.md)**

---

## Project Structure

```
scalable_ai_api/
├── __init__.py                 # Package initialization
├── main.py                     # Main entry point for Render
├── interfaces.py               # Core system interfaces
├── models.py                   # Data models and validation
├── load_balancer/              # Load balancer implementation
│   ├── core.py                 # Round Robin load balancer
│   └── render_app.py           # FastAPI app for Render
├── ai_server/                  # AI server instances
│   ├── base_server.py          # Base AI server implementation
│   └── server_runner.py        # Server startup utility
└── config/                     # Configuration management
    └── manager.py              # Configuration loading and validation

# Render deployment files
render.yaml                     # Render services configuration
Procfile                        # Process definitions
runtime.txt                     # Python version
requirements.txt                # Dependencies
RENDER_DEPLOYMENT.md           # Deployment guide
test_render_deployment.py      # Deployment testing
```

## Features

- **Load Balancing**: Round Robin request distribution across multiple AI server instances
- **Dual Server Architecture**: Server A (port 8080) and Server B (port 8081) for A/B testing
- **Health Monitoring**: Continuous health checks and status tracking
- **Auto Scaling**: Dynamic scaling based on CPU and request metrics
- **Configuration Management**: Support for environment variables and configuration files
- **Comprehensive Metrics**: Performance monitoring and reporting
- **Error Handling**: Robust error handling and recovery mechanisms
- **Server Identification**: Clear server identification in all responses for tracking
- **Cloud Ready**: Optimized for Render deployment with auto-scaling

## Configuration

The system supports configuration through:

1. **Configuration Files**: YAML or JSON format (see `config.yaml`)
2. **Environment Variables**: Override any configuration value (see `.env.example`)

Environment variables take precedence over configuration files.

### Key Configuration Parameters

- `LOAD_BALANCER_PORT`: Port for the load balancer (default: 8000)
- `HEALTH_CHECK_INTERVAL`: Health check frequency in seconds (default: 30)
- `MIN_INSTANCES`: Minimum number of server instances (default: 2)
- `MAX_INSTANCES`: Maximum number of server instances (default: 10)
- `SCALE_UP_THRESHOLD`: CPU threshold for scaling up (default: 80.0%)
- `SCALE_DOWN_THRESHOLD`: CPU threshold for scaling down (default: 30.0%)

## Quick Start

### Local Development

#### Running Individual Servers

Start Server A:
```bash
python -m scalable_ai_api.ai_server.server_runner --server-id "Server A" --port 8080
```

Start Server B:
```bash
python -m scalable_ai_api.ai_server.server_runner --server-id "Server B" --port 8081
```

#### Running Load Balancer
```bash
python -m scalable_ai_api.main --component load_balancer --port 8000
```

#### Running Both Servers (Demo)

Use the demo script to start both servers:
```bash
# Show manual commands
python demo_servers.py --mode manual

# Run automated demo
python demo_servers.py --mode auto
```

### Cloud Deployment (Render)

1. **Deploy via render.yaml**:
   - Connect GitHub repo to Render
   - Render auto-detects `render.yaml`
   - All 3 services deploy automatically

2. **Test deployment**:
   ```bash
   python test_render_deployment.py --config render_config.json
   ```

### A/B Testing Demo

Test both servers with A/B testing:
```bash
python demo_ab_testing.py
```

### Testing Individual Servers

Test Server A:
```bash
python test_server_a.py
```

Test Server B:
```bash
python test_server_b.py
```

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install the package in development mode:
```bash
pip install -e .
```

## Testing

Run the test suite:
```bash
pytest tests/
```

Run tests with coverage:
```bash
pytest tests/ --cov=scalable_ai_api
```

## API Endpoints

### Load Balancer
- `GET /` - Service information
- `GET /health` - Health check
- `GET /status` - Detailed status and metrics
- `POST /api/ai` - AI request processing (Round Robin)

### AI Servers (A & B)
- `GET /health` - Health check
- `GET /info` - Server information
- `POST /api/ai` - AI request processing

## Requirements Addressed

This implementation addresses the following requirements:

### Server Instance Management (Requirement 2)
- **Requirement 2.1**: ✅ System deploys exactly 2 AI server instances (Server A and Server B)
- **Requirement 2.2**: ✅ Server A processes requests and identifies itself as "Server A"
- **Requirement 2.3**: ✅ Server B processes requests and identifies itself as "Server B"

### Load Balancing (Requirement 1)
- **Requirement 1.1**: ✅ Round Robin request distribution
- **Requirement 1.4**: ✅ Single URL endpoint for client access
- **Requirement 1.5**: ✅ Dynamic server pool management

### Configuration Management (Requirement 9)
- **Requirement 9.1**: ✅ Configuration through environment variables and configuration files
- **Requirement 9.5**: ✅ Configuration validation at startup with descriptive error messages

### Request Processing (Requirement 6)
- **Requirement 6.1**: ✅ AI servers process requests and return responses within timeout
- **Requirement 6.2**: ✅ Server identification included in all responses
- **Requirement 6.3**: ✅ Request/response correlation ID tracking
- **Requirement 6.4**: ✅ Appropriate error codes with descriptive messages
- **Requirement 6.5**: ✅ Concurrent request handling without data corruption

## Server Architecture

### Server A
- **Port**: 8080 (local) / Dynamic (Render)
- **Identifier**: "Server A"
- **Documentation**: See `SERVER_A_README.md`
- **Test Script**: `test_server_a.py`

### Server B
- **Port**: 8081 (local) / Dynamic (Render)
- **Identifier**: "Server B"
- **Documentation**: See `SERVER_B_README.md`
- **Test Script**: `test_server_b.py`

### Load Balancer
- **Port**: 8000 (local) / Dynamic (Render)
- **Algorithm**: Round Robin
- **Health Monitoring**: Automatic
- **Metrics**: Comprehensive tracking

Both servers provide:
- Health check endpoint (`/health`)
- Server info endpoint (`/info`)
- AI processing endpoint (`/api/ai`)
- Request correlation tracking
- Comprehensive error handling
- Performance metrics collection

## Monitoring & Observability

- **Health Checks**: Automatic health monitoring every 30 seconds
- **Metrics Collection**: Request counts, response times, error rates
- **Server Identification**: Clear tracking of which server processes each request
- **Load Distribution**: Fair Round Robin distribution tracking
- **Error Handling**: Comprehensive error logging and reporting

## Next Steps

The project structure and core interfaces are now in place. The next tasks will implement:

1. ✅ AI Server instances with FastAPI
2. ✅ Load Balancer with Round Robin algorithm
3. 🔄 Health Monitoring system
4. 🔄 Auto Scaling controller
5. 🔄 Comprehensive testing and validation

## Production Considerations

### Scaling on Render
- Start with Starter plan for development
- Upgrade to Standard/Pro for production
- Monitor resource usage and costs
- Consider horizontal scaling

### Security
- HTTPS enabled by default on Render
- Add authentication middleware if needed
- Configure CORS for production
- Environment variable security

### Performance
- Connection pooling enabled
- Request timeout configuration
- Health check optimization
- Metrics-based scaling

## Support

- 📖 [Deployment Guide](RENDER_DEPLOYMENT.md)
- 🧪 [Testing Guide](test_render_deployment.py)
- 🔧 [Configuration Examples](render_config.json)
- 📊 [API Documentation](scalable_ai_api/)

For issues:
- Check Render logs in dashboard
- Run local tests first
- Verify environment variables
- Review deployment guide