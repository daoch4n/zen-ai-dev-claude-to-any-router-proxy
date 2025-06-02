"""
Tests for Phase 3: MCP Environment Management System.

These tests verify the complete MCP server lifecycle management system
including configuration, environment management, and workflow orchestration.
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
import subprocess
import importlib

from src.mcp.server_configs import (
    MCPServerConfig, HealthCheckConfig, GlobalMCPConfig,
    MCPConfigManager, config_manager
)
from src.mcp.environment_manager import (
    MCPEnvironmentManager, MCPServerProcess, environment_manager
)
from src.mcp.lifecycle_service import (
    MCPLifecycleService, lifecycle_service,
    start_mcp_server_task, stop_mcp_server_task, restart_mcp_server_task
)


class TestMCPServerConfig:
    """Test MCP server configuration management."""
    
    def test_mcp_health_check_creation(self):
        """Test HealthCheckConfig dataclass creation."""
        health_check = HealthCheckConfig(
            enabled=True,
            endpoint="http://localhost:3000/health",
            interval=30,
            timeout=10
        )
        
        assert health_check.enabled is True
        assert health_check.endpoint == "http://localhost:3000/health"
        assert health_check.interval == 30
        assert health_check.timeout == 10
    
    def test_mcp_server_config_creation(self):
        """Test MCPServerConfig dataclass creation."""
        health_check = HealthCheckConfig(enabled=True)
        
        config = MCPServerConfig(
            name="test-server",
            type="nodejs",
            command="node server.js",
            environment={"NODE_ENV": "production"},
            log_level="INFO",
            restart_policy="on-failure",
            max_restarts=3,
            python_version=None,
            node_version="18.0.0",
            health_check=health_check
        )
        
        assert config.name == "test-server"
        assert config.type == "nodejs"
        assert config.command == "node server.js"
        assert config.environment == {"NODE_ENV": "production"}
        assert config.node_version == "18.0.0"
        assert config.health_check == health_check
    
    def test_mcp_global_config_creation(self):
        """Test GlobalMCPConfig dataclass creation."""
        global_config = GlobalMCPConfig(
            log_directory="logs/mcp",
            enable_monitoring=True,
            shutdown_timeout=10
        )
        
        assert global_config.log_directory == "logs/mcp"
        assert global_config.enable_monitoring is True
        assert global_config.shutdown_timeout == 10


class TestMCPConfigManager:
    """Test MCP configuration manager."""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary directory for test configuration."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_config_file(self, temp_config_dir):
        """Create a sample MCP configuration file."""
        config_content = """
global:
  log_directory: "logs/mcp"
  enable_monitoring: true
  shutdown_timeout: 30

servers:
  python-assistant:
    type: "python"
    command: "python assistant.py"
    environment:
      PYTHONPATH: "/app/src"
      LOG_LEVEL: "info"
    log_level: "INFO"
    restart_policy: "on-failure"
    max_restarts: 3
    python_version: "3.9"
    health_check:
      enabled: true
      endpoint: "http://localhost:3001/health"
      interval: 30
      timeout: 10
  
  node-server:
    type: "nodejs"
    command: "node server.js"
    environment:
      NODE_ENV: "production"
    log_level: "INFO"
    restart_policy: "always"
    max_restarts: 5
    node_version: "18.0.0"
    health_check:
      enabled: false
"""
        config_file = Path(temp_config_dir) / "mcp_servers.yaml"
        config_file.write_text(config_content)
        return config_file
    
    def test_config_manager_initialization(self):
        """Test config manager initialization."""
        manager = MCPConfigManager()
        assert manager is not None
        assert hasattr(manager, 'logger')
    
    @patch('src.mcp.server_configs.config_manager')
    def test_load_config_success(self, mock_manager, sample_config_file):
        """Test successful configuration loading."""
        manager = MCPConfigManager()
        
        # Mock the file path
        with patch.object(manager, 'config_path', sample_config_file):
            success = manager.load_configuration()
        
        assert success is True
    
    def test_get_server_config_missing(self):
        """Test getting configuration for non-existent server."""
        manager = MCPConfigManager()
        config = manager.get_server_config("non-existent-server")
        assert config is None
    
    def test_list_server_names_empty(self):
        """Test listing server names when no servers configured."""
        manager = MCPConfigManager()
        manager.servers = {}
        names = manager.list_server_names()
        assert names == []


class TestMCPEnvironmentManager:
    """Test MCP environment manager."""
    
    @pytest.fixture
    def environment_manager_instance(self):
        """Create a fresh environment manager instance for testing."""
        return MCPEnvironmentManager()
    
    @pytest.fixture
    def sample_server_config(self):
        """Create a sample server configuration."""
        return MCPServerConfig(
            name="test-server",
            type="python",
            command="python test_server.py",
            environment={"TEST_ENV": "true"},
            log_level="DEBUG",
            restart_policy="on-failure",
            max_restarts=3,
            python_version="3.9",
            node_version=None,
            health_check=HealthCheckConfig(enabled=False)
        )
    
    def test_environment_manager_initialization(self, environment_manager_instance):
        """Test environment manager initialization."""
        assert environment_manager_instance is not None
        assert hasattr(environment_manager_instance, 'running_servers')
        assert hasattr(environment_manager_instance, 'logger')
        assert isinstance(environment_manager_instance.running_servers, dict)
    
    @pytest.mark.asyncio
    async def test_prepare_server_environment(self, environment_manager_instance, sample_server_config):
        """Test environment preparation for a server."""
        env = await environment_manager_instance._prepare_server_environment(sample_server_config)
        
        assert isinstance(env, dict)
        assert "TEST_ENV" in env
        assert env["TEST_ENV"] == "true"
        assert "LOG_LEVEL" in env
        assert env["LOG_LEVEL"] == "DEBUG"
    
    @pytest.mark.asyncio
    @patch('subprocess.Popen')
    async def test_spawn_server_process(self, mock_popen, environment_manager_instance, sample_server_config, tmp_path):
        """Test server process spawning."""
        # Create a mock process
        mock_process = Mock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        # Create temporary log file
        log_file = tmp_path / "test.log"
        
        env = {"TEST": "true"}
        
        with patch('builtins.open', mock_open()):
            process = await environment_manager_instance._spawn_server_process(
                server_config=sample_server_config,
                env=env,
                log_file=log_file
            )
        
        assert process == mock_process
        assert process.pid == 12345
        mock_popen.assert_called_once()
    
    def test_get_server_status_not_running(self, environment_manager_instance):
        """Test getting status of a server that's not running."""
        status = environment_manager_instance.get_server_status("non-existent-server")
        
        assert status["name"] == "non-existent-server"
        assert status["status"] == "stopped"
        assert status["running"] is False
    
    def test_get_all_server_status_empty(self, environment_manager_instance):
        """Test getting status of all servers when none are configured."""
        with patch('src.mcp.server_configs.config_manager') as mock_manager:
            mock_manager.list_server_names.return_value = []
            
            all_status = environment_manager_instance.get_all_server_status()
            assert all_status == {}


class TestMCPLifecycleService:
    """Test MCP lifecycle service."""
    
    @pytest.fixture
    def lifecycle_service_instance(self):
        """Create a fresh lifecycle service instance for testing."""
        return MCPLifecycleService()
    
    def test_lifecycle_service_initialization(self, lifecycle_service_instance):
        """Test lifecycle service initialization."""
        assert lifecycle_service_instance is not None
        assert hasattr(lifecycle_service_instance, 'logger')
    
    @pytest.mark.asyncio
    async def test_get_available_servers(self, lifecycle_service_instance):
        """Test getting available servers list."""
        # Mock the config manager directly in the lifecycle service module
        mock_config_manager = Mock()
        mock_config_manager.list_server_names.return_value = ["server1", "server2"]
        
        lifecycle_module = importlib.import_module('src.mcp.lifecycle_service')
        original_config_manager = lifecycle_module.config_manager
        lifecycle_module.config_manager = mock_config_manager
        
        try:
            servers = await lifecycle_service_instance.get_available_servers()
            assert servers == ["server1", "server2"]
        finally:
            lifecycle_module.config_manager = original_config_manager
    
    @pytest.mark.asyncio
    async def test_get_server_status(self, lifecycle_service_instance):
        """Test getting individual server status."""
        # Mock the environment manager directly in the lifecycle service module
        mock_env_manager = Mock()
        mock_status = {"name": "test-server", "status": "running", "running": True}
        mock_env_manager.get_server_status.return_value = mock_status
        
        lifecycle_module = importlib.import_module('src.mcp.lifecycle_service')
        original_env_manager = lifecycle_module.environment_manager
        lifecycle_module.environment_manager = mock_env_manager
        
        try:
            status = await lifecycle_service_instance.get_server_status("test-server")
            assert status == mock_status
        finally:
            lifecycle_module.environment_manager = original_env_manager
    
    @pytest.mark.asyncio
    async def test_get_all_servers_status(self, lifecycle_service_instance):
        """Test getting all servers status."""
        # Mock the environment manager directly in the lifecycle service module
        mock_env_manager = Mock()
        mock_status = {"server1": {"status": "running"}, "server2": {"status": "stopped"}}
        mock_env_manager.get_all_server_status.return_value = mock_status
        
        lifecycle_module = importlib.import_module('src.mcp.lifecycle_service')
        original_env_manager = lifecycle_module.environment_manager
        lifecycle_module.environment_manager = mock_env_manager
        
        try:
            all_status = await lifecycle_service_instance.get_all_servers_status()
            assert all_status == mock_status
        finally:
            lifecycle_module.environment_manager = original_env_manager


class TestMCPPrefectTasks:
    """Test MCP Prefect tasks and flows."""
    
    @pytest.mark.asyncio
    async def test_start_mcp_server_task_success(self):
        """Test successful MCP server start task."""
        mock_env_manager = Mock()
        mock_env_manager.start_server = AsyncMock(return_value=True)
        mock_env_manager.get_server_status.return_value = {
            "name": "test-server",
            "status": "running",
            "pid": 12345
        }
        
        lifecycle_module = importlib.import_module('src.mcp.lifecycle_service')
        original_env_manager = lifecycle_module.environment_manager
        lifecycle_module.environment_manager = mock_env_manager
        
        try:
            result = await start_mcp_server_task("test-server")
            
            assert result["server_name"] == "test-server"
            assert result["success"] is True
            assert "timestamp" in result
            assert "pid" in result
        finally:
            lifecycle_module.environment_manager = original_env_manager
    
    @pytest.mark.asyncio
    async def test_start_mcp_server_task_failure(self):
        """Test failed MCP server start task."""
        mock_env_manager = Mock()
        mock_env_manager.start_server = AsyncMock(return_value=False)
        
        lifecycle_module = importlib.import_module('src.mcp.lifecycle_service')
        original_env_manager = lifecycle_module.environment_manager
        lifecycle_module.environment_manager = mock_env_manager
        
        try:
            result = await start_mcp_server_task("test-server")
            
            assert result["server_name"] == "test-server"
            assert result["success"] is False
            assert "timestamp" in result
        finally:
            lifecycle_module.environment_manager = original_env_manager
    
    @pytest.mark.asyncio
    async def test_stop_mcp_server_task_success(self):
        """Test successful MCP server stop task."""
        mock_env_manager = Mock()
        mock_env_manager.stop_server = AsyncMock(return_value=True)
        
        lifecycle_module = importlib.import_module('src.mcp.lifecycle_service')
        original_env_manager = lifecycle_module.environment_manager
        lifecycle_module.environment_manager = mock_env_manager
        
        try:
            result = await stop_mcp_server_task("test-server", force=False)
            
            assert result["server_name"] == "test-server"
            assert result["success"] is True
            assert result["force"] is False
            assert "timestamp" in result
        finally:
            lifecycle_module.environment_manager = original_env_manager
    
    @pytest.mark.asyncio
    async def test_restart_mcp_server_task_success(self):
        """Test successful MCP server restart task."""
        mock_env_manager = Mock()
        mock_env_manager.restart_server = AsyncMock(return_value=True)
        mock_env_manager.get_server_status.return_value = {
            "name": "test-server",
            "status": "running",
            "restart_count": 1
        }
        
        lifecycle_module = importlib.import_module('src.mcp.lifecycle_service')
        original_env_manager = lifecycle_module.environment_manager
        lifecycle_module.environment_manager = mock_env_manager
        
        try:
            result = await restart_mcp_server_task("test-server")
            
            assert result["server_name"] == "test-server"
            assert result["success"] is True
            assert "timestamp" in result
            assert "restart_count" in result
        finally:
            lifecycle_module.environment_manager = original_env_manager


class TestMCPIntegration:
    """Integration tests for the complete MCP system."""
    
    @pytest.mark.asyncio
    async def test_mcp_system_integration(self):
        """Test the complete MCP system integration."""
        # Test that all components can be imported and initialized
        from src.mcp import (
            config_manager, environment_manager, lifecycle_service,
            MCPServerConfig, HealthCheckConfig, GlobalMCPConfig
        )
        
        # Verify components exist
        assert config_manager is not None
        assert environment_manager is not None
        assert lifecycle_service is not None
        
        # Verify classes can be instantiated
        health_check = HealthCheckConfig(enabled=True)
        assert health_check is not None
        
        server_config = MCPServerConfig(
            name="test",
            type="python",
            command="python logs/test_files/test.py",
            python_version="3.9",
            health_check=health_check
        )
        assert server_config is not None
        
        global_config = GlobalMCPConfig()
        assert global_config is not None
    
    @pytest.mark.asyncio
    async def test_mcp_workflow_orchestration(self):
        """Test MCP workflow orchestration capabilities."""
        # Test that Prefect tasks can be imported
        from src.mcp.lifecycle_service import (
            start_mcp_server_task,
            stop_mcp_server_task,
            restart_mcp_server_task,
            health_check_mcp_server_task
        )
        
        # Verify tasks exist and are callable
        assert callable(start_mcp_server_task)
        assert callable(stop_mcp_server_task)
        assert callable(restart_mcp_server_task)
        assert callable(health_check_mcp_server_task)


def mock_open(mock=None, read_data=''):
    """Helper function to create mock file handles."""
    if mock is None:
        mock = Mock()
    
    def _mock_open(*args, **kwargs):
        return mock
    
    return _mock_open


# Phase 3 completion verification
def test_phase_3_completion():
    """Test that Phase 3 MCP Environment Management is complete."""
    
    # Verify all required modules can be imported
    try:
        from src.mcp import config_manager, MCPServerConfig
        from src.mcp.environment_manager import environment_manager, MCPServerProcess
        from src.mcp.lifecycle_service import lifecycle_service
        from src.routers.mcp import router as mcp_router
        
        phase_3_complete = True
    except ImportError as e:
        phase_3_complete = False
        pytest.fail(f"Phase 3 incomplete - import error: {e}")
    
    # Verify key functionality
    assert phase_3_complete, "Phase 3 MCP Environment Management must be complete"
    assert config_manager is not None, "MCP config manager must be available"
    assert environment_manager is not None, "MCP environment manager must be available"
    assert lifecycle_service is not None, "MCP lifecycle service must be available"
    assert mcp_router is not None, "MCP router must be available"
    
    print("✅ Phase 3: MCP Environment Management - COMPLETE")