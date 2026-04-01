# Deployment Guide: Scalable AI API System trên Render

## Tổng quan

Hướng dẫn này sẽ giúp bạn deploy hệ thống Scalable AI API lên Render cloud platform với 3 services:
- **Load Balancer**: Phân phối requests giữa các AI servers
- **Server A**: AI server instance đầu tiên
- **Server B**: AI server instance thứ hai

## Chuẩn bị

### 1. Repository Setup
Đảm bảo code của bạn đã được push lên GitHub repository với các files sau:
- `render.yaml` - Cấu hình Render services
- `Procfile` - Process definitions
- `runtime.txt` - Python version
- `requirements.txt` - Dependencies
- Toàn bộ source code trong `scalable_ai_api/`

### 2. Render Account
- Tạo account tại [render.com](https://render.com)
- Connect với GitHub repository của bạn

## Deployment Options

### Option 1: Sử dụng render.yaml (Recommended)

1. **Connect Repository**:
   - Vào Render Dashboard
   - Click "New" → "Blueprint"
   - Connect GitHub repository
   - Render sẽ tự động detect `render.yaml`

2. **Deploy Services**:
   - Render sẽ tạo 3 services tự động:
     - `scalable-ai-api-load-balancer`
     - `scalable-ai-api-server-a` 
     - `scalable-ai-api-server-b`

3. **Environment Variables** (tự động set từ render.yaml):
   ```
   LOAD_BALANCER_PORT=$PORT
   SERVER_A_URL=https://scalable-ai-api-server-a.onrender.com
   SERVER_B_URL=https://scalable-ai-api-server-b.onrender.com
   HEALTH_CHECK_INTERVAL=30
   REQUEST_TIMEOUT=30
   LOG_LEVEL=INFO
   ```

### Option 2: Manual Service Creation

#### 2.1 Deploy Server A
1. **Create Web Service**:
   - Service Name: `scalable-ai-api-server-a`
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python -m scalable_ai_api.ai_server.server_runner --server-id "Server A" --host 0.0.0.0 --port $PORT`

2. **Environment Variables**:
   ```
   SERVER_ID=Server A
   LOG_LEVEL=INFO
   ```

#### 2.2 Deploy Server B
1. **Create Web Service**:
   - Service Name: `scalable-ai-api-server-b`
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python -m scalable_ai_api.ai_server.server_runner --server-id "Server B" --host 0.0.0.0 --port $PORT`

2. **Environment Variables**:
   ```
   SERVER_ID=Server B
   LOG_LEVEL=INFO
   ```

#### 2.3 Deploy Load Balancer
1. **Create Web Service**:
   - Service Name: `scalable-ai-api-load-balancer`
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python -m scalable_ai_api.main --component load_balancer --port $PORT`

2. **Environment Variables**:
   ```
   LOAD_BALANCER_PORT=$PORT
   SERVER_A_URL=https://scalable-ai-api-server-a.onrender.com
   SERVER_B_URL=https://scalable-ai-api-server-b.onrender.com
   HEALTH_CHECK_INTERVAL=30
   REQUEST_TIMEOUT=30
   LOG_LEVEL=INFO
   ```

## URLs sau khi Deploy

Sau khi deploy thành công, bạn sẽ có các URLs:

- **Load Balancer**: `https://scalable-ai-api-load-balancer.onrender.com`
- **Server A**: `https://scalable-ai-api-server-a.onrender.com`
- **Server B**: `https://scalable-ai-api-server-b.onrender.com`

## Testing Deployment

### 1. Health Checks
```bash
# Test Load Balancer
curl https://scalable-ai-api-load-balancer.onrender.com/health

# Test Server A
curl https://scalable-ai-api-server-a.onrender.com/health

# Test Server B
curl https://scalable-ai-api-server-b.onrender.com/health
```

### 2. AI Request Testing
```bash
# Test qua Load Balancer (Round Robin)
curl -X POST https://scalable-ai-api-load-balancer.onrender.com/api/ai \
  -H "Content-Type: application/json" \
  -H "X-Correlation-ID: test-123" \
  -d '{
    "prompt": "Hello AI! Please identify yourself.",
    "parameters": {"temperature": 0.7},
    "client_id": "test_client"
  }'

# Test trực tiếp Server A
curl -X POST https://scalable-ai-api-server-a.onrender.com/api/ai \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hello Server A!",
    "client_id": "test_client"
  }'

# Test trực tiếp Server B
curl -X POST https://scalable-ai-api-server-b.onrender.com/api/ai \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hello Server B!",
    "client_id": "test_client"
  }'
```

### 3. Load Balancer Status
```bash
curl https://scalable-ai-api-load-balancer.onrender.com/status
```

## Monitoring và Logs

### 1. Render Dashboard
- Vào Render Dashboard để xem logs real-time
- Monitor resource usage và performance
- Check deployment status

### 2. Application Logs
Các logs sẽ hiển thị:
- Request routing information
- Server health status
- Round Robin distribution
- Error handling

### 3. Health Monitoring
- Load Balancer tự động monitor health của Server A và B
- Unhealthy servers sẽ được exclude khỏi routing
- Health checks chạy mỗi 30 giây

## Troubleshooting

### Common Issues

1. **Service không start**:
   - Check logs trong Render Dashboard
   - Verify environment variables
   - Check Python version trong runtime.txt

2. **Load Balancer không connect được servers**:
   - Verify SERVER_A_URL và SERVER_B_URL
   - Check server health endpoints
   - Ensure servers đã deploy thành công

3. **Requests timeout**:
   - Increase REQUEST_TIMEOUT environment variable
   - Check server response times
   - Monitor resource usage

### Debug Commands

```bash
# Check service status
curl https://your-service.onrender.com/

# Check health
curl https://your-service.onrender.com/health

# Check load balancer metrics
curl https://scalable-ai-api-load-balancer.onrender.com/status
```

## Production Considerations

### 1. Scaling
- Render Starter plan: Suitable cho development/testing
- Upgrade to Standard/Pro plans cho production workloads
- Consider horizontal scaling với multiple instances

### 2. Security
- Add authentication middleware nếu cần
- Configure CORS properly cho production
- Use HTTPS (Render provides SSL certificates tự động)

### 3. Performance
- Monitor response times và error rates
- Optimize AI processing logic
- Consider caching strategies

### 4. Cost Optimization
- Render Starter plan: Free tier với limitations
- Monitor usage để avoid unexpected charges
- Consider sleep/wake patterns cho development

## Next Steps

Sau khi deploy thành công:

1. **Implement remaining features**:
   - Health Monitoring System (Task 5)
   - Auto Scaling Controller (Task 7)
   - Comprehensive monitoring (Task 6)

2. **Add production features**:
   - Authentication/Authorization
   - Rate limiting
   - Advanced monitoring
   - Database integration

3. **Performance optimization**:
   - Caching layer
   - Connection pooling
   - Resource optimization

## Support

Nếu gặp vấn đề:
- Check Render documentation: https://render.com/docs
- Review application logs trong Render Dashboard
- Test locally trước khi deploy
- Verify all environment variables