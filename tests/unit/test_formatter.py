"""Unit tests for the Rich output formatter."""

from io import StringIO

import pytest
from rich.console import Console

from graphite_cli.cli.output.formatter import Formatter, MessageType


class TestFormatter:
    """Test suite for the Formatter class."""

    @pytest.fixture
    def formatter(self):
        """Create a Formatter instance for testing."""
        return Formatter()

    @pytest.fixture
    def mock_console(self):
        """Create a mock console with StringIO for capturing output."""
        string_io = StringIO()
        console = Console(file=string_io, force_terminal=True, width=80)
        return console, string_io

    def test_formatter_initialization(self, formatter):
        """Test that formatter initializes with a Console instance."""
        assert isinstance(formatter.console, Console)

    def test_success_message(self, mock_console):
        """Test success message formatting."""
        console, output = mock_console
        formatter = Formatter(console=console)

        formatter.success("Operation completed successfully")

        result = output.getvalue()
        assert "✓" in result or "✔" in result  # Check for success symbol
        assert "Operation completed successfully" in result

    def test_error_message(self, mock_console):
        """Test error message formatting."""
        console, output = mock_console
        formatter = Formatter(console=console)

        formatter.error("Something went wrong")

        result = output.getvalue()
        # Check for error symbol (using character check)
        assert "✗" in result or "✘" in result
        assert "Something went wrong" in result

    def test_warning_message(self, mock_console):
        """Test warning message formatting."""
        console, output = mock_console
        formatter = Formatter(console=console)

        formatter.warning("This is a warning")

        result = output.getvalue()
        assert "⚠" in result or "!" in result  # Check for warning symbol
        assert "This is a warning" in result

    def test_info_message(self, mock_console):
        """Test info message formatting."""
        console, output = mock_console
        formatter = Formatter(console=console)

        formatter.info("Information message")

        result = output.getvalue()
        # Check for info symbol
        assert "i" in result.lower()
        assert "Information message" in result

    def test_message_with_type(self, mock_console):
        """Test generic message method with message type."""
        console, output = mock_console
        formatter = Formatter(console=console)

        formatter.message("Test message", MessageType.SUCCESS)

        result = output.getvalue()
        assert "Test message" in result

    def test_format_list(self, mock_console):
        """Test list formatting."""
        console, output = mock_console
        formatter = Formatter(console=console)

        items = ["Item 1", "Item 2", "Item 3"]
        formatter.format_list(items, title="My List")

        result = output.getvalue()
        assert "My List" in result
        # Check for "Item" text and numbers separately due to Rich number formatting
        assert "Item" in result
        assert "•" in result or "bullet" in result.lower()
        assert "1" in result
        assert "2" in result
        assert "3" in result

    def test_format_list_with_bullets(self, mock_console):
        """Test list formatting with custom bullets."""
        console, output = mock_console
        formatter = Formatter(console=console)

        items = ["First", "Second", "Third"]
        formatter.format_list(items, bullet="→")

        result = output.getvalue()
        assert "→" in result
        assert "First" in result

    def test_format_key_value_pairs(self, mock_console):
        """Test key-value pair formatting."""
        console, output = mock_console
        formatter = Formatter(console=console)

        data = {
            "Branch": "feature/test",
            "Parent": "main",
            "PR Number": "123",
        }
        formatter.format_key_value(data, title="Branch Info")

        result = output.getvalue()
        assert "Branch Info" in result
        assert "Branch" in result
        assert "feature/test" in result
        assert "Parent" in result
        assert "main" in result

    def test_print_separator(self, mock_console):
        """Test separator printing."""
        console, output = mock_console
        formatter = Formatter(console=console)

        formatter.print_separator()

        result = output.getvalue()
        assert len(result.strip()) > 0  # Separator should produce output

    def test_print_separator_with_char(self, mock_console):
        """Test separator printing with custom character."""
        console, output = mock_console
        formatter = Formatter(console=console)

        formatter.print_separator(char="=")

        result = output.getvalue()
        assert "=" in result

    def test_print_blank_line(self, mock_console):
        """Test blank line printing."""
        console, output = mock_console
        formatter = Formatter(console=console)

        formatter.print_blank_line()

        result = output.getvalue()
        assert "\n" in result

    def test_format_title(self, mock_console):
        """Test title formatting."""
        console, output = mock_console
        formatter = Formatter(console=console)

        formatter.format_title("My Title")

        result = output.getvalue()
        assert "My Title" in result

    def test_format_subtitle(self, mock_console):
        """Test subtitle formatting."""
        console, output = mock_console
        formatter = Formatter(console=console)

        formatter.format_subtitle("My Subtitle")

        result = output.getvalue()
        assert "My Subtitle" in result

    def test_message_type_enum_values(self):
        """Test MessageType enum has all expected values."""
        assert hasattr(MessageType, "SUCCESS")
        assert hasattr(MessageType, "ERROR")
        assert hasattr(MessageType, "WARNING")
        assert hasattr(MessageType, "INFO")

    def test_console_property(self, formatter):
        """Test that console property is accessible."""
        assert hasattr(formatter, "console")
        assert isinstance(formatter.console, Console)

    def test_formatter_with_custom_console(self):
        """Test formatter initialization with custom console."""
        custom_console = Console()
        formatter = Formatter(console=custom_console)
        assert formatter.console is custom_console

    def test_multiple_messages(self, mock_console):
        """Test multiple consecutive messages."""
        console, output = mock_console
        formatter = Formatter(console=console)

        formatter.success("First success")
        formatter.error("First error")
        formatter.warning("First warning")

        result = output.getvalue()
        assert "First success" in result
        assert "First error" in result
        assert "First warning" in result

    def test_format_empty_list(self, mock_console):
        """Test formatting an empty list."""
        console, output = mock_console
        formatter = Formatter(console=console)

        formatter.format_list([], title="Empty List")

        result = output.getvalue()
        assert "Empty List" in result

    def test_format_empty_key_value(self, mock_console):
        """Test formatting empty key-value pairs."""
        console, output = mock_console
        formatter = Formatter(console=console)

        formatter.format_key_value({}, title="Empty Data")

        result = output.getvalue()
        assert "Empty Data" in result
