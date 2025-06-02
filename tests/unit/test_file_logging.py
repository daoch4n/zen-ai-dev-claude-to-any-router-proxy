"""Tests for file logging configuration"""
import pytest
import tempfile
import shutil
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock
import structlog

from src.core.logging_config import configure_structlog


class TestFileLogging:
    """Test file logging configuration and functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.logs_dir = Path(self.temp_dir) / "test_logs"
        
        # Clear any existing logging configuration
        logging.getLogger().handlers.clear()
        structlog.reset_defaults()
    
    def teardown_method(self):
        """Cleanup after each test"""
        # Clear logging configuration
        logging.getLogger().handlers.clear()
        structlog.reset_defaults()
        
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_logs_directory_creation(self):
        """Test that logs directory is created automatically"""
        # Ensure directory doesn't exist
        assert not self.logs_dir.exists()
        
        # Configure logging with custom directory
        configure_structlog(
            development=True,
            logs_dir=str(self.logs_dir),
            log_rotation="daily",
            log_retention_days=7,
            enable_file_logging=True  # Explicitly enable for testing
        )
        
        # Directory should now exist
        assert self.logs_dir.exists()
        assert self.logs_dir.is_dir()
    
    def test_log_files_creation(self):
        """Test that log files are created with correct names"""
        configure_structlog(
            development=True,
            logs_dir=str(self.logs_dir),
            log_rotation="daily",
            log_retention_days=7,
            enable_file_logging=True  # Explicitly enable for testing
        )
        
        # Get a logger and log something
        import structlog
        logger = structlog.get_logger("test")
        logger.info("Test message")
        logger.error("Test error")
        
        # Check that log files exist
        app_log = self.logs_dir / "application.log"
        error_log = self.logs_dir / "errors.log"
        
        assert app_log.exists()
        assert error_log.exists()
    
    @pytest.mark.parametrize("rotation,expected_when", [
        ("daily", "midnight"),
        ("hourly", "H"),
        ("weekly", "W0"),
        ("invalid", "midnight")  # Should fallback to default
    ])
    def test_rotation_configuration(self, rotation, expected_when):
        """Test different rotation configurations"""
        with patch('src.core.logging_config.SafeTimedRotatingFileHandler') as mock_handler:
            mock_instance = MagicMock()
            mock_instance.level = logging.INFO  # Set proper log level
            mock_handler.return_value = mock_instance
            
            configure_structlog(
                development=True,
                logs_dir=str(self.logs_dir),
                log_rotation=rotation,
                log_retention_days=15,
                enable_file_logging=True  # Explicitly enable for testing
            )
            
            # Should be called twice (application.log and errors.log)
            assert mock_handler.call_count == 2
            
            # Check that the rotation settings are correct
            calls = mock_handler.call_args_list
            for call in calls:
                kwargs = call[1]
                assert kwargs['when'] == expected_when
                assert kwargs['interval'] == 1
                assert kwargs['backupCount'] == 15
                assert kwargs['encoding'] == 'utf-8'
    
    def test_retention_days_configuration(self):
        """Test that retention days are properly configured"""
        with patch('src.core.logging_config.SafeTimedRotatingFileHandler') as mock_handler:
            mock_instance = MagicMock()
            mock_instance.level = logging.INFO  # Set proper log level
            mock_handler.return_value = mock_instance
            
            retention_days = 45
            configure_structlog(
                development=True,
                logs_dir=str(self.logs_dir),
                log_retention_days=retention_days,
                enable_file_logging=True  # Explicitly enable for testing
            )
            
            # Verify backupCount is set correctly
            calls = mock_handler.call_args_list
            for call in calls:
                kwargs = call[1]
                assert kwargs['backupCount'] == retention_days
    
    def test_development_vs_production_formatting(self):
        """Test different log formatting for dev vs prod"""
        with patch('src.core.logging_config.SafeTimedRotatingFileHandler') as mock_handler:
            mock_instance = MagicMock()
            mock_instance.level = logging.INFO  # Set proper log level
            mock_handler.return_value = mock_instance
            
            # Test development formatting
            configure_structlog(
                development=True,
                json_logs=False,
                logs_dir=str(self.logs_dir),
                enable_file_logging=True
            )
            
            # Clear handlers and reset for second test
            logging.getLogger().handlers.clear()
            structlog.reset_defaults()
            
            # Test production formatting
            configure_structlog(
                development=False,
                json_logs=True,
                logs_dir=str(self.logs_dir),
                enable_file_logging=True
            )
            
            # Handler should be called for both configurations
            assert mock_handler.call_count >= 2
    
    def test_error_log_level_filtering(self):
        """Test that error log only captures ERROR and above"""
        configure_structlog(
            development=True,
            logs_dir=str(self.logs_dir),
            log_level="DEBUG",
            enable_file_logging=True
        )
        
        # Get the root logger to inspect handlers
        root_logger = logging.getLogger()
        
        # Find the error handler
        error_handler = None
        for handler in root_logger.handlers:
            if hasattr(handler, 'baseFilename') and 'errors.log' in str(handler.baseFilename):
                error_handler = handler
                break
        
        assert error_handler is not None
        assert error_handler.level == logging.ERROR
    
    def test_multiple_handlers_configuration(self):
        """Test that multiple handlers are configured correctly"""
        configure_structlog(
            development=True,
            logs_dir=str(self.logs_dir),
            log_level="INFO",
            enable_file_logging=True
        )
        
        root_logger = logging.getLogger()
        
        # Check for specific handler types by class name
        stream_handlers = []
        timed_rotating_handlers = []
        application_handlers = []
        error_handlers = []
        
        for handler in root_logger.handlers:
            handler_type = type(handler).__name__
            
            if handler_type == 'SafeStreamHandler':
                stream_handlers.append(handler)
            elif handler_type == 'SafeTimedRotatingFileHandler':
                timed_rotating_handlers.append(handler)
                # Check which file this handler is for
                if hasattr(handler, 'baseFilename'):
                    filename = str(handler.baseFilename)
                    if 'errors.log' in filename:
                        error_handlers.append(handler)
                    elif 'application.log' in filename:
                        application_handlers.append(handler)
        
        # We should have exactly one console handler (SafeStreamHandler)
        assert len(stream_handlers) == 1, f"Expected 1 SafeStreamHandler, got {len(stream_handlers)}"
        
        # We should have exactly two file handlers (SafeTimedRotatingFileHandler)
        assert len(timed_rotating_handlers) == 2, f"Expected 2 SafeTimedRotatingFileHandlers, got {len(timed_rotating_handlers)}"
        
        # We should have exactly one application file handler
        assert len(application_handlers) == 1, f"Expected 1 application file handler, got {len(application_handlers)}"
        
        # We should have exactly one error file handler
        assert len(error_handlers) == 1, f"Expected 1 error file handler, got {len(error_handlers)}"
        
        # Total should be 3 handlers
        assert len(root_logger.handlers) == 3, f"Expected 3 total handlers, got {len(root_logger.handlers)}"
    
    def test_nested_directory_creation(self):
        """Test that nested log directories are created"""
        nested_logs_dir = self.logs_dir / "nested" / "deep" / "logs"
        
        configure_structlog(
            development=True,
            logs_dir=str(nested_logs_dir),
            enable_file_logging=True
        )
        
        assert nested_logs_dir.exists()
        assert nested_logs_dir.is_dir()
    
    def test_log_level_propagation(self):
        """Test that log levels are properly set on all handlers"""
        configure_structlog(
            development=True,
            logs_dir=str(self.logs_dir),
            log_level="WARNING",
            enable_file_logging=True
        )
        
        root_logger = logging.getLogger()
        
        # Root logger should have WARNING level
        assert root_logger.level == logging.WARNING
        
        # Check each handler
        for handler in root_logger.handlers:
            if hasattr(handler, 'baseFilename') and 'errors.log' in str(handler.baseFilename):
                # Error handler should always be ERROR level
                assert handler.level == logging.ERROR
            else:
                # Other handlers should respect the configured level
                assert handler.level == logging.WARNING
    
    def test_unicode_log_encoding(self):
        """Test that log files are configured with UTF-8 encoding"""
        with patch('src.core.logging_config.SafeTimedRotatingFileHandler') as mock_handler:
            mock_instance = MagicMock()
            mock_instance.level = logging.INFO  # Set proper log level
            mock_handler.return_value = mock_instance
            
            configure_structlog(
                development=True,
                logs_dir=str(self.logs_dir),
                enable_file_logging=True
            )
            
            # Check that all handlers use UTF-8 encoding
            calls = mock_handler.call_args_list
            for call in calls:
                kwargs = call[1]
                assert kwargs['encoding'] == 'utf-8'
    
    def test_log_directory_permissions(self):
        """Test that log directory is created with proper permissions"""
        configure_structlog(
            development=True,
            logs_dir=str(self.logs_dir),
            enable_file_logging=True
        )
        
        # Directory should exist and be writable
        assert self.logs_dir.exists()
        assert self.logs_dir.is_dir()
        
        # Test we can create files in it
        test_file = self.logs_dir / "test.txt"
        test_file.write_text("test")
        assert test_file.exists()


class TestFileLoggingIntegration:
    """Integration tests for file logging with actual log output"""
    
    def setup_method(self):
        """Setup for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.logs_dir = Path(self.temp_dir) / "integration_logs"
    
    def teardown_method(self):
        """Cleanup after each test"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_actual_log_writing(self):
        """Test that logs are actually written to files"""
        configure_structlog(
            development=True,
            logs_dir=str(self.logs_dir),
            log_level="DEBUG",
            enable_file_logging=True
        )
        
        import structlog
        logger = structlog.get_logger("test.integration")
        
        # Write various log levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        # Force flush
        for handler in logging.getLogger().handlers:
            if hasattr(handler, 'flush'):
                handler.flush()
        
        # Check application log contains all messages
        app_log = self.logs_dir / "application.log"
        assert app_log.exists()
        
        app_content = app_log.read_text()
        assert "Debug message" in app_content
        assert "Info message" in app_content
        assert "Warning message" in app_content
        assert "Error message" in app_content
        
        # Check error log only contains error
        error_log = self.logs_dir / "errors.log"
        assert error_log.exists()
        
        error_content = error_log.read_text()
        assert "Debug message" not in error_content
        assert "Info message" not in error_content
        assert "Warning message" not in error_content
        assert "Error message" in error_content
    
    def test_structured_log_content(self):
        """Test that structured log content is properly formatted"""
        configure_structlog(
            development=False,  # Use JSON formatting
            json_logs=True,
            logs_dir=str(self.logs_dir),
            enable_file_logging=True
        )
        
        import structlog
        import json
        
        logger = structlog.get_logger("test.structured")
        logger.info("Structured message", user_id=123, action="test")
        
        # Force flush
        for handler in logging.getLogger().handlers:
            if hasattr(handler, 'flush'):
                handler.flush()
        
        app_log = self.logs_dir / "application.log"
        assert app_log.exists()
        
        content = app_log.read_text().strip()
        if content:
            # Should be valid JSON
            log_entry = json.loads(content)
            assert log_entry["event"] == "Structured message"
            assert log_entry["user_id"] == 123
            assert log_entry["action"] == "test"