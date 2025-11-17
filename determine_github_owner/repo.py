"""GitHub repository information retrieval."""

from urllib.request import Request, urlopen
import json
import typing as t
from structlog_config import configure_logger

from determine_github_owner.models import ContactInfo

log = configure_logger()


def get_github_token() -> str:
    """Get GitHub token from environment."""
    import os

    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        raise EnvironmentError("GITHUB_TOKEN is not set or is empty")
    return token


def _make_github_request(url: str) -> dict:
    """Make authenticated request to GitHub API."""
    token = get_github_token()
    headers = {"Authorization": f"token {token}"}
    request = Request(url, headers=headers)
    response = urlopen(request)
    return json.loads(response.read())


def get_top_contributors(owner: str, repo: str) -> str:
    """Get contributors who made at least 5% of total contributions."""
    url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
    contributors = _make_github_request(url)

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

    excluded_emails = ["@users.noreply.github.com", "snyk-bot@snyk.io"]

    for event in push_events:
        if event["actor"]["login"] != github_user:
            continue
        email_from_commit = event["payload"]["commits"][0]["author"]["email"]
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

    url = url_or_username.strip().replace("https://", "").replace("http://", "")

    if "/" not in url:
        return url, None

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
        - basic: Basic repository information (description, language, stars, etc)
        - readme: README content if available
        - topics: Repository topics/tags
    """
    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    repo_data = _make_github_request(repo_url)

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


def distinct_on(seq, key):
    """Get distinct items from sequence based on key function."""
    seen = set()
    seen_add = seen.add
    return [x for x in seq if key(x) not in seen and not seen_add(key(x))]


def get_emails_from_commits(
    owner: str, repo: str, username: str, limit: int = 10
) -> list[ContactInfo]:
    """Get a user's recent commits on a repository."""
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


def parse_email_from_commit(commit: dict) -> ContactInfo:
    """
    Extract contact information from a GitHub commit.

    Args:
        commit: GitHub commit object containing author information

    Returns:
        ContactInfo object with name and email from commit author
    """
    author = commit.get("commit", {}).get("author", {})

    email = author.get("email", "")

    if "@users.noreply.github.com" in email:
        return None

    return ContactInfo(name=author.get("name"), email=email)
