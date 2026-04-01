# Dockerfile for Load Balancer on Render
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment
ENV PYTHONPATH=/app
ENV PORT=8000

# Expose port
EXPOSE $PORT

# Start Load Balancer
CMD uvicorn scalable_ai_api.load_balancer.render_app:app --host 0.0.0.0 --port $PORT