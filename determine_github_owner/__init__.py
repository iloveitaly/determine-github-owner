"""Determine GitHub repository owner contact information."""

import click
import json
from structlog_config import configure_logger

from determine_github_owner.repo import (
    parse_github_url,
    github_email,
    github_recent_commits,
    get_repository_info,
    get_top_contributors,
    get_emails_from_commits,
)
from determine_github_owner.package_managers import (
    get_pypi_contact_info,
    get_npm_contact_information_from_npm_package,
)

logger = configure_logger()


@click.group()
def cli():
    """Determine GitHub repository owner contact information."""
    pass


@cli.command()
@click.argument("github_url")
@click.option("--include-contributors", is_flag=True, help="Include top contributors")
def owner(github_url: str, include_contributors: bool):
    """Get owner contact information from GitHub URL or username."""
    github_user, github_repo = parse_github_url(github_url)

    owner_email = github_email(github_user)

    if not owner_email:
        logger.info("no email on profile, checking commits")
        recent_emails = github_recent_commits(github_user)
        if recent_emails:
            click.echo(f"Emails from recent commits for {github_user}:")
            for email in recent_emails:
                click.echo(f"  {email}")
        else:
            click.echo(f"No email found for {github_user}")
    else:
        click.echo(f"Email for {github_user}: {owner_email}")

    if github_repo:
        click.echo(f"\nRepository: {github_user}/{github_repo}")

        emails = get_emails_from_commits(github_user, github_repo, github_user)
        if emails:
            click.echo("Emails from repository commits:")
            for contact in emails:
                if contact:
                    click.echo(f"  {contact.name} <{contact.email}>")

        if include_contributors:
            contributors = get_top_contributors(github_user, github_repo)
            click.echo(f"\nTop contributors:\n{contributors}")


@cli.command()
@click.argument("github_url")
def repo(github_url: str):
    """Get repository information from GitHub URL."""
    github_user, github_repo = parse_github_url(github_url)

    if not github_repo:
        click.echo("Error: Please provide a full repository URL", err=True)
        raise click.Abort()

    repo_info = get_repository_info(github_user, github_repo)
    click.echo(json.dumps(repo_info, indent=2))


@cli.command()
@click.argument("package_name")
def pypi(package_name: str):
    """Get PyPI package author contact information."""
    info = get_pypi_contact_info(package_name)
    click.echo(f"Package: {info.package_name}")
    click.echo(f"Author: {info.author_name}")
    click.echo(f"Email: {info.author_email}")


@cli.command()
@click.argument("package_name")
def npm(package_name: str):
    """Get NPM package maintainer contact information."""
    contacts = get_npm_contact_information_from_npm_package(package_name)

    if not contacts:
        click.echo(f"No contacts found for {package_name}")
        return

    click.echo(f"Contacts for {package_name}:")
    for contact in contacts:
        click.echo(f"  {contact.email}")


def main():
    """Main entry point."""
    cli()
