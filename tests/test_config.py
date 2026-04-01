"""Tests for configuration management system."""

import os
import tempfile
import pytest
from pathlib import Path

from scalable_ai_api.config.manager import ConfigurationManager, ConfigurationError
from scalable_ai_api.models import SystemConfiguration, ScalingPolicy


class TestConfigurationManager:
    """Test cases for ConfigurationManager."""
    
    def test_load_default_configuration(self):
        """Test loading default configuration."""
        manager = ConfigurationManager()
        config = manager.load_configuration()
        
        assert isinstance(config, SystemConfiguration)
        assert config.load_balancer_port == 8000
        assert config.health_check_interval == 30
        assert config.health_check_timeout == 5
        assert config.scaling_policy.min_instances == 2
        assert config.scaling_policy.max_instances == 10
    
    def test_load_configuration_from_yaml_file(self):
        """Test loading configuration from YAML file."""
        config_content = """
        load_balancer_port: 9000
        health_check_interval: 60
        scaling_policy:
          min_instances: 3
          max_instances: 15
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            config_file = f.name
        
        try:
            manager = ConfigurationManager(config_file)
            config = manager.load_configuration()
            
            assert config.load_balancer_port == 9000
            assert config.health_check_interval == 60
            assert config.scaling_policy.min_instances == 3
            assert config.scaling_policy.max_instances == 15
        finally:
            os.unlink(config_file)
    
    def test_load_configuration_from_environment(self):
        """Test loading configuration from environment variables."""
        # Set environment variables
        os.environ["LOAD_BALANCER_PORT"] = "7000"
        os.environ["MIN_INSTANCES"] = "4"
        os.environ["MAX_INSTANCES"] = "20"
        
        try:
            manager = ConfigurationManager()
            config = manager.load_configuration()
            
            assert config.load_balancer_port == 7000
            assert config.scaling_policy.min_instances == 4
            assert config.scaling_policy.max_instances == 20
        finally:
            # Clean up environment variables
            for key in ["LOAD_BALANCER_PORT", "MIN_INSTANCES", "MAX_INSTANCES"]:
                os.environ.pop(key, None)
    
    def test_environment_overrides_file_config(self):
        """Test that environment variables override file configuration."""
        config_content = """
        load_balancer_port: 9000
        health_check_interval: 60
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            config_file = f.name
        
        # Set environment variable that should override file config
        os.environ["LOAD_BALANCER_PORT"] = "7000"
        
        try:
            manager = ConfigurationManager(config_file)
            config = manager.load_configuration()
            
            # Environment should override file
            assert config.load_balancer_port == 7000
            # File config should still be used for non-overridden values
            assert config.health_check_interval == 60
        finally:
            os.unlink(config_file)
            os.environ.pop("LOAD_BALANCER_PORT", None)
    
    def test_invalid_configuration_raises_error(self):
        """Test that invalid configuration raises ConfigurationError."""
        config_content = """
        load_balancer_port: -1  # Invalid port
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            config_file = f.name
        
        try:
            manager = ConfigurationManager(config_file)
            with pytest.raises(ConfigurationError):
                manager.load_configuration()
        finally:
            os.unlink(config_file)
    
    def test_invalid_scaling_thresholds_raises_error(self):
        """Test that invalid scaling thresholds raise ConfigurationError."""
        config_content = """
        scaling_policy:
          scale_up_threshold: 30.0
          scale_down_threshold: 80.0  # Invalid: down > up
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            config_file = f.name
        
        try:
            manager = ConfigurationManager(config_file)
            with pytest.raises(ConfigurationError):
                manager.load_configuration()
        finally:
            os.unlink(config_file)
    
    def test_get_configuration_before_load_raises_error(self):
        """Test that getting configuration before loading raises error."""
        manager = ConfigurationManager()
        
        with pytest.raises(ConfigurationError):
            manager.get_configuration()
    
    def test_nonexistent_config_file_ignored(self):
        """Test that nonexistent config file is ignored gracefully."""
        manager = ConfigurationManager("nonexistent_file.yaml")
        config = manager.load_configuration()
        
        # Should load default configuration
        assert config.load_balancer_port == 8000
    
    def test_malformed_json_raises_error(self):
        """Test that malformed JSON config file raises error."""
        config_content = '{"load_balancer_port": 8000'  # Missing closing brace
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(config_content)
            config_file = f.name
        
        try:
            manager = ConfigurationManager(config_file)
            with pytest.raises(ConfigurationError):
                manager.load_configuration()
        finally:
            os.unlink(config_file)


class TestSystemConfiguration:
    """Test cases for SystemConfiguration model validation."""
    
    def test_valid_configuration_creation(self):
        """Test creating valid SystemConfiguration."""
        config = SystemConfiguration(
            load_balancer_port=8080,
            health_check_interval=45,
            health_check_timeout=10
        )
        
        assert config.load_balancer_port == 8080
        assert config.health_check_interval == 45
        assert config.health_check_timeout == 10
    
    def test_invalid_port_raises_error(self):
        """Test that invalid port raises ValueError."""
        with pytest.raises(ValueError):
            SystemConfiguration(load_balancer_port=70000)  # Port too high
        
        with pytest.raises(ValueError):
            SystemConfiguration(load_balancer_port=0)  # Port too low
    
    def test_invalid_intervals_raise_error(self):
        """Test that invalid intervals raise ValueError."""
        with pytest.raises(ValueError):
            SystemConfiguration(health_check_interval=-1)
        
        with pytest.raises(ValueError):
            SystemConfiguration(health_check_timeout=0)


class TestScalingPolicy:
    """Test cases for ScalingPolicy model validation."""
    
    def test_valid_scaling_policy_creation(self):
        """Test creating valid ScalingPolicy."""
        policy = ScalingPolicy(
            min_instances=3,
            max_instances=15,
            scale_up_threshold=85.0,
            scale_down_threshold=25.0
        )
        
        assert policy.min_instances == 3
        assert policy.max_instances == 15
        assert policy.scale_up_threshold == 85.0
        assert policy.scale_down_threshold == 25.0
    
    def test_invalid_instance_counts_raise_error(self):
        """Test that invalid instance counts raise ValueError."""
        with pytest.raises(ValueError):
            ScalingPolicy(min_instances=0)  # Too low
        
        with pytest.raises(ValueError):
            ScalingPolicy(min_instances=5, max_instances=3)  # Max < min
    
    def test_invalid_thresholds_raise_error(self):
        """Test that invalid thresholds raise ValueError."""
        with pytest.raises(ValueError):
            ScalingPolicy(
                scale_up_threshold=30.0,
                scale_down_threshold=80.0  # Down > up
            )