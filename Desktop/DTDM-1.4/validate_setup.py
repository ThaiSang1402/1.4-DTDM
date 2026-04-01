#!/usr/bin/env python3
"""
Validation script for the Scalable AI API System setup.

This script validates that the project structure and configuration system
are working correctly.
"""

import sys
from pathlib import Path

from scalable_ai_api.config.manager import load_system_configuration, ConfigurationError
from scalable_ai_api.models import SystemConfiguration


def validate_project_structure():
    """Validate that all required directories and files exist."""
    print("🔍 Validating project structure...")
    
    required_paths = [
        "scalable_ai_api/__init__.py",
        "scalable_ai_api/interfaces.py",
        "scalable_ai_api/models.py",
        "scalable_ai_api/config/manager.py",
        "scalable_ai_api/load_balancer/__init__.py",
        "scalable_ai_api/ai_server/__init__.py",
        "scalable_ai_api/monitoring/__init__.py",
        "scalable_ai_api/auto_scaling/__init__.py",
        "tests/test_config.py",
        "requirements.txt",
        "config.yaml",
        ".env.example"
    ]
    
    missing_paths = []
    for path in required_paths:
        if not Path(path).exists():
            missing_paths.append(path)
    
    if missing_paths:
        print(f"❌ Missing required files/directories:")
        for path in missing_paths:
            print(f"   - {path}")
        return False
    
    print("✅ Project structure is complete")
    return True


def validate_configuration_system():
    """Validate that the configuration system works correctly."""
    print("\n🔍 Validating configuration system...")
    
    try:
        # Test loading default configuration
        config = load_system_configuration()
        print(f"✅ Default configuration loaded successfully")
        print(f"   - Load balancer port: {config.load_balancer_port}")
        print(f"   - Health check interval: {config.health_check_interval}s")
        print(f"   - Min instances: {config.scaling_policy.min_instances}")
        print(f"   - Max instances: {config.scaling_policy.max_instances}")
        
        # Test loading from config file
        config_file = load_system_configuration("config.yaml")
        print(f"✅ Configuration file loaded successfully")
        
        # Validate configuration object
        assert isinstance(config, SystemConfiguration)
        assert config.load_balancer_port > 0
        assert config.health_check_interval > 0
        assert config.scaling_policy.min_instances >= 1
        assert config.scaling_policy.max_instances >= config.scaling_policy.min_instances
        
        return True
        
    except ConfigurationError as e:
        print(f"❌ Configuration error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def validate_data_models():
    """Validate that data models work correctly."""
    print("\n🔍 Validating data models...")
    
    try:
        from scalable_ai_api.models import (
            ServerInstance, AIRequest, AIResponse, 
            HealthStatus, LoadBalancerMetrics, ScalingPolicy
        )
        
        # Test ServerInstance creation
        server = ServerInstance(
            id="test-server",
            ip_address="192.168.1.10",
            port=8080
        )
        print(f"✅ ServerInstance created: {server.id}")
        
        # Test AIRequest creation
        request = AIRequest(
            client_id="test-client",
            prompt="Test prompt"
        )
        print(f"✅ AIRequest created: {request.request_id}")
        
        # Test ScalingPolicy validation
        policy = ScalingPolicy(
            min_instances=2,
            max_instances=10,
            scale_up_threshold=80.0,
            scale_down_threshold=30.0
        )
        print(f"✅ ScalingPolicy created with valid thresholds")
        
        return True
        
    except Exception as e:
        print(f"❌ Data model error: {e}")
        return False


def main():
    """Run all validation checks."""
    print("🚀 Scalable AI API System - Setup Validation")
    print("=" * 50)
    
    checks = [
        validate_project_structure,
        validate_configuration_system,
        validate_data_models
    ]
    
    results = []
    for check in checks:
        results.append(check())
    
    print("\n" + "=" * 50)
    if all(results):
        print("🎉 All validation checks passed!")
        print("✅ Project setup is complete and ready for development")
        return 0
    else:
        print("❌ Some validation checks failed")
        print("🔧 Please fix the issues above before proceeding")
        return 1


if __name__ == "__main__":
    sys.exit(main())