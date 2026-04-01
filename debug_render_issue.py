#!/usr/bin/env python3
"""
Debug script to identify Render deployment issues.
"""

import sys
import os
import traceback

def test_imports():
    """Test all critical imports."""
    print("🔍 Testing imports...")
    
    try:
        import fastapi
        print(f"✅ FastAPI: {fastapi.__version__}")
    except Exception as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print(f"✅ Uvicorn: {uvicorn.__version__}")
    except Exception as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False
    
    try:
        from scalable_ai_api.load_balancer.render_app import app as lb_app
        print("✅ Load Balancer app imported successfully")
    except Exception as e:
        print(f"❌ Load Balancer app import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from scalable_ai_api.ai_server.render_app import app as ai_app
        print("✅ AI Server app imported successfully")
    except Exception as e:
        print(f"❌ AI Server app import failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_environment():
    """Test environment variables."""
    print("\n🔍 Testing environment...")
    
    port = os.environ.get("PORT", "Not set")
    print(f"PORT: {port}")
    
    server_id = os.environ.get("SERVER_ID", "Not set")
    print(f"SERVER_ID: {server_id}")
    
    pythonpath = os.environ.get("PYTHONPATH", "Not set")
    print(f"PYTHONPATH: {pythonpath}")
    
    return True

def test_app_creation():
    """Test app creation and basic functionality."""
    print("\n🔍 Testing app creation...")
    
    try:
        from scalable_ai_api.load_balancer.render_app import app as lb_app
        print(f"✅ Load Balancer app type: {type(lb_app)}")
        print(f"✅ Load Balancer routes: {len(lb_app.routes)}")
    except Exception as e:
        print(f"❌ Load Balancer app creation failed: {e}")
        return False
    
    try:
        from scalable_ai_api.ai_server.render_app import app as ai_app
        print(f"✅ AI Server app type: {type(ai_app)}")
        print(f"✅ AI Server routes: {len(ai_app.routes)}")
    except Exception as e:
        print(f"❌ AI Server app creation failed: {e}")
        return False
    
    return True

def main():
    """Main debug function."""
    print("🚀 Render Deployment Debug Script")
    print("=" * 50)
    
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    
    success = True
    success &= test_imports()
    success &= test_environment()
    success &= test_app_creation()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed! Deployment should work.")
    else:
        print("❌ Some tests failed. Check errors above.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())