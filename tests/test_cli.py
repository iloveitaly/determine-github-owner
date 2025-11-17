"""Test CLI commands."""

from click.testing import CliRunner
from determine_github_owner import cli


def test_cli_help():
    """Test that CLI help works."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Determine GitHub repository owner contact information" in result.output


def test_owner_command_help():
    """Test owner command help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["owner", "--help"])
    assert result.exit_code == 0
    assert "Get owner contact information" in result.output


def test_repo_command_help():
    """Test repo command help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["repo", "--help"])
    assert result.exit_code == 0
    assert "Get repository information" in result.output


def test_pypi_command_help():
    """Test pypi command help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["pypi", "--help"])
    assert result.exit_code == 0
    assert "Get PyPI package author contact information" in result.output


def test_npm_command_help():
    """Test npm command help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["npm", "--help"])
    assert result.exit_code == 0
    assert "Get NPM package maintainer contact information" in result.output
