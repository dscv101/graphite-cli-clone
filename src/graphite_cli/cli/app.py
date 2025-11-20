"""Main CLI application entry point."""


import typer

from graphite_cli import __version__

app = typer.Typer(
    name="gt",
    help="Graphite CLI - A Git workflow tool for PR stacking",
    add_completion=True,
    no_args_is_help=True,
)


@app.command()
def version() -> None:
    """Display version information."""
    typer.echo(f"Graphite CLI version {__version__}")


@app.callback(invoke_without_command=True)
def main_callback(
    _ctx: typer.Context,
    version_flag: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit.",
        is_flag=True,
    ),
) -> None:
    """Graphite CLI - A Git workflow tool for PR stacking."""
    if version_flag:
        typer.echo(f"Graphite CLI version {__version__}")
        raise typer.Exit


def main() -> None:
    """Entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main()
