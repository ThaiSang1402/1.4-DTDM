# Procfile for Render deployment
# This file defines how to run different components

# Load Balancer (default web process)
web: uvicorn scalable_ai_api.load_balancer.render_app:app --host 0.0.0.0 --port $PORT

# Alternative commands for different services:
# AI Server: uvicorn scalable_ai_api.ai_server.render_app:app --host 0.0.0.0 --port $PORT