"""CLI entry point for Gmail Intelligence Platform."""

import typer

app = typer.Typer(help="Gmail Intelligence Platform - Email extraction and analysis")


@app.command()
def setup():
    """Set up Gmail OAuth2 credentials."""
    typer.echo("Setting up Gmail authentication...")
    typer.echo("Not yet implemented")


@app.command()
def search(
    purpose: str = typer.Option(..., help="Purpose of the search"),
    output_format: str = typer.Option("json", help="Output format (json, csv, folder)"),
):
    """Search for emails with a specific purpose."""
    typer.echo(f"Searching for: {purpose}")
    typer.echo(f"Output format: {output_format}")
    typer.echo("Not yet implemented")


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
