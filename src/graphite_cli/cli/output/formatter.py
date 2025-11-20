"""Output formatting utilities using Rich library.

This module provides the Formatter class for formatting command output
using the Rich library for beautiful terminal displays.
"""

from enum import Enum
from typing import Any

from rich.console import Console
from rich.text import Text


class MessageType(Enum):
    """Message type enumeration for formatting."""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class Formatter:
    """Formatter for terminal output using Rich library.

    This class provides methods for formatting various types of output
    including success/error messages, lists, key-value pairs, and titles.

    Attributes:
        console: The Rich Console instance for output.
    """

    def __init__(self, console: Console | None = None) -> None:
        """Initialize the Formatter.

        Args:
            console: Optional Rich Console instance. If not provided,
                a new Console instance will be created.
        """
        self.console = console if console is not None else Console()

    def success(self, message: str) -> None:
        """Print a success message with formatting.

        Args:
            message: The success message to display.
        """
        self.message(message, MessageType.SUCCESS)

    def error(self, message: str) -> None:
        """Print an error message with formatting.

        Args:
            message: The error message to display.
        """
        self.message(message, MessageType.ERROR)

    def warning(self, message: str) -> None:
        """Print a warning message with formatting.

        Args:
            message: The warning message to display.
        """
        self.message(message, MessageType.WARNING)

    def info(self, message: str) -> None:
        """Print an info message with formatting.

        Args:
            message: The info message to display.
        """
        self.message(message, MessageType.INFO)

    def message(self, message: str, message_type: MessageType) -> None:
        """Print a message with type-specific formatting.

        Args:
            message: The message to display.
            message_type: The type of message (success, error, warning, info).
        """
        # Define symbols and colors for each message type
        type_config = {
            MessageType.SUCCESS: ("✓", "green"),
            MessageType.ERROR: ("✗", "red"),
            MessageType.WARNING: ("⚠", "yellow"),
            MessageType.INFO: ("i", "blue"),
        }

        symbol, color = type_config[message_type]

        # Create formatted text with symbol and color
        formatted_message = Text()
        formatted_message.append(f"{symbol} ", style=f"bold {color}")
        formatted_message.append(message)

        self.console.print(formatted_message)

    def format_list(
        self,
        items: list[str],
        title: str | None = None,
        bullet: str = "•",
    ) -> None:
        """Format and print a list of items.

        Args:
            items: List of items to display.
            title: Optional title for the list.
            bullet: Bullet character to use (default: "•").
        """
        if title:
            self.console.print(f"[bold]{title}[/bold]")

        for item in items:
            self.console.print(f"  {bullet} {item}")

    def format_key_value(
        self,
        data: dict[str, Any],
        title: str | None = None,
    ) -> None:
        """Format and print key-value pairs.

        Args:
            data: Dictionary of key-value pairs to display.
            title: Optional title for the key-value display.
        """
        if title:
            self.console.print(f"[bold]{title}[/bold]")

        for key, value in data.items():
            self.console.print(f"  [cyan]{key}:[/cyan] {value}")

    def print_separator(self, char: str = "─", length: int | None = None) -> None:
        """Print a separator line.

        Args:
            char: Character to use for the separator (default: "─").
            length: Length of the separator. If None, uses console width.
        """
        if length is None:
            length = self.console.width

        self.console.print(char * length)

    def print_blank_line(self) -> None:
        """Print a blank line."""
        self.console.print()

    def format_title(self, title: str) -> None:
        """Format and print a title.

        Args:
            title: The title to display.
        """
        self.console.print(f"[bold blue]{title}[/bold blue]")

    def format_subtitle(self, subtitle: str) -> None:
        """Format and print a subtitle.

        Args:
            subtitle: The subtitle to display.
        """
        self.console.print(f"[bold]{subtitle}[/bold]")
