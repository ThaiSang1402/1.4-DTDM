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

# Render will set PORT automatically
EXPOSE 8000

# Start Load Balancer (Render will override PORT)
CMD ["sh", "-c", "uvicorn scalable_ai_api.load_balancer.render_app:app --host 0.0.0.0 --port ${PORT:-8000}"]