"""
Attempt to get someone who owns a repo to let me get in and contribute
"""

from pathlib import Path
from datetime import date, timedelta, datetime
import json

from regex import template
from uritemplate import variables
from constants import OPENAI_MODEL
from github.package_managers import (
    get_npm_contact_information_from_npm_package,
    get_npm_package_info,
    get_pypi_contact_info,
)
from github.repo import (
    get_emails_from_commits,
    get_repository_info,
    get_top_contributors,
    github_email,
    parse_github_url,
)
from aijobs import parse_job_file, render_prompt

from pydantic_ai import Agent

from models import EmailMessage
from utils import pydantic_ai_model


def add_package_tools(agent):
    agent.tool_plain()(get_pypi_contact_info)
    agent.tool_plain()(get_npm_contact_information_from_npm_package)


def is_pull_request_link(github_link: str) -> bool:
    """
    Check if a GitHub link is a pull request link.

    Here's what they look like:

    https://github.com/plurals/pluralize/pull/206
    """
    return "/pull/" in github_link


def ask_for_help(
    github_url: str, extra_prompt: str | None = None
) -> list[EmailMessage]:
    """
    Reads a Markdown file (using parse_job_file) as the system prompt,
    fetches 2 months of work/personal calendar data, sends to OpenAI,
    and returns the JSON result.
    """

    metadata, job_description = parse_job_file("open source help")
    job_prompt = render_prompt(
        job_description, template_variables={"EMAIL_MESSAGE_SCHEMA": EmailMessage}
    )

    user_description = """
# Repository Information

```
{{REPO_INFO}}
```

# Discovered Emails

{{EMAILS}}
"""
    if extra_prompt:
        user_description += f"""
# Extra Instructions
{extra_prompt}
"""
    if is_pull_request_link(github_url):
        user_description += f"""
# Pull Request

{github_url}
        """

    # Pull Request Information
    # TODO I think we can set result_type here?
    agent = Agent(
        pydantic_ai_model(),
        system_prompt=job_prompt,
        result_type=list[EmailMessage],
    )
    add_package_tools(agent)

    github_user, github_repo = parse_github_url(github_url)

    owner_github_email = github_email(github_user)

    if not owner_github_email:
        # lets try to get it from the commits on the repo
        emails_from_commit = get_emails_from_commits(
            github_user, github_repo, github_user
        )

        owner_github_email = "\n".join(
            [contact.email for contact in emails_from_commit]
        )

    # TODO we can try top maintainers next

    user_prompt = render_prompt(
        user_description,
        {
            "REPO_INFO": get_repository_info(github_user, github_repo),
            "EMAILS": owner_github_email,
        },
    )

    result = agent.run_sync(user_prompt)

    # response = run_chat_completion(
    #     job_prompt=rendered_system_prompt,
    #     user_prompt=render_prompt(
    #         prompt,
    #         {
    #             "REPO_INFO": get_repository_info("whtsky", "pixelmatch-py"),
    #             "EMAILS": "whtsky@gmail.com",
    #         },
    #     ),
    #     temperature=0.7,
    # )

    return result.data

    # try:
    #     return json.loads(result.data)
    # except json.JSONDecodeError:
    #     raise ValueError(f"Failed to parse JSON: {result.data}")


if __name__ == "__main__":
    from gmail.utils import send_email
    import sys

    github_url = sys.argv[1]
    extra_prompt = sys.argv[2] if len(sys.argv) > 2 else None

    emails_to_send = ask_for_help(github_url, extra_prompt)

    for email_data in emails_to_send:
        send_email(email_data)

    breakpoint()
