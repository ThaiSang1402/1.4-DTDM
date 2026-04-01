#!/usr/bin/env python3
"""
Render Docker Compatibility Validator

This script validates that the Docker configuration is compatible with Render platform.
"""

import os
import sys
import yaml
import subprocess
from pathlib import Path


def validate_render_yaml():
    """Validate render.yaml configuration."""
    print("🔍 Validating render.yaml...")
    
    if not os.path.exists("render.yaml"):
        print("❌ render.yaml not found")
        return False
    
    try:
        with open("render.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        services = config.get("services", [])
        if not services:
            print("❌ No services defined in render.yaml")
            return False
        
        print(f"✅ Found {len(services)} services in render.yaml")
        
        for service in services:
            name = service.get("name", "unknown")
            runtime = service.get("runtime")
            dockerfile_path = service.get("dockerfilePath")
            
            if runtime != "docker":
                print(f"❌ Service {name}: runtime should be 'docker', got '{runtime}'")
                return False
            
            if not dockerfile_path:
                print(f"❌ Service {name}: missing dockerfilePath")
                return False
            
            if not os.path.exists(dockerfile_path.lstrip("./")):
                print(f"❌ Service {name}: Dockerfile not found at {dockerfile_path}")
                return False
            
            print(f"✅ Service {name}: Docker configuration valid")
        
        return True
        
    except Exception as e:
        print(f"❌ Error parsing render.yaml: {e}")
        return False


def validate_dockerfiles():
    """Validate Dockerfile configurations."""
    print("\n🔍 Validating Dockerfiles...")
    
    dockerfiles = ["Dockerfile", "Dockerfile.aiserver"]
    
    for dockerfile in dockerfiles:
        if not os.path.exists(dockerfile):
            print(f"❌ {dockerfile} not found")
            return False
        
        print(f"📋 Checking {dockerfile}...")
        
        with open(dockerfile, "r") as f:
            content = f.read()
        
        # Check for Render compatibility
        checks = [
            ("FROM python:3.11-slim", "Uses compatible Python base image"),
            ("WORKDIR /app", "Sets working directory"),
            ("COPY requirements.txt", "Copies requirements first for caching"),
            ("pip install", "Installs Python dependencies"),
            ("COPY . .", "Copies application code"),
            ("ENV PYTHONPATH=/app", "Sets Python path"),
            ("CMD", "Has startup command"),
        ]
        
        for check, description in checks:
            if check in content:
                print(f"  ✅ {description}")
            else:
                print(f"  ❌ Missing: {description}")
                return False
        
        # Check for Render-specific issues
        if "ENV PORT=" in content:
            print(f"  ⚠️  Warning: Hardcoded PORT env var (Render will override)")
        
        if "EXPOSE $PORT" in content:
            print(f"  ⚠️  Warning: Using variable in EXPOSE (use static port)")
        
        if "uvicorn" in content and "--port $PORT" not in content and "--port ${PORT" not in content:
            print(f"  ❌ uvicorn command should use $PORT variable")
            return False
        
        print(f"✅ {dockerfile} is Render compatible")
    
    return True


def validate_requirements():
    """Validate requirements.txt."""
    print("\n🔍 Validating requirements.txt...")
    
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found")
        return False
    
    with open("requirements.txt", "r") as f:
        requirements = f.read()
    
    essential_packages = [
        "fastapi",
        "uvicorn",
        "requests",
        "httpx",
        "psutil",
        "pyyaml",
    ]
    
    for package in essential_packages:
        if package in requirements:
            print(f"  ✅ {package} found")
        else:
            print(f"  ❌ {package} missing")
            return False
    
    # Check for unnecessary packages that slow down builds
    unnecessary_packages = [
        "pytest",
        "hypothesis",
        "prometheus_client",
    ]
    
    for package in unnecessary_packages:
        if package in requirements:
            print(f"  ⚠️  {package} found (consider removing for faster builds)")
    
    print("✅ requirements.txt is valid")
    return True


def validate_app_imports():
    """Validate that app modules can be imported."""
    print("\n🔍 Validating app imports...")
    
    imports_to_test = [
        ("scalable_ai_api.load_balancer.render_app", "Load Balancer app"),
        ("scalable_ai_api.ai_server.render_app", "AI Server app"),
        ("scalable_ai_api.models", "Data models"),
        ("scalable_ai_api.interfaces", "Interfaces"),
    ]
    
    for module, description in imports_to_test:
        try:
            __import__(module)
            print(f"  ✅ {description} import successful")
        except ImportError as e:
            print(f"  ❌ {description} import failed: {e}")
            return False
    
    return True


def validate_dockerignore():
    """Validate .dockerignore configuration."""
    print("\n🔍 Validating .dockerignore...")
    
    if not os.path.exists(".dockerignore"):
        print("⚠️  .dockerignore not found (recommended for smaller builds)")
        return True
    
    with open(".dockerignore", "r") as f:
        dockerignore = f.read()
    
    recommended_ignores = [
        ".git",
        "__pycache__",
        "*.pyc",
        ".pytest_cache",
        "tests/",
        "demo_*.py",
        "validate_*.py",
    ]
    
    for ignore in recommended_ignores:
        if ignore in dockerignore:
            print(f"  ✅ {ignore} ignored")
        else:
            print(f"  ⚠️  Consider ignoring {ignore}")
    
    print("✅ .dockerignore configuration checked")
    return True


def validate_render_specific():
    """Validate Render-specific requirements."""
    print("\n🔍 Validating Render-specific requirements...")
    
    # Check that apps handle PORT environment variable
    render_apps = [
        "scalable_ai_api/load_balancer/render_app.py",
        "scalable_ai_api/ai_server/render_app.py"
    ]
    
    for app_file in render_apps:
        if os.path.exists(app_file):
            with open(app_file, "r") as f:
                content = f.read()
            
            if "create_app" in content or "app =" in content:
                print(f"  ✅ {app_file} has ASGI app export")
            else:
                print(f"  ❌ {app_file} missing ASGI app export")
                return False
        else:
            print(f"  ❌ {app_file} not found")
            return False
    
    print("✅ Render-specific requirements validated")
    return True


def main():
    """Run all validation checks."""
    print("🚀 Render Docker Compatibility Validator")
    print("=" * 50)
    
    checks = [
        validate_render_yaml,
        validate_dockerfiles,
        validate_requirements,
        validate_app_imports,
        validate_dockerignore,
        validate_render_specific,
    ]
    
    all_passed = True
    
    for check in checks:
        try:
            if not check():
                all_passed = False
        except Exception as e:
            print(f"❌ Check failed with error: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 All checks passed! Docker configuration is Render compatible.")
        print("\n📋 Next steps:")
        print("1. Push code to GitHub")
        print("2. Connect repository to Render")
        print("3. Render will auto-detect render.yaml and deploy")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())