"""
* github user data
* event data to see if an email was included in a recent commit
"""

from urllib.request import Request, urlopen
import json
import os
import sys
import logging
from urllib.request import Request, urlopen
import json
import os
import sys
from decouple import config
from github.package_managers import ContactInfo
from utils import log
import typing as t

# Move token check to module level
GITHUB_TOKEN = config("GITHUB_TOKEN", default="", cast=str)
if not GITHUB_TOKEN:
    raise EnvironmentError("GITHUB_TOKEN is not set or is empty")


def _make_github_request(url: str) -> dict:
    """Make authenticated request to GitHub API."""
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    request = Request(url, headers=headers)
    response = urlopen(request)
    return json.loads(response.read())


def get_top_contributors(owner: str, repo: str) -> str:
    """Get contributors who made at least 5% of total contributions."""
    url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
    contributors = _make_github_request(url)

    # if a user did not contribute at least 5% of the total commits, they are not included
    contribution_minimum = 0.05

    total_commits = sum(c["contributions"] for c in contributors)
    top_contributors = [
        {
            "name": c["login"],
            "contributions": c["contributions"],
            "percent": int((c["contributions"] / total_commits) * 100),
        }
        for c in contributors
        if c["contributions"] >= total_commits * contribution_minimum
    ]

    log.info(
        "retrieved_contributors",
        total_contributors=len(contributors),
        top_contributor_count=len(top_contributors),
        repo=repo,
    )
    return json.dumps(top_contributors)


def github_email(github_user: str) -> str | None:
    """Get email for GitHub user from their profile."""
    log.info("getting_github_email", user=github_user)

    url = f"https://api.github.com/users/{github_user}"
    user_data = _make_github_request(url)
    email = user_data.get("email")

    if not email:
        log.warning("no_email_found_on_github", user=github_user)
        return None

    return email


def github_recent_commits(github_user: str) -> list[str]:
    """Get unique email addresses from user's recent commits."""
    url = f"https://api.github.com/users/{github_user}/events"
    events = _make_github_request(url)

    if not events:
        log.info("no_events_found", user=github_user)
        return []

    emails = []
    push_events = [event for event in events if event["type"] == "PushEvent"]

    # Emails to exclude
    excluded_emails = ["@users.noreply.github.com", "snyk-bot@snyk.io"]

    for event in push_events:
        if event["actor"]["login"] != github_user:
            continue
        email_from_commit = event["payload"]["commits"][0]["author"][
            "email"
        ]  # Filter out excluded emails
        if not any(excluded in email_from_commit for excluded in excluded_emails):
            emails.append(email_from_commit)

    log.info(
        "found_commit_emails", user=github_user, unique_email_count=len(set(emails))
    )
    return list(set(emails))


def parse_github_url(url_or_username: str) -> tuple[str, str | None]:
    """
    Parse a GitHub URL or username to extract owner and repo.
    Returns (owner, repo) tuple. repo is None if only username provided.

    Handles formats:
    - username
    - github.com/username
    - github.com/username/repo
    - github.com/username/repo/...
    """
    import re

    # Clean up URL if provided
    url = url_or_username.strip().replace("https://", "").replace("http://", "")

    # Handle just username format
    if "/" not in url:
        return url, None

    # Extract from github URL
    github_pattern = r"(?:github\.com/)?([^/]+)(?:/([^/#]+))?"
    match = re.search(github_pattern, url)

    if not match:
        raise ValueError(f"Could not parse GitHub URL: {url_or_username}")

    owner = match.group(1)
    repo = match.group(2)

    log.debug("parsed_github_url", owner=owner, repo=repo, original=url_or_username)
    return owner, repo


def get_repository_info(owner: str, repo: str) -> dict[str, t.Any]:
    """
    Get repository metadata and readme content.

    Returns:
        Dictionary containing:
        - basic: Basic rexpository information (description, language, stars, etc)
        - readme: README content if available
        - topics: Repository topics/tags
        - license: License information if available
    """
    # Get main repository information
    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    repo_data = _make_github_request(repo_url)

    # Get README content
    try:
        readme_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
        readme_data = _make_github_request(readme_url)
        import base64

        readme_content = base64.b64decode(readme_data.get("content", "")).decode(
            "utf-8"
        )
    except Exception as e:
        log.warning("failed_to_fetch_readme", owner=owner, repo=repo, error=str(e))
        readme_content = ""

    # Extract relevant information
    info = {
        "basic": {
            "name": repo_data.get("name"),
            "full_name": repo_data.get("full_name"),
            "description": repo_data.get("description"),
            "language": repo_data.get("language"),
            "stars": repo_data.get("stargazers_count"),
            "forks": repo_data.get("forks_count"),
            "open_issues": repo_data.get("open_issues_count"),
            "created_at": repo_data.get("created_at"),
            "updated_at": repo_data.get("updated_at"),
            "homepage": repo_data.get("homepage"),
        },
        "readme": readme_content,
        "topics": repo_data.get("topics", []),
    }

    log.info(
        "retrieved_repository_info",
        owner=owner,
        repo=repo,
        stars=info["basic"]["stars"],
        topics=len(info["topics"]),
        has_readme=bool(readme_content),
    )

    return info


# TODO upstream to funcy pipe
def distinct_on(seq, key):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if key(x) not in seen and not seen_add(key(x))]


def get_emails_from_commits(
    owner: str, repo: str, username: str, limit: int = 10
) -> list[ContactInfo]:
    """
    Get a user's recent commits on a repository.
    """

    commits = get_user_commits(owner, repo, username, limit)
    emails = [parse_email_from_commit(commit) for commit in commits]
    distinct_emails = distinct_on(emails, key=lambda x: x.email)

    return distinct_emails


def get_user_commits(
    owner: str, repo: str, username: str, limit: int = 10
) -> list[dict]:
    """
    Get a user's recent commits on a repository.

    Args:
        owner: Repository owner
        repo: Repository name
        username: GitHub username to filter commits by
        limit: Maximum number of commits to return (default: 10)

    Returns:
        List of commit data including sha, message, date, etc.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    params = {"author": username, "per_page": limit}

    # Add params to URL
    query_string = "&".join(f"{k}={v}" for k, v in params.items())
    full_url = f"{url}?{query_string}"

    commits = _make_github_request(full_url)
    log.info(
        "retrieved_user_commits",
        owner=owner,
        repo=repo,
        username=username,
        commit_count=len(commits),
    )

    return commits


from models import ContactInfo


def parse_email_from_commit(commit: dict) -> ContactInfo:
    """
    Extract contact information from a GitHub commit.

    Args:
        commit: GitHub commit object containing author information

    Returns:
        ContactInfo object with name and email from commit author

    Example commit author data:
        commit['commit']['author'] = {
            'name': 'Dror Speiser',
            'email': 'dror.mastershin@gmail.com',
            'date': '2017-10-18T17:11:01Z'
        }
    """
    author = commit.get("commit", {}).get("author", {})

    # Exclude noreply addresses
    email = author.get("email", "")

    if "@users.noreply.github.com" in email:
        return None

    return ContactInfo(name=author.get("name"), email=email)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: script.py <github_username_or_url>")
        sys.exit(1)

    input_value = sys.argv[1]
    owner, repo = parse_github_url(input_value)

    # If repo provided, show contributors
    if repo:
        print(f"\nRepository information for {owner}/{repo}:")
        repo_info = get_repository_info(owner, repo)
        print(json.dumps(repo_info, indent=2))
        print(get_top_contributors(owner, repo))

        # Get user's commits and most recent patch
        commits = get_user_commits(owner, repo, owner)
        if commits:
            latest_commit = commits[0]
            patch_data = get_commit_patch(owner, repo, latest_commit["sha"])
            print("\nLatest commit patch:")
            print(patch_data["patch"])

    github_user_email = github_email(owner)
    recent_commit_emails = github_recent_commits(owner)
    all_emails = list(set([github_user_email] + recent_commit_emails))
    print(f"\nEmails for {owner}:")
    [print(e) for e in all_emails]
