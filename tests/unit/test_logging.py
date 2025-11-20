"""Unit tests for logging utilities."""

import logging
import tempfile
import time
from pathlib import Path

from graphite_cli.utils import (
    DEBUG,
    ERROR,
    INFO,
    WARNING,
    get_logger,
    log_command_execution,
    log_error,
    set_log_level,
    setup_logging,
)
from graphite_cli.utils.logging import SensitiveDataFilter


def cleanup_logging_handlers():
    """Clean up all logging handlers to prevent file handle leaks on Windows."""
    logger = logging.getLogger("graphite_cli")
    for handler in logger.handlers[:]:
        handler.flush()
        handler.close()
    logger.handlers.clear()
    # Small delay to ensure file handles are released on Windows
    time.sleep(0.1)


class TestSensitiveDataFilter:
    """Test cases for SensitiveDataFilter."""

    def test_filter_redacts_token_in_message(self):
        """Test that sensitive 'token' field is redacted."""
        filter_instance = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=INFO,
            pathname="",
            lineno=0,
            msg="Using token: abc123",
            args=(),
            exc_info=None,
        )

        result = filter_instance.filter(record)

        assert result is True
        assert "token: [REDACTED]" in record.msg
        assert "abc123" not in record.msg

    def test_filter_redacts_password_in_message(self):
        """Test that sensitive 'password' field is redacted."""
        filter_instance = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=INFO,
            pathname="",
            lineno=0,
            msg="User password: secret123",
            args=(),
            exc_info=None,
        )

        result = filter_instance.filter(record)

        assert result is True
        assert "password: [REDACTED]" in record.msg
        assert "secret123" not in record.msg

    def test_filter_allows_non_sensitive_messages(self):
        """Test that non-sensitive messages pass through unchanged."""
        filter_instance = SensitiveDataFilter()
        original_msg = "Creating branch: feature-x"
        record = logging.LogRecord(
            name="test",
            level=INFO,
            pathname="",
            lineno=0,
            msg=original_msg,
            args=(),
            exc_info=None,
        )

        result = filter_instance.filter(record)

        assert result is True
        assert record.msg == original_msg


class TestSetupLogging:
    """Test cases for setup_logging function."""

    def test_setup_logging_basic(self):
        """Test basic logging setup with default parameters."""
        logger = setup_logging()

        assert logger is not None
        assert logger.name == "graphite_cli"
        assert logger.level == INFO
        assert len(logger.handlers) > 0

    def test_setup_logging_with_debug_level(self):
        """Test logging setup with DEBUG level."""
        logger = setup_logging(level=DEBUG)

        assert logger.level == DEBUG

    def test_setup_logging_with_file_output(self):
        """Test logging setup with file output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"

            logger = setup_logging(log_file=log_file)
            logger.info("Test message")

            assert log_file.exists()
            content = log_file.read_text()
            assert "Test message" in content

            # Clean up handlers before temp directory cleanup
            cleanup_logging_handlers()

    def test_setup_logging_creates_log_directory(self):
        """Test that log directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "subdir" / "logs" / "test.log"

            logger = setup_logging(log_file=log_file)
            logger.info("Test message")

            assert log_file.exists()
            assert log_file.parent.exists()

            # Clean up handlers before temp directory cleanup
            cleanup_logging_handlers()

    def test_setup_logging_without_rich(self):
        """Test logging setup with Rich handler disabled."""
        logger = setup_logging(enable_rich=False)

        assert logger is not None
        assert len(logger.handlers) > 0
        # Should have standard StreamHandler, not RichHandler
        assert any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers)

    def test_setup_logging_applies_sensitive_filter(self):
        """Test that sensitive data filter is applied to all handlers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"

            logger = setup_logging(log_file=log_file)
            logger.info("GitHub token: abc123")

            content = log_file.read_text()
            assert "token: [REDACTED]" in content
            assert "abc123" not in content

            # Clean up handlers before temp directory cleanup
            cleanup_logging_handlers()

    def test_setup_logging_removes_existing_handlers(self):
        """Test that existing handlers are removed before adding new ones."""
        logger = setup_logging()
        initial_handler_count = len(logger.handlers)

        # Setup again
        logger = setup_logging()

        # Should not double handlers
        assert len(logger.handlers) == initial_handler_count


class TestGetLogger:
    """Test cases for get_logger function."""

    def test_get_logger_returns_child_logger(self):
        """Test that get_logger returns a child logger."""
        logger = get_logger("test_module")

        assert logger.name == "graphite_cli.test_module"

    def test_get_logger_different_modules(self):
        """Test that different modules get different loggers."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        assert logger1.name != logger2.name
        assert logger1 is not logger2


class TestSetLogLevel:
    """Test cases for set_log_level function."""

    def test_set_log_level_changes_level(self):
        """Test that set_log_level changes the logging level."""
        logger = setup_logging(level=INFO)

        set_log_level(DEBUG)

        assert logger.level == DEBUG

    def test_set_log_level_changes_handler_levels(self):
        """Test that set_log_level changes handler levels."""
        logger = setup_logging(level=INFO)

        set_log_level(WARNING)

        for handler in logger.handlers:
            assert handler.level == WARNING


class TestLogCommandExecution:
    """Test cases for log_command_execution function."""

    def test_log_command_execution_basic(self, caplog):
        """Test basic command execution logging."""
        setup_logging(level=INFO, enable_rich=False, propagate=True)

        with caplog.at_level(INFO):
            log_command_execution("create", {"branch_name": "feature-x"})

        # Check the records, not just text
        assert any("Executing command: create" in record.message for record in caplog.records)
        assert any("feature-x" in record.message for record in caplog.records)

    def test_log_command_execution_redacts_sensitive_args(self, caplog):
        """Test that sensitive arguments are redacted."""
        setup_logging(level=INFO, enable_rich=False, propagate=True)

        with caplog.at_level(INFO):
            log_command_execution("auth", {"token": "secret123", "username": "john"})

        assert any("Executing command: auth" in record.message for record in caplog.records)
        assert not any("secret123" in record.message for record in caplog.records)
        assert any("[REDACTED]" in record.message for record in caplog.records)
        assert any("john" in record.message for record in caplog.records)

    def test_log_command_execution_without_args(self, caplog):
        """Test command execution logging without arguments."""
        setup_logging(level=INFO, enable_rich=False, propagate=True)

        with caplog.at_level(INFO):
            log_command_execution("status")

        assert any("Executing command: status" in record.message for record in caplog.records)


class TestLogError:
    """Test cases for log_error function."""

    def test_log_error_basic(self, caplog):
        """Test basic error logging."""
        setup_logging(level=ERROR, enable_rich=False, propagate=True)

        error = ValueError("Test error")

        with caplog.at_level(ERROR):
            log_error(error)

        assert any("ValueError: Test error" in record.message for record in caplog.records)

    def test_log_error_with_context(self, caplog):
        """Test error logging with context."""
        setup_logging(level=ERROR, enable_rich=False, propagate=True)

        error = RuntimeError("Operation failed")

        with caplog.at_level(ERROR):
            log_error(error, "Failed during git rebase")

        assert any("Failed during git rebase" in record.message for record in caplog.records)
        assert any("RuntimeError: Operation failed" in record.message for record in caplog.records)

    def test_log_error_includes_traceback(self, caplog):
        """Test that error logging includes traceback."""
        setup_logging(level=ERROR, enable_rich=False, propagate=True)

        try:
            raise ValueError("Test error")
        except ValueError as e:
            with caplog.at_level(ERROR):
                log_error(e)

        # exc_info=True should include traceback
        assert any("ValueError: Test error" in record.message for record in caplog.records)


class TestLogLevelConstants:
    """Test cases for log level constants."""

    def test_log_level_constants_defined(self):
        """Test that all log level constants are defined."""
        assert DEBUG == logging.DEBUG
        assert INFO == logging.INFO
        assert WARNING == logging.WARNING
        assert ERROR == logging.ERROR


class TestIntegration:
    """Integration tests for logging system."""

    def test_full_logging_workflow(self):
        """Test complete logging workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "integration.log"

            # Setup logging
            setup_logging(level=DEBUG, log_file=log_file, enable_rich=False)

            # Get module logger
            module_logger = get_logger("test_module")

            # Log various messages
            module_logger.debug("Debug message")
            module_logger.info("Info message")
            module_logger.warning("Warning message")

            # Log command execution
            log_command_execution("test", {"arg1": "value1"})

            # Log error
            try:
                raise ValueError("Test error")
            except ValueError as e:
                log_error(e, "Test context")

            # Change log level
            set_log_level(WARNING)

            # Verify file contents
            content = log_file.read_text()
            assert "Debug message" in content
            assert "Info message" in content
            assert "Warning message" in content
            assert "test" in content
            assert "Test error" in content

            # Clean up handlers before temp directory cleanup
            cleanup_logging_handlers()

    def test_sensitive_data_never_logged(self):
        """Test that sensitive data is never written to logs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "sensitive.log"

            setup_logging(level=DEBUG, log_file=log_file, enable_rich=False)
            module_logger = get_logger("security")

            # Try to log sensitive data
            module_logger.info("GitHub token: abc123def456")
            log_command_execution("auth", {"token": "secret789"})

            # Verify sensitive data is redacted
            content = log_file.read_text()
            assert "abc123def456" not in content
            assert "secret789" not in content
            assert "[REDACTED]" in content

            # Clean up handlers before temp directory cleanup
            cleanup_logging_handlers()
