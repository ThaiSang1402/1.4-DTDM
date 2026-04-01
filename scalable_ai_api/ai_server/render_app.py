"""
FastAPI application for AI Server on Render.

This module creates a FastAPI application that wraps the AI Server
functionality for deployment on Render.
"""

import os
from scalable_ai_api.ai_server.base_server import BaseAIServer

def create_app():
    """Create and configure the FastAPI application for AI Server."""
    # Get server configuration from environment
    SERVER_ID = os.environ.get("SERVER_ID", "AI Server")
    HOST = "0.0.0.0"
    PORT = int(os.environ.get("PORT", "8080"))
    
    # Create AI Server instance
    ai_server = BaseAIServer(
        server_id=SERVER_ID,
        host=HOST,
        port=PORT
    )
    
    return ai_server.app

# Export the FastAPI app for ASGI server
app = create_app()