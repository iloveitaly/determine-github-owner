"""Test CLI commands."""

from click.testing import CliRunner
from determine_github_owner import cli


def test_cli_help():
    """Test that CLI help works."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Discover owner contact information" in result.output


def test_cli_requires_full_url():
    """Test that CLI requires a full repository URL."""
    runner = CliRunner()
    result = runner.invoke(cli, ["iloveitaly"])
    assert result.exit_code == 1
    assert "Error: Please provide a full repository URL" in result.output
