"""Determine GitHub repository owner contact information using AI."""

import click
import json
from structlog_config import configure_logger
from pydantic_ai import Agent

from determine_github_owner.repo import (
    parse_github_url,
    github_email,
    get_repository_info,
    get_emails_from_commits,
)
from determine_github_owner.package_managers import (
    get_pypi_contact_info,
    get_npm_contact_information_from_npm_package,
)

logger = configure_logger()

SYSTEM_PROMPT = """You are an expert at discovering contact information for GitHub repository owners and maintainers.

Your goal is to find the best way to contact the owner or maintainer of a GitHub repository.

You have access to tools that can:
- Get PyPI package author information (use if the repo contains a Python package)
- Get NPM package maintainer information (use if the repo contains an NPM package)

Based on the repository information and discovered emails provided by the user, determine:
1. The best email(s) to contact
2. The name of the person/people to contact
3. Any additional context about the repository or owner

Return a JSON object with:
- "emails": list of email addresses (strings)
- "names": list of names (strings)
- "notes": any relevant notes about the repository or how to contact the owner

If you find package information through the tools, include those emails in your response."""


@click.command()
@click.argument("github_url")
@click.option("--model", default="openai:gpt-4o", help="AI model to use (e.g., openai:gpt-4o, anthropic:claude-3-5-sonnet-20241022)")
def cli(github_url: str, model: str):
    """Discover owner contact information for a GitHub repository using AI."""
    github_user, github_repo = parse_github_url(github_url)

    if not github_repo:
        click.echo("Error: Please provide a full repository URL", err=True)
        raise click.Abort()

    logger.info("discovering_owner", repo=f"{github_user}/{github_repo}")

    owner_github_email = github_email(github_user)
    repo_info = get_repository_info(github_user, github_repo)

    if not owner_github_email:
        logger.info("no email on profile, checking commits")
        emails_from_commits = get_emails_from_commits(github_user, github_repo, github_user)
        owner_github_email = "\n".join(
            [f"{contact.name} <{contact.email}>" for contact in emails_from_commits if contact]
        )

    user_prompt = f"""# Repository Information

```json
{json.dumps(repo_info, indent=2)}
```

# Discovered Emails

{owner_github_email or "No emails found in profile or commits"}

# Repository URL

{github_url}

Please analyze this repository and use available tools to discover the best way to contact the owner or maintainer."""

    agent = Agent(
        model,
        system_prompt=SYSTEM_PROMPT,
    )

    agent.tool_plain()(get_pypi_contact_info)
    agent.tool_plain()(get_npm_contact_information_from_npm_package)

    result = agent.run_sync(user_prompt)

    click.echo("\n" + "="*60)
    click.echo("OWNER DISCOVERY RESULTS")
    click.echo("="*60)
    click.echo(result.data)


def main():
    """Main entry point."""
    cli()
